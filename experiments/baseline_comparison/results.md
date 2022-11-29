# Second highest dose

|    | config.model.embedding.model   | config.model.load_pretrained   | config.dataset.data_params.split_key   |   result.val_mean_de |   result.test_mean |   result.test_mean_de |   result.perturbation disentanglement |   result.covariate disentanglement | config_hash                      |
|---:|:-------------------------------|:-------------------------------|:---------------------------------------|---------------------:|-------------------:|----------------------:|--------------------------------------:|-----------------------------------:|:---------------------------------|
|  9 | vanilla                        | False                          | split_baseline_A549                    |             0.74049  |           0.796837 |              0.664316 |                              0.110348 |                           0.644261 | 044c4dba0c8719985c3622834f2cbd58 |
| 30 | rdkit                          | True                           | split_baseline_A549                    |             0.76364  |           0.843732 |              0.793032 |                              0.117478 |                           0.669652 | 3326f900c45faaf99ca4400f78c58847 |
| 48 | rdkit                          | False                          | split_baseline_A549                    |             0.757339 |           0.818123 |              0.767883 |                              0.117391 |                           0.657043 | 8779ff45830000c6bc8e22023bb1cb2c |
| 19 | vanilla                        | False                          | split_baseline_K562                    |             0.744223 |           0.679318 |              0.477948 |                              0.106156 |                           0.686293 | 5ea85d5dd7abd5962d1d3eeff1b8c1ff |
| 50 | rdkit                          | True                           | split_baseline_K562                    |             0.766318 |           0.669244 |              0.587607 |                              0.111611 |                           0.59174  | 6388fa373386c11e40dceb5e2e8a113d |
| 68 | rdkit                          | False                          | split_baseline_K562                    |             0.758748 |           0.696678 |              0.547135 |                              0.110572 |                           0.660317 | 34fd06018d6e2662ccd5da7a16b57334 |
| 29 | vanilla                        | False                          | split_baseline_MCF7                    |             0.743061 |           0.675943 |              0.481244 |                              0.112676 |                           0.657728 | 4d98e7d857f497d870e19c6d12175aaa |
| 70 | rdkit                          | True                           | split_baseline_MCF7                    |             0.768464 |           0.792985 |              0.667422 |                              0.11719  |                           0.625767 | 2075a457bafdca5948ab671b77757974 |
| 87 | rdkit                          | False                          | split_baseline_MCF7                    |             0.746372 |           0.699372 |              0.498912 |                              0.1171   |                           0.688606 | 6ad52ba3939397521c5050ca1dd89a4c |

# Highest dose

|    | config.model.embedding.model   | config.model.load_pretrained   | config.dataset.data_params.split_key   |   result.val_mean_de |   result.test_mean |   result.test_mean_de |   result.perturbation disentanglement |   result.covariate disentanglement | config_hash                      |
|---:|:-------------------------------|:-------------------------------|:---------------------------------------|---------------------:|-------------------:|----------------------:|--------------------------------------:|-----------------------------------:|:---------------------------------|
|  1 | vanilla                        | False                          | split_baseline_A549                    |             0.673733 |           0.676855 |              0.538096 |                             0.0978514 |                           0.586775 | 4f5a9a00cb34fff872d9e650545f8d49 |
| 30 | rdkit                          | True                           | split_baseline_A549                    |             0.735164 |           0.873311 |              0.84548  |                             0.11484   |                           0.659227 | 8a077f7c4f6fd3aecc192eec50a1b7db |
| 43 | rdkit                          | False                          | split_baseline_A549                    |             0.723251 |           0.803806 |              0.739397 |                             0.119587  |                           0.627831 | abb6672bdaba28e59c22d8ef0a04a946 |
| 17 | vanilla                        | False                          | split_baseline_K562                    |             0.673669 |           0.492373 |              0.286343 |                             0.0966678 |                           0.558397 | 224debd3ad4bd09a254e23300b654f84 |
| 50 | rdkit                          | True                           | split_baseline_K562                    |             0.742996 |           0.66221  |              0.56839  |                             0.112009  |                           0.623804 | 99a342899b22d38659ef0f78b46d386b |
| 63 | rdkit                          | False                          | split_baseline_K562                    |             0.727149 |           0.622505 |              0.495356 |                             0.123062  |                           0.62933  | f8a333ed5a87d65898ce980862e58ba1 |
| 27 | vanilla                        | False                          | split_baseline_MCF7                    |             0.675772 |           0.448547 |              0.202625 |                             0.113254  |                           0.502279 | 9e09ecdbef94501e956db107758bbd75 |
| 70 | rdkit                          | True                           | split_baseline_MCF7                    |             0.742264 |           0.759469 |              0.620997 |                             0.114218  |                           0.626315 | 8c7f1848947f9a002eb62260ae92f584 |
| 83 | rdkit                          | False                          | split_baseline_MCF7                    |             0.721518 |           0.708941 |              0.517542 |                             0.12614   |                           0.681539 | 88dceb78980ad3e5da9f2b6245780d5a |