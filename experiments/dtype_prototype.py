# plum-dispatch-lab/experiment/dtype_prototype.py

import torch
from plum import dispatch

print(f"--- DType-Aware Dispatch Prototype ---")

# ===================================================================
# 1. THE FINAL STRATEGY: A Registry, No Patching.
#    The logic lives inside the main function.
# ===================================================================

# Step 1: Define the specific implementations as standalone, private functions.
def _process_uint8(x: torch.Tensor):
    print("-> [Exec] UINT8 path")
    return x.float()

def _process_float32(x: torch.Tensor):
    print("-> [Exec] FLOAT32 path")
    return x

# Step 2: Create the main dispatched function. THIS IS THE ONLY ONE
#         that handles the `torch.Tensor` type for Plum.
@dispatch
def process_tensor(x: torch.Tensor):
    """
    This function is the single entry point for all Tensors.
    It looks up the dtype in its own registry and calls the correct implementation.
    """
    # Look for a specific implementation in our registry.
    # The `.get` method returns `None` if the dtype is not found.
    specific_func = process_tensor._dtype_registry.get(x.dtype)
    
    if specific_func:
        # If we found a specific function, call it.
        return specific_func(x)
    else:
        # Otherwise, execute the generic fallback logic right here.
        print(f"-> [Exec] GENERIC TENSOR fallback for dtype: {x.dtype}")
        return x

# Step 3: Initialize the registry and populate it. We attach it to the
#         `process_tensor` object itself to keep everything tidy.
process_tensor._dtype_registry = {
    torch.uint8: _process_uint8,
    torch.float32: _process_float32,
}

# Step 4: Register any non-tensor functions as normal. This works perfectly.
@process_tensor.dispatch
def process_int(x: int):
    print(f"-> [Exec] INT path")
    return x

# ===================================================================
# 2. THE EXPERIMENT: Simplified, with no `try...finally`.
# ===================================================================

print("\n--- Running Tests ---")

print("\nTest 1: Calling with torch.uint8")
t_uint8 = torch.zeros(1, dtype=torch.uint8)
result = process_tensor(t_uint8)
assert result.dtype == torch.float32
print("-> OK")

print("\nTest 2: Calling with torch.float32")
t_float32 = torch.zeros(1, dtype=torch.float32)
result = process_tensor(t_float32)
assert result.dtype == torch.float32
print("-> OK")

print("\nTest 3: Calling with an un-registered tensor type (float64)")
t_float64 = torch.zeros(1, dtype=torch.float64)
result = process_tensor(t_float64)
assert result.dtype == torch.float64
print("-> OK")

print("\nTest 4: Calling with a non-tensor type")
result = process_tensor(100)
assert result == 100
print("-> OK")

print("\n\n All tests passed!")