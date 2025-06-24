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

@dispatch
def process(x: C):
    return "Processed as C"

c_instance = C()
print(process(c_instance)) # raises AmbiguousLookupError