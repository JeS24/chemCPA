import json
import os
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import seml
import torch
from sacred import Experiment

from compert.data import load_dataset_splits
from compert.embedding import get_chemical_representation
from compert.model import ComPert
from compert.profiling import Profiler
from compert.train import custom_collate, evaluate, evaluate_r2

ex = Experiment()
seml.setup_logger(ex)


@ex.post_run_hook
def collect_stats(_run):
    seml.collect_exp_stats(_run)


@ex.config
def config():
    overwrite = None
    db_collection = None
    if db_collection is not None:
        ex.observers.append(
            seml.create_mongodb_observer(db_collection, overwrite=overwrite)
        )


profiler = None


@ex.pre_run_hook(prefix="profiling")
def init_profiler(run_profiler: bool, outdir: str):
    if run_profiler:
        if not Path(outdir).exists():
            Path(outdir).mkdir(parents=True)
        global profiler
        profiler = Profiler(
            str(seml.utils.make_hash(ex.current_run.config)),
            outdir,
        )
        profiler.start()


@ex.post_run_hook
def stop_profiler():
    if profiler:
        profiler.stop(experiment=ex)


def pjson(s):
    """
    Prints a string in JSON format and flushes stdout
    """
    print(json.dumps(s), flush=True)


class ExperimentWrapper:
    """
    A simple wrapper around a sacred experiment, making use of sacred's captured functions with prefixes.
    This allows a modular design of the configuration, where certain sub-dictionaries (e.g., "data") are parsed by
    specific method. This avoids having one large "main" function which takes all parameters as input.
    """

    def __init__(self, init_all=True):
        if init_all:
            self.init_all()

    # With the prefix option we can "filter" the configuration for the sub-dictionary under "dataset".
    @ex.capture(prefix="dataset")
    def init_dataset(self, dataset_type: str, data_params: dict):
        """
        Perform dataset loading, preprocessing etc.
        Since we set prefix="dataset ", this method only gets passed the respective sub-dictionary, enabling a modular
        experiment design.
        """

        if dataset_type in ("kang", "trapnell", "lincs"):
            self.datasets, self.dataset = load_dataset_splits(
                **data_params, return_dataset=True
            )

    @ex.capture(prefix="model")
    def init_drug_embedding(self, embedding: dict):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if embedding["model"] is not None:
            # ComPert will use the provided embedding, which is frozen during training
            self.drug_embeddings = get_chemical_representation(
                smiles=self.dataset.canon_smiles_unique_sorted,
                embedding_model=embedding["model"],
                data_dir=embedding["directory"],
                device=device,
            )
        else:
            # ComPert will initialize a new embedding, which is updated during training
            self.drug_embeddings = None

    @ex.capture(prefix="model")
    def init_model(self, hparams: dict, additional_params: dict):

        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.autoencoder = ComPert(
            self.datasets["training"].num_genes,
            self.datasets["training"].num_drugs,
            self.datasets["training"].num_covariates,
            device=device,
            **additional_params,
            hparams=hparams,
            drug_embeddings=self.drug_embeddings,
            use_drugs_idx=self.dataset.use_drugs_idx,
        )

    def update_datasets(self):
        """
        Instantiates a torch DataLoader for the given batchsize
        """

        self.datasets.update(
            {
                "loader_tr": torch.utils.data.DataLoader(
                    self.datasets["training"],
                    batch_size=self.autoencoder.hparams["batch_size"],
                    collate_fn=custom_collate,
                    shuffle=True,
                )
            }
        )
        # pjson({"training_args": args})
        # pjson({"autoencoder_params": self.autoencoder.hparams})

    @ex.capture
    def init_all(self, seed: int):
        """
        Sequentially run the sub-initializers of the experiment.
        """

        self.seed = seed
        self.init_dataset()
        self.init_drug_embedding()
        self.init_model()
        self.update_datasets()

    @ex.capture(prefix="training")
    def train(
        self,
        num_epochs: int,
        max_minutes: int,
        checkpoint_freq: int,
        ignore_evaluation: bool,
        run_eval_disentangle: bool,
        save_checkpoints: bool,
        save_dir: str,
    ):

        print(f"CWD: {os.getcwd()}")
        print(f"Save dir: {save_dir}")
        assert not save_checkpoints or (
            save_dir is not None and os.path.exists(save_dir)
        ), f"save_dir ({save_dir}) doesn't exist, create it first."

        start_time = time.time()
        for epoch in range(num_epochs):
            epoch_training_stats = defaultdict(float)

            for data in self.datasets["loader_tr"]:
                if self.dataset.use_drugs_idx:
                    genes, drugs_idx, dosages, covariates = (
                        data[0],
                        data[1],
                        data[2],
                        data[3:],
                    )
                    training_stats = self.autoencoder.update(
                        genes=genes,
                        drugs_idx=drugs_idx,
                        dosages=dosages,
                        covariates=covariates,
                    )
                else:
                    genes, drugs, covariates = data[0], data[1], data[2:]
                    training_stats = self.autoencoder.update(
                        genes=genes,
                        drugs=drugs,
                        covariates=covariates,
                    )

                for key, val in training_stats.items():
                    epoch_training_stats[key] += val

            for key, val in epoch_training_stats.items():
                epoch_training_stats[key] = val / len(self.datasets["loader_tr"])
                if not (key in self.autoencoder.history.keys()):
                    self.autoencoder.history[key] = []
                self.autoencoder.history[key].append(val)
            self.autoencoder.history["epoch"].append(epoch)

            # print some stats for each epoch
            pjson({"epoch": epoch, "training_stats": epoch_training_stats})

            ellapsed_minutes = (time.time() - start_time) / 60
            self.autoencoder.history["elapsed_time_min"] = ellapsed_minutes

            # decay learning rate if necessary
            # also check stopping condition: patience ran out OR
            # time ran out OR max epochs achieved
            stop = ellapsed_minutes > max_minutes or (epoch == num_epochs - 1)

            if ((epoch % checkpoint_freq) == 0 and epoch > 0) or stop:
                evaluation_stats = {}
                evaluation_stats["test"] = evaluate_r2(
                    self.autoencoder,
                    self.datasets["test_treated"],
                    self.datasets["test_control"].genes,
                )
                score = np.mean(evaluation_stats["test"])
                stop = stop or self.autoencoder.early_stopping(score)
                if not ignore_evaluation or stop:
                    if not stop:
                        evaluation_stats = evaluate(self.autoencoder, self.datasets)
                    else:
                        evaluation_stats = evaluate(
                            self.autoencoder,
                            self.datasets,
                            disentangle=run_eval_disentangle,
                        )
                    for key, val in evaluation_stats.items():
                        if not (key in self.autoencoder.history.keys()):
                            self.autoencoder.history[key] = []
                        self.autoencoder.history[key].append(val)
                    self.autoencoder.history["stats_epoch"].append(epoch)

                pjson(
                    {
                        "epoch": epoch,
                        "training_stats": epoch_training_stats,
                        "evaluation_stats": evaluation_stats,
                        "ellapsed_minutes": ellapsed_minutes,
                    }
                )

                improved_model = self.autoencoder.best_score <= score
                if save_checkpoints and improved_model:
                    if save_dir is None or not os.path.exists(save_dir):
                        raise ValueError(
                            "Please provide a valid directory for 'save_dir'."
                        )
                    file_name = f"{ex.observers[0].run_entry['config_hash']}_{ex.current_run.start_time.strftime('%Y-%m-%d_%H-%M-%S-%f')}.pt"
                    torch.save(
                        (
                            self.autoencoder.state_dict(),
                            self.autoencoder.init_args,
                            self.autoencoder.history,
                        ),
                        os.path.join(save_dir, file_name),
                    )
                    pjson({"model_saved": file_name})

                if stop:
                    pjson({"early_stop": epoch})
                    break

        results = self.autoencoder.history
        # results = pd.DataFrame.from_dict(results) # not same length!
        results["total_epochs"] = epoch
        return results


# We can call this command, e.g., from a Jupyter notebook with init_all=False to get an "empty" experiment wrapper,
# where we can then for instance load a pretrained model to inspect the performance.
@ex.command(unobserved=True)
def get_experiment(init_all=False):
    print("get_experiment")
    experiment = ExperimentWrapper(init_all=init_all)
    return experiment


# This function will be called by default. Note that we could in principle manually pass an experiment instance,
# e.g., obtained by loading a model from the database or by calling this from a Jupyter notebook.
@ex.automain
def train(experiment=None):
    if experiment is None:
        experiment = ExperimentWrapper()
    return experiment.train()
