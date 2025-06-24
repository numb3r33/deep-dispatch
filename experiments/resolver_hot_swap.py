import plum
from plum import dispatch
from plum.resolver import Resolver

# --- THE MONKEY-PATCHING STRATEGY ---

# 1. Save a reference to the ORIGINAL `resolve` method from the Resolver class.
#    This is crucial for restoration and for calling the original logic.
original_resolve = Resolver.resolve

# 2. Define our new, custom resolve method.
#    It MUST have the same signature as the original: `(self, types)`.
def dtype_aware_resolve(self, types):
    """Our new global resolve logic."""
    print(f"MONKEY-PATCH ACTIVATED for types: {types} on resolver: {id(self)}")
    
    # After our custom logic, we call the original method to complete the dispatch.
    # We must pass `self` along with the other arguments.
    return original_resolve(self, types)

# 3. Define a test function. When it's created, it gets a standard Resolver instance.
@dispatch
def my_func(x: int):
    print(f"-> Executing my_func(int)")
    return x

# 4. Use a `try...finally` block to ensure our changes are always reverted.
try:
    # --- DEMONSTRATE THE HOT-SWAP ---
    print("--- 1. Calling with the default, un-patched behavior ---")
    my_func(1)
    
    print("\n--- 2. Applying the monkey-patch to the Resolver class ---")
    # This globally changes the behavior of ALL Resolver instances.
    Resolver.resolve = dtype_aware_resolve
    
    # Now, when my_func calls its internal resolver's .resolve() method,
    # it will execute our patched code.
    my_func(1)
    
    # Let's prove it works for other functions too
    @dispatch
    def my_other_func(x: str):
        print("-> Executing my_other_func(str)")
    
    my_other_func("hello")

finally:
    # --- RESTORATION ---
    print("\n--- 3. Restoring the original Resolver.resolve method ---")
    # This is critical to clean up our experiment.
    Resolver.resolve = original_resolve

print("\n--- 4. Calling after restoration to confirm it's back to normal ---")
my_func(1)

print("\n✅ Patching and restoration complete.")