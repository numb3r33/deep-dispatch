import torch
from plum import dispatch
from fastai.vision.all import TensorImage # Using a fastai-specific type

# Define a dispatched function
@dispatch
def foo(x: int, y: TensorImage):
    return x * 2

# Call the function to trigger the dispatch mechanism
print("Calling dispatched function 'foo'...")
foo(1, TensorImage(torch.zeros(1, 1)))
print("Call complete.")