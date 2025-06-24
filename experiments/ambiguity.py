from plum import dispatch

class A: pass
class B: pass
class C(A, B): pass

@dispatch
def process(x: A):
    return "Processed as A"

@dispatch
def process(x: B):
    return "Processed as B"

c_instance = C()
process(c_instance) # raises AmbiguousLookupError