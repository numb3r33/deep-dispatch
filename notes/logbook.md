# Logbook: Deep-Dispatch

## 2023-10-27: Day 0 - Liftoff

Project scaffolding is complete. The `deep-dispatch` repo is live. `fastcore` and `fastai` are forked and cloned locally with `upstream` remotes configured. This ensures we can stay in sync with the mainline repos while working on our experimental branch.

Next up: a preliminary dive into the call stack to get a feel for the beast. Dropping a breakpoint in `_TypeDispatch.__call__` and triggering it with `learn.show_batch()` seems like the perfect way to see it in its natural habitat.