import pytest
from nano_plum import NanoResolver, AmbiguousLookupError, NotFoundLookupError

# --- Test Fixture -----
@pytest.fixture
def resolver():
    r = NanoResolver()

    # Define some types for testing
    class A: pass
    class B(A): pass
    class C(A): pass
    class D(B, C): pass


    # Register functions
    @r.register(A)
    def process_a(x): return "A"

    @r.register(B)
    def process_b(x): return "B"

    @r.register(C)
    def process_c(x): return "C"

    return r, (A, B, C, D)


# --- Test Cases -----

def test_simple_match(resolver):
    """Tests that a direct match works."""
    r, (A, B, C, D) = resolver
    func = r.resolve(A)
    assert func(A()) == "A"


def test_subclass_preference(resolver):
    """TEsts taht the more specific subclas implementation is chosen."""
    r, (A, B, C, D) = resolver

    # Calling with type B should resolve to `process_b`, not `process_a`

    func = r.resolve(B)
    assert func(B()) == "B"

def test_ambiguity_error(resolver):
    """Tests that the diamond problem correctly raises an AmbiguityLookupError."""

    r, (A, B, C, D) = resolver
    # D is both a B and a C. Neither is more specific than the other.

    with pytest.raises(AmbiguousLookupError):
        r.resolve(D)

def test_not_found_error(resolver):
    """Tests that calling with an unregistered type raises an error."""
    r, types = resolver
    class Unregistered: pass
    with pytest.raises(NotFoundLookupError):
        r.resolve(Unregistered)

def test_two_arg_dispatch(resolver):
    """Tests dispatch with multiple arguments."""

    r, (A, B, C, D) = resolver

    @r.register(A, int)
    def process_a_int(x, y): return "A, int"

    @r.register(B, int)
    def process_b_int(x, y): return "B, int"

    # The more specific (B, int) should be chosen over (A, int)
    func = r.resolve(B, int)
    assert func(B(), 1) == "B, int"