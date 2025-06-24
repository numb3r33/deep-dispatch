# deep-dispatch: A Deep-Dive into Plum Dispatch for DL

This repository documents a research sprint into the `plum-dispatch` library, with a focus on its core resolver algorithm and its potential application and extension for deep-learning workloads in the fastai ecosystem.

## Plum-only Deep-Dive Roadmap (v3)

| Status | Step                                 | Goal                                                    | Concrete Deliverables                                                                                                                              |
| :----: | ------------------------------------ | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
|   ✔️   | 0. Project bootstrap                 | Single-track repo (plum-dispatch-lab/)                  | • README.md with roadmap<br>• requirements.txt pinning plum, fasttransform, fastai, pytest-benchmark                                            |
|   ⬜   | 1. “nano-plum” re-implementation     | Internalise algorithm by coding a 15-line toy resolver  | • `nano_plum.py`<br>• Shared pytest suite illustrating: simple match, subclass preference, ambiguity error                                           |
|   ⬜   | 2. Experimental branch (pick ONE)    | A) DType-aware B) Hybrid shim C) Speed hacker           | • Design memo `03_experiment_design.md`<br>• Prototype implementation `experiment/…`<br>• perfplot notebook comparing stock vs experimental       |
|   ⬜   | 3. fasttransform integration harness | Hot-swap resolver, run fasttransform / fastai tests     | • Script `run_tests.py` that monkey-patches resolver<br>• CSV of pass/fail & timing deltas                                                        |
|   ⬜   | 4. Write-up & demo notebook          | Produce publishable artefact                            | • 4-6 page report “Extending Plum Dispatch for Deep-Learning Workloads”<br>• Demo notebook: train a small CNN; toggle resolver; plot overhead      |
|   ⬜   | 5. Community feedback loop           | Gather edge-cases from real users                       | • GitHub Discussions + issue template<br>• Announcement post on fastai forum & r/MachineLearning                                                  |