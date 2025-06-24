# Design Memo: DType-Aware Dispatch for Plum

## Motivation

Standard dispatch systems operate on class types. A function signature

`def process(x: torch.Tensor): ....` will match any tensor, regardless of its underlying data type (dtype). In deep learning and scientific computing, the dtype is often as important as the class. For example:

* A uint8 tensor of an image (values 0-255) must be converted to float32 and normalized (values 0.0-1.0) before entering a model.
* Low-precision bfloat16 tensors require numerical stability considerations than float64 tensors.

A dispatch system that can natively select an implementation based on dtype would allow for cleaner, safer and more explicit code, removing the need for if/elif blocks a single function body.

## Proposed API

We will leverage the standard typing.Annotated type, introduced in Python 3.9. It is the modern, accepted way to attach metadata to type hints.

