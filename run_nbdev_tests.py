"""
run_nbdev_tests.py

Runs the fastai notebook test-suite (`nbdev_test`) from one level up,
optionally patching Plum’s dispatch to be dtype-aware, and **guaranteeing**
that any multiprocessing pool is started with a *spawn* context so that
PyTorch’s MPS backend on Apple-silicon does not crash.

Compatible with Python 3.12, nbdev 2.x, fastcore 1.5+, fastai 2.x.
"""

import multiprocessing as mp

# -- 1. PROCESS-START METHOD (do *before* importing torch/fastai) --------
mp.set_start_method("spawn", force=True)  # safety on macOS/Apple Silicon

# -- 2. STL & THIRD-PARTY IMPORTS ---------------------------------------
import sys, time, os
from contextlib import contextmanager
import pandas as pd

# -- 3. ADD PARENT DIR TO PATH (so `../fastai` is importable) ------------
sys.path.insert(0, "..")

# -- 4. GUARANTEE PARALLEL(… , method='spawn') ---------------------------
from fastcore import parallel as _fc_parallel
_parallel_orig = _fc_parallel.parallel

def _parallel_spawn(func, items, *args, **kwargs):
    kwargs.setdefault("method", "spawn")  # force spawn unless caller over-rides
    return _parallel_orig(func, items, *args, **kwargs)

_fc_parallel.parallel = _parallel_spawn  # ← monkey-patch in place

# -- 5. IMPORT TEST RUNNER ----------------------------------------------
from nbdev import test as nbtest

# -- 6. OPTIONAL PLUM HOT-PATCH -----------------------------------------
from plum.function import Function
from typing import Annotated, get_origin, get_args

_original_function_call = Function.__call__

def _dtype_aware_call(self: Function, *args, **kwargs):
    "Dispatch on `dtype` where present, else fall back to original resolution."
    if not any(hasattr(arg, "dtype") for arg in args):
        return _original_function_call(self, *args, **kwargs)

    call_key = tuple(
        (type(arg), arg.dtype) if hasattr(arg, "dtype") else type(arg) for arg in args
    )
    if not hasattr(self, "_dtype_cache"):
        self._dtype_cache = {}
    if call_key in self._dtype_cache:
        return self._dtype_cache[call_key](*args, **kwargs)

    applicable = []
    for method in self.methods:
        sig_types = method.signature.types
        if len(args) != len(sig_types):
            continue
        good = True
        for arg, sig_t in zip(args, sig_types):
            if get_origin(sig_t) is Annotated:
                base_t, annot = get_args(sig_t)
                if not (
                    isinstance(arg, base_t)
                    and hasattr(arg, "dtype")
                    and arg.dtype == annot
                ):
                    good = False
                    break
            elif not isinstance(arg, sig_t):
                good = False
                break
        if good:
            applicable.append(method)

    if not applicable:
        return _original_function_call(self, *args, **kwargs)

    if len(applicable) == 1:
        winner = applicable[0]
    else:
        better = [
            m1
            for m1 in applicable
            if all(m1.signature >= m2.signature for m2 in applicable)
        ]
        better = [m1 for m1 in better if not any(m2.signature > m1.signature for m2 in better)]
        if len(better) != 1:
            return _original_function_call(self, *args, **kwargs)
        winner = better[0]

    self._dtype_cache[call_key] = winner
    return winner(*args, **kwargs)

# -- 7. SMALL UTILS ------------------------------------------------------
@contextmanager
def patch_plum(active=True):
    "Context-manager to swap in/out the dtype-aware Plum call."
    if active:
        Function.__call__ = _dtype_aware_call
        print("+++ Plum Function.__call__ PATCHED +++")
    try:
        yield
    finally:
        if active:
            Function.__call__ = _original_function_call
            print("--- Plum Function.__call__ RESTORED ---")


@contextmanager
def chdir(path: str | os.PathLike):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


# -- 8. TEST-SUITE RUNNER ------------------------------------------------
def run_nbdev_suite(label: str, use_plum_patch: bool, n_workers: int = 0):
    """
    Execute `nbdev_test` from the fastai repo and return a summary dict.
    `n_workers=0` means *serial*; increase for spawn-parallel.
    """
    print(f"\n[{label}] Running nbdev_test (n_workers={n_workers}) …")
    t0 = time.time()
    passed = False
    try:
        with chdir("../fastai"):
            passed = nbtest.nbdev_test(path="/Users/abhisheksharma/Desktop/src/github/fastai/nbs/08_vision.data.ipynb", n_workers=n_workers)
    except SystemExit as ex:  # nbdev_test may call sys.exit(1) on failure
        passed = ex.code == 0
    except Exception:
        import traceback

        traceback.print_exc()

    dt = time.time() - t0
    status = "PASS" if passed else "FAIL"
    print(f"[{label}] {status} in {dt:.2f}s")
    return {"suite": "fastai/nbdev_test", "version": label, "status": status, "duration": dt}


# -- 9. MAIN -------------------------------------------------------------
if __name__ == "__main__":
    results = []
    # First run with Plum patch enabled
    with patch_plum(True):
        results.append(run_nbdev_suite("patched", use_plum_patch=True, n_workers=0))

    # Second run without the Plum patch
    with patch_plum(False):
        results.append(run_nbdev_suite("stock", use_plum_patch=False, n_workers=0))

    # Save simple CSV summary
    df = pd.DataFrame(results)
    df.to_csv("pass_fail_timing.csv", index=False)
    print("\nSaved timing to pass_fail_timing.csv")
    print(df)
