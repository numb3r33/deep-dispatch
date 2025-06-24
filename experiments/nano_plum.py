class AmbiguousLookupError(LookupError):
    """Raised when multiple methods are equally specific."""
    pass

class NotFoundLookupError(LookupError):
    """Raised when no applicable method can be found."""
    pass

class NanoResolver:
    def __init__(self):
        self._signatures = {} # Maps a signature tuple to a function
    
    def register(self, *signature):
        def decorator(func):
            self._signatures[signature] = func
            return func
        return decorator

    def _is_applicable(self, call_sig, impl_sig):
        """Check if an implementation is applicable for a given call."""

        if len(call_sig) != len(impl_sig):
            return False
        return all(issubclass(c, i) for c, i in zip(call_sig, impl_sig))
    
    def _is_more_specific(self, sig_a, sig_b):
        """Check if signature A is strictly more specific than signature B."""
        # A is more specific if all its types are subclasses of B's types,
        # and at least one is a strict subclass.
        return (all(issubclass(a, b) for a, b in zip(sig_a, sig_b)) and any(a is not b for a, b in zip(sig_a, sig_b)))
    
    def resolve(self, *call_sig):
        """Find the best implementation for a given call signature."""
        # 1. Find all applicable methods
        applicable = [
            impl_sig for impl_sig in self._signatures if self._is_applicable(call_sig, impl_sig)
        ]

        if not applicable:
            raise NotFoundLookupError(f"No implementation found for {call_sig}")
        
        if len(applicable) == 1:
            return self._signatures[applicable[0]]
        
        # 2. Find the unique, most-specific method among the applicable ones

        best_method = None
        for sig1 in applicable:
            is_best = True
            for sig2 in applicable:
                if sig1 is not sig2 and not self._is_more_specific(sig1, sig2):
                    is_best = False
                    break
            if is_best:
                if best_method is not None:
                    # We found another "best" method, which means ambiguity
                    raise AmbiguousLookupError(f"Call {call_sig} is ambiguous between implementations.")
                best_method = self._signatures[sig1]
        
        if best_method is None:
            # This happens in a perfect tie, e.g., the diamond problem
            raise AmbiguousLookupError(f"Call {call_sig} is ambiguous between implementations.")
        
        return best_method