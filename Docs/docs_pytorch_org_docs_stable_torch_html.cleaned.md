

--- DOCUMENT: https://docs.pytorch.org/docs/stable/torch.html#tensors/ ---
# torch[#](https://docs.pytorch.org/docs/stable/torch.html#module-torch "Link to this heading")
Created On: Dec 23, 2016 | Last Updated On: Jan 08, 2026
The torch package contains data structures for multi-dimensional tensors and defines mathematical operations over these tensors. Additionally, it provides many utilities for efficient serialization of Tensors and arbitrary types, and other useful utilities.
It has a CUDA counterpart, that enables you to run your tensor computations on an NVIDIA GPU with compute capability >= 3.0.
## Tensors[#](https://docs.pytorch.org/docs/stable/torch.html#tensors "Link to this heading")
| [`is_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.is_tensor.html#torch.is_tensor "torch.is_tensor")  | Returns True if obj is a PyTorch tensor.  |
| --- | --- |
| [`is_storage`](https://docs.pytorch.org/docs/stable/generated/torch.is_storage.html#torch.is_storage "torch.is_storage")  | Returns True if obj is a PyTorch storage object.  |
| [`is_complex`](https://docs.pytorch.org/docs/stable/generated/torch.is_complex.html#torch.is_complex "torch.is_complex")  | Returns True if the data type of `input` is a complex data type i.e., one of `torch.complex64`, and `torch.complex128`.  |
| [`is_conj`](https://docs.pytorch.org/docs/stable/generated/torch.is_conj.html#torch.is_conj "torch.is_conj")  | Returns True if the `input` is a conjugated tensor, i.e. its conjugate bit is set to True.  |
| [`is_floating_point`](https://docs.pytorch.org/docs/stable/generated/torch.is_floating_point.html#torch.is_floating_point "torch.is_floating_point")  | Returns True if the data type of `input` is a floating point data type i.e., one of `torch.float64`, `torch.float32`, `torch.float16`, and `torch.bfloat16`.  |
| [`is_nonzero`](https://docs.pytorch.org/docs/stable/generated/torch.is_nonzero.html#torch.is_nonzero "torch.is_nonzero")  | Returns True if the `input` is a single element tensor which is not equal to zero after type conversions.  |
| [`set_default_dtype`](https://docs.pytorch.org/docs/stable/generated/torch.set_default_dtype.html#torch.set_default_dtype "torch.set_default_dtype")  | Sets the default floating point dtype to `d`.  |
| [`get_default_dtype`](https://docs.pytorch.org/docs/stable/generated/torch.get_default_dtype.html#torch.get_default_dtype "torch.get_default_dtype")  | Get the current default floating point [`torch.dtype`](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.dtype "torch.dtype").  |
| [`set_default_device`](https://docs.pytorch.org/docs/stable/generated/torch.set_default_device.html#torch.set_default_device "torch.set_default_device")  | Sets the default `torch.Tensor` to be allocated on `device`.  |
| [`get_default_device`](https://docs.pytorch.org/docs/stable/generated/torch.get_default_device.html#torch.get_default_device "torch.get_default_device")  | Gets the default `torch.Tensor` to be allocated on `device`  |
| [`set_default_tensor_type`](https://docs.pytorch.org/docs/stable/generated/torch.set_default_tensor_type.html#torch.set_default_tensor_type "torch.set_default_tensor_type")  |   |
| [`numel`](https://docs.pytorch.org/docs/stable/generated/torch.numel.html#torch.numel "torch.numel")  | Returns the total number of elements in the `input` tensor.  |
| [`set_printoptions`](https://docs.pytorch.org/docs/stable/generated/torch.set_printoptions.html#torch.set_printoptions "torch.set_printoptions")  | Set options for printing.  |
| [`set_flush_denormal`](https://docs.pytorch.org/docs/stable/generated/torch.set_flush_denormal.html#torch.set_flush_denormal "torch.set_flush_denormal")  | Disables denormal floating numbers on CPU.  |
### Creation Ops[#](https://docs.pytorch.org/docs/stable/torch.html#creation-ops "Link to this heading")
Note
Random sampling creation ops are listed under [Random sampling](https://docs.pytorch.org/docs/stable/torch.html#random-sampling) and include: [`torch.rand()`](https://docs.pytorch.org/docs/stable/generated/torch.rand.html#torch.rand "torch.rand") [`torch.rand_like()`](https://docs.pytorch.org/docs/stable/generated/torch.rand_like.html#torch.rand_like "torch.rand_like") [`torch.randn()`](https://docs.pytorch.org/docs/stable/generated/torch.randn.html#torch.randn "torch.randn") [`torch.randn_like()`](https://docs.pytorch.org/docs/stable/generated/torch.randn_like.html#torch.randn_like "torch.randn_like") [`torch.randint()`](https://docs.pytorch.org/docs/stable/generated/torch.randint.html#torch.randint "torch.randint") [`torch.randint_like()`](https://docs.pytorch.org/docs/stable/generated/torch.randint_like.html#torch.randint_like "torch.randint_like") [`torch.randperm()`](https://docs.pytorch.org/docs/stable/generated/torch.randperm.html#torch.randperm "torch.randperm") You may also use [`torch.empty()`](https://docs.pytorch.org/docs/stable/generated/torch.empty.html#torch.empty "torch.empty") with the [In-place random sampling](https://docs.pytorch.org/docs/stable/torch.html#inplace-random-sampling) methods to create [`torch.Tensor`](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") s with values sampled from a broader range of distributions.
| [`tensor`](https://docs.pytorch.org/docs/stable/generated/torch.tensor.html#torch.tensor "torch.tensor")  | Constructs a tensor with no autograd history (also known as a "leaf tensor", see [Autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd.html)) by copying `data`.  |
| --- | --- |
| [`sparse_coo_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.sparse_coo_tensor.html#torch.sparse_coo_tensor "torch.sparse_coo_tensor")  | Constructs a [sparse tensor in COO(rdinate) format](https://docs.pytorch.org/docs/stable/sparse.html#sparse-coo-docs) with specified values at the given `indices`.  |
| [`sparse_csr_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.sparse_csr_tensor.html#torch.sparse_csr_tensor "torch.sparse_csr_tensor")  | Constructs a [sparse tensor in CSR (Compressed Sparse Row)](https://docs.pytorch.org/docs/stable/sparse.html#sparse-csr-docs) with specified values at the given `crow_indices` and `col_indices`.  |
| [`sparse_csc_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.sparse_csc_tensor.html#torch.sparse_csc_tensor "torch.sparse_csc_tensor")  | Constructs a [sparse tensor in CSC (Compressed Sparse Column)](https://docs.pytorch.org/docs/stable/sparse.html#sparse-csc-docs) with specified values at the given `ccol_indices` and `row_indices`.  |
| [`sparse_bsr_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.sparse_bsr_tensor.html#torch.sparse_bsr_tensor "torch.sparse_bsr_tensor")  | Constructs a [sparse tensor in BSR (Block Compressed Sparse Row))](https://docs.pytorch.org/docs/stable/sparse.html#sparse-bsr-docs) with specified 2-dimensional blocks at the given `crow_indices` and `col_indices`.  |
| [`sparse_bsc_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.sparse_bsc_tensor.html#torch.sparse_bsc_tensor "torch.sparse_bsc_tensor")  | Constructs a [sparse tensor in BSC (Block Compressed Sparse Column))](https://docs.pytorch.org/docs/stable/sparse.html#sparse-bsc-docs) with specified 2-dimensional blocks at the given `ccol_indices` and `row_indices`.  |
| [`asarray`](https://docs.pytorch.org/docs/stable/generated/torch.asarray.html#torch.asarray "torch.asarray")  | Converts `obj` to a tensor.  |
| [`as_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.as_tensor.html#torch.as_tensor "torch.as_tensor")  | Converts `data` into a tensor, sharing data and preserving autograd history if possible.  |
| [`as_strided`](https://docs.pytorch.org/docs/stable/generated/torch.as_strided.html#torch.as_strided "torch.as_strided")  | Create a view of an existing torch.Tensor `input` with specified `size`, `stride` and `storage_offset`.  |
| [`from_file`](https://docs.pytorch.org/docs/stable/generated/torch.from_file.html#torch.from_file "torch.from_file")  | Creates a CPU tensor with a storage backed by a memory-mapped file.  |
| [`from_numpy`](https://docs.pytorch.org/docs/stable/generated/torch.from_numpy.html#torch.from_numpy "torch.from_numpy")  | Creates a [`Tensor`](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") from a [`numpy.ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "\(in NumPy v2.4\)").  |
| [`from_dlpack`](https://docs.pytorch.org/docs/stable/generated/torch.from_dlpack.html#torch.from_dlpack "torch.from_dlpack")  | Converts a tensor from an external library into a `torch.Tensor`.  |
| [`frombuffer`](https://docs.pytorch.org/docs/stable/generated/torch.frombuffer.html#torch.frombuffer "torch.frombuffer")  | Creates a 1-dimensional [`Tensor`](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") from an object that implements the Python buffer protocol.  |
| [`zeros`](https://docs.pytorch.org/docs/stable/generated/torch.zeros.html#torch.zeros "torch.zeros")  | Returns a tensor filled with the scalar value 0, with the shape defined by the variable argument `size`.  |
| [`zeros_like`](https://docs.pytorch.org/docs/stable/generated/torch.zeros_like.html#torch.zeros_like "torch.zeros_like")  | Returns a tensor filled with the scalar value 0, with the same size as `input`.  |
| [`ones`](https://docs.pytorch.org/docs/stable/generated/torch.ones.html#torch.ones "torch.ones")  | Returns a tensor filled with the scalar value 1, with the shape defined by the variable argument `size`.  |
| [`ones_like`](https://docs.pytorch.org/docs/stable/generated/torch.ones_like.html#torch.ones_like "torch.ones_like")  | Returns a tensor filled with the scalar value 1, with the same size as `input`.  |
| [`arange`](https://docs.pytorch.org/docs/stable/generated/torch.arange.html#torch.arange "torch.arange")  | Returns a 1-D tensor of size ⌈end−startstep⌉\left\lceil \frac{\text{end} - \text{start}}{\text{step}} \right\rceil⌈stepend−start​⌉ with values from the interval `[start, end)` taken with common difference `step` beginning from start.  |
| [`range`](https://docs.pytorch.org/docs/stable/generated/torch.range.html#torch.range "torch.range")  | Returns a 1-D tensor of size ⌊end−startstep⌋+1\left\lfloor \frac{\text{end} - \text{start}}{\text{step}} \right\rfloor + 1⌊stepend−start​⌋+1 with values from `start` to `end` with step `step`.  |
| [`linspace`](https://docs.pytorch.org/docs/stable/generated/torch.linspace.html#torch.linspace "torch.linspace")  | Creates a one-dimensional tensor of size `steps` whose values are evenly spaced from `start` to `end`, inclusive.  |
| [`logspace`](https://docs.pytorch.org/docs/stable/generated/torch.logspace.html#torch.logspace "torch.logspace")  | Creates a one-dimensional tensor of size `steps` whose values are evenly spaced from basestart{{\text{{base}}}}^{{\text{{start}}}}basestart to baseend{{\text{{base}}}}^{{\text{{end}}}}baseend, inclusive, on a logarithmic scale with base `base`.  |
| [`eye`](https://docs.pytorch.org/docs/stable/generated/torch.eye.html#torch.eye "torch.eye")  | Returns a 2-D tensor with ones on the diagonal and zeros elsewhere.  |
| [`empty`](https://docs.pytorch.org/docs/stable/generated/torch.empty.html#torch.empty "torch.empty")  | Returns a tensor filled with uninitialized data.  |
| [`empty_like`](https://docs.pytorch.org/docs/stable/generated/torch.empty_like.html#torch.empty_like "torch.empty_like")  | Returns an uninitialized tensor with the same size as `input`.  |
| [`empty_strided`](https://docs.pytorch.org/docs/stable/generated/torch.empty_strided.html#torch.empty_strided "torch.empty_strided")  | Creates a tensor with the specified `size` and `stride` and filled with undefined data.  |
| [`full`](https://docs.pytorch.org/docs/stable/generated/torch.full.html#torch.full "torch.full")  | Creates a tensor of size `size` filled with `fill_value`.  |
| [`full_like`](https://docs.pytorch.org/docs/stable/generated/torch.full_like.html#torch.full_like "torch.full_like")  | Returns a tensor with the same size as `input` filled with `fill_value`.  |
| [`quantize_per_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.quantize_per_tensor.html#torch.quantize_per_tensor "torch.quantize_per_tensor")  | Converts a float tensor to a quantized tensor with given scale and zero point.  |
| [`quantize_per_channel`](https://docs.pytorch.org/docs/stable/generated/torch.quantize_per_channel.html#torch.quantize_per_channel "torch.quantize_per_channel")  | Converts a float tensor to a per-channel quantized tensor with given scales and zero points.  |
| [`dequantize`](https://docs.pytorch.org/docs/stable/generated/torch.dequantize.html#torch.dequantize "torch.dequantize")  | Returns an fp32 Tensor by dequantizing a quantized Tensor  |
| [`complex`](https://docs.pytorch.org/docs/stable/generated/torch.complex.html#torch.complex "torch.complex")  | Constructs a complex tensor with its real part equal to [`real`](https://docs.pytorch.org/docs/stable/generated/torch.real.html#torch.real "torch.real") and its imaginary part equal to [`imag`](https://docs.pytorch.org/docs/stable/generated/torch.imag.html#torch.imag "torch.imag").  |
| [`polar`](https://docs.pytorch.org/docs/stable/generated/torch.polar.html#torch.polar "torch.polar")  | Constructs a complex tensor whose elements are Cartesian coordinates corresponding to the polar coordinates with absolute value [`abs`](https://docs.pytorch.org/docs/stable/generated/torch.abs.html#torch.abs "torch.abs") and angle [`angle`](https://docs.pytorch.org/docs/stable/generated/torch.angle.html#torch.angle "torch.angle").  |
| [`heaviside`](https://docs.pytorch.org/docs/stable/generated/torch.heaviside.html#torch.heaviside "torch.heaviside")  | Computes the Heaviside step function for each element in `input`.  |
### Indexing, Slicing, Joining, Mutating Ops[#](https://docs.pytorch.org/docs/stable/torch.html#indexing-slicing-joining-mutating-ops "Link to this heading")
| [`adjoint`](https://docs.pytorch.org/docs/stable/generated/torch.adjoint.html#torch.adjoint "torch.adjoint")  | Returns a view of the tensor conjugated and with the last two dimensions transposed.  |
| --- | --- |
| [`argwhere`](https://docs.pytorch.org/docs/stable/generated/torch.argwhere.html#torch.argwhere "torch.argwhere")  | Returns a tensor containing the indices of all non-zero elements of `input`.  |
| [`cat`](https://docs.pytorch.org/docs/stable/generated/torch.cat.html#torch.cat "torch.cat")  | Concatenates the given sequence of tensors in `tensors` in the given dimension.  |
| [`concat`](https://docs.pytorch.org/docs/stable/generated/torch.concat.html#torch.concat "torch.concat")  | Alias of [`torch.cat()`](https://docs.pytorch.org/docs/stable/generated/torch.cat.html#torch.cat "torch.cat").  |
| [`concatenate`](https://docs.pytorch.org/docs/stable/generated/torch.concatenate.html#torch.concatenate "torch.concatenate")  | Alias of [`torch.cat()`](https://docs.pytorch.org/docs/stable/generated/torch.cat.html#torch.cat "torch.cat").  |
| [`conj`](https://docs.pytorch.org/docs/stable/generated/torch.conj.html#torch.conj "torch.conj")  | Returns a view of `input` with a flipped conjugate bit.  |
| [`chunk`](https://docs.pytorch.org/docs/stable/generated/torch.chunk.html#torch.chunk "torch.chunk")  | Attempts to split a tensor into the specified number of chunks.  |
| [`dsplit`](https://docs.pytorch.org/docs/stable/generated/torch.dsplit.html#torch.dsplit "torch.dsplit")  | Splits `input`, a tensor with three or more dimensions, into multiple tensors depthwise according to `indices_or_sections`.  |
| [`column_stack`](https://docs.pytorch.org/docs/stable/generated/torch.column_stack.html#torch.column_stack "torch.column_stack")  | Creates a new tensor by horizontally stacking the tensors in `tensors`.  |
| [`dstack`](https://docs.pytorch.org/docs/stable/generated/torch.dstack.html#torch.dstack "torch.dstack")  | Stack tensors in sequence depthwise (along third axis).  |
| [`gather`](https://docs.pytorch.org/docs/stable/generated/torch.gather.html#torch.gather "torch.gather")  | Gathers values along an axis specified by dim.  |
| [`hsplit`](https://docs.pytorch.org/docs/stable/generated/torch.hsplit.html#torch.hsplit "torch.hsplit")  | Splits `input`, a tensor with one or more dimensions, into multiple tensors horizontally according to `indices_or_sections`.  |
| [`hstack`](https://docs.pytorch.org/docs/stable/generated/torch.hstack.html#torch.hstack "torch.hstack")  | Stack tensors in sequence horizontally (column wise).  |
| [`index_add`](https://docs.pytorch.org/docs/stable/generated/torch.index_add.html#torch.index_add "torch.index_add")  | See [`index_add_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.index_add_.html#torch.Tensor.index_add_ "torch.Tensor.index_add_") for function description.  |
| [`index_copy`](https://docs.pytorch.org/docs/stable/generated/torch.index_copy.html#torch.index_copy "torch.index_copy")  | See [`index_add_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.index_add_.html#torch.Tensor.index_add_ "torch.Tensor.index_add_") for function description.  |
| [`index_reduce`](https://docs.pytorch.org/docs/stable/generated/torch.index_reduce.html#torch.index_reduce "torch.index_reduce")  | See [`index_reduce_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.index_reduce_.html#torch.Tensor.index_reduce_ "torch.Tensor.index_reduce_") for function description.  |
| [`index_select`](https://docs.pytorch.org/docs/stable/generated/torch.index_select.html#torch.index_select "torch.index_select")  | Returns a new tensor which indexes the `input` tensor along dimension `dim` using the entries in `index`.  |
| [`masked_select`](https://docs.pytorch.org/docs/stable/generated/torch.masked_select.html#torch.masked_select "torch.masked_select")  | Returns a new 1-D tensor which indexes the `input` tensor according to the boolean mask `mask` which is a BoolTensor.  |
| [`movedim`](https://docs.pytorch.org/docs/stable/generated/torch.movedim.html#torch.movedim "torch.movedim")  | Moves the dimension(s) of `input` at the position(s) in `source` to the position(s) in `destination`.  |
| [`moveaxis`](https://docs.pytorch.org/docs/stable/generated/torch.moveaxis.html#torch.moveaxis "torch.moveaxis")  | Alias for [`torch.movedim()`](https://docs.pytorch.org/docs/stable/generated/torch.movedim.html#torch.movedim "torch.movedim").  |
| [`narrow`](https://docs.pytorch.org/docs/stable/generated/torch.narrow.html#torch.narrow "torch.narrow")  | Returns a new tensor that is a narrowed version of `input` tensor.  |
| [`narrow_copy`](https://docs.pytorch.org/docs/stable/generated/torch.narrow_copy.html#torch.narrow_copy "torch.narrow_copy")  | Same as [`Tensor.narrow()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.narrow.html#torch.Tensor.narrow "torch.Tensor.narrow") except this returns a copy rather than shared storage.  |
| [`nonzero`](https://docs.pytorch.org/docs/stable/generated/torch.nonzero.html#torch.nonzero "torch.nonzero")  |   |
| [`permute`](https://docs.pytorch.org/docs/stable/generated/torch.permute.html#torch.permute "torch.permute")  | Returns a view of the original tensor `input` with its dimensions permuted.  |
| [`reshape`](https://docs.pytorch.org/docs/stable/generated/torch.reshape.html#torch.reshape "torch.reshape")  | Returns a tensor with the same data and number of elements as `input`, but with the specified shape.  |
| [`row_stack`](https://docs.pytorch.org/docs/stable/generated/torch.row_stack.html#torch.row_stack "torch.row_stack")  | Alias of [`torch.vstack()`](https://docs.pytorch.org/docs/stable/generated/torch.vstack.html#torch.vstack "torch.vstack").  |
| [`select`](https://docs.pytorch.org/docs/stable/generated/torch.select.html#torch.select "torch.select")  | Slices the `input` tensor along the selected dimension at the given index.  |
| [`scatter`](https://docs.pytorch.org/docs/stable/generated/torch.scatter.html#torch.scatter "torch.scatter")  | Out-of-place version of [`torch.Tensor.scatter_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.scatter_.html#torch.Tensor.scatter_ "torch.Tensor.scatter_")  |
| [`diagonal_scatter`](https://docs.pytorch.org/docs/stable/generated/torch.diagonal_scatter.html#torch.diagonal_scatter "torch.diagonal_scatter")  | Embeds the values of the `src` tensor into `input` along the diagonal elements of `input`, with respect to `dim1` and `dim2`.  |
| [`select_scatter`](https://docs.pytorch.org/docs/stable/generated/torch.select_scatter.html#torch.select_scatter "torch.select_scatter")  | Embeds the values of the `src` tensor into `input` at the given index.  |
| [`slice_scatter`](https://docs.pytorch.org/docs/stable/generated/torch.slice_scatter.html#torch.slice_scatter "torch.slice_scatter")  | Embeds the values of the `src` tensor into `input` at the given dimension.  |
| [`scatter_add`](https://docs.pytorch.org/docs/stable/generated/torch.scatter_add.html#torch.scatter_add "torch.scatter_add")  | Out-of-place version of [`torch.Tensor.scatter_add_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.scatter_add_.html#torch.Tensor.scatter_add_ "torch.Tensor.scatter_add_")  |
| [`scatter_reduce`](https://docs.pytorch.org/docs/stable/generated/torch.scatter_reduce.html#torch.scatter_reduce "torch.scatter_reduce")  | Out-of-place version of [`torch.Tensor.scatter_reduce_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.scatter_reduce_.html#torch.Tensor.scatter_reduce_ "torch.Tensor.scatter_reduce_")  |
| [`segment_reduce`](https://docs.pytorch.org/docs/stable/generated/torch.segment_reduce.html#torch.segment_reduce "torch.segment_reduce")  | Perform a segment reduction operation on the input tensor along the specified axis.  |
| [`split`](https://docs.pytorch.org/docs/stable/generated/torch.split.html#torch.split "torch.split")  | Splits the tensor into chunks.  |
| [`squeeze`](https://docs.pytorch.org/docs/stable/generated/torch.squeeze.html#torch.squeeze "torch.squeeze")  | Returns a tensor with all specified dimensions of `input` of size 1 removed.  |
| [`stack`](https://docs.pytorch.org/docs/stable/generated/torch.stack.html#torch.stack "torch.stack")  | Concatenates a sequence of tensors along a new dimension.  |
| [`swapaxes`](https://docs.pytorch.org/docs/stable/generated/torch.swapaxes.html#torch.swapaxes "torch.swapaxes")  | Alias for [`torch.transpose()`](https://docs.pytorch.org/docs/stable/generated/torch.transpose.html#torch.transpose "torch.transpose").  |
| [`swapdims`](https://docs.pytorch.org/docs/stable/generated/torch.swapdims.html#torch.swapdims "torch.swapdims")  | Alias for [`torch.transpose()`](https://docs.pytorch.org/docs/stable/generated/torch.transpose.html#torch.transpose "torch.transpose").  |
| [`t`](https://docs.pytorch.org/docs/stable/generated/torch.t.html#torch.t "torch.t")  | Expects `input` to be <= 2-D tensor and transposes dimensions 0 and 1.  |
| [`take`](https://docs.pytorch.org/docs/stable/generated/torch.take.html#torch.take "torch.take")  | Returns a new tensor with the elements of `input` at the given indices.  |
| [`take_along_dim`](https://docs.pytorch.org/docs/stable/generated/torch.take_along_dim.html#torch.take_along_dim "torch.take_along_dim")  | Selects values from `input` at the 1-dimensional indices from `indices` along the given `dim`.  |
| [`tensor_split`](https://docs.pytorch.org/docs/stable/generated/torch.tensor_split.html#torch.tensor_split "torch.tensor_split")  | Splits a tensor into multiple sub-tensors, all of which are views of `input`, along dimension `dim` according to the indices or number of sections specified by `indices_or_sections`.  |
| [`tile`](https://docs.pytorch.org/docs/stable/generated/torch.tile.html#torch.tile "torch.tile")  | Constructs a tensor by repeating the elements of `input`.  |
| [`transpose`](https://docs.pytorch.org/docs/stable/generated/torch.transpose.html#torch.transpose "torch.transpose")  | Returns a tensor that is a transposed version of `input`.  |
| [`unbind`](https://docs.pytorch.org/docs/stable/generated/torch.unbind.html#torch.unbind "torch.unbind")  | Removes a tensor dimension.  |
| [`unravel_index`](https://docs.pytorch.org/docs/stable/generated/torch.unravel_index.html#torch.unravel_index "torch.unravel_index")  | Converts a tensor of flat indices into a tuple of coordinate tensors that index into an arbitrary tensor of the specified shape.  |
| [`unsqueeze`](https://docs.pytorch.org/docs/stable/generated/torch.unsqueeze.html#torch.unsqueeze "torch.unsqueeze")  | Returns a new tensor with a dimension of size one inserted at the specified position.  |
| [`vsplit`](https://docs.pytorch.org/docs/stable/generated/torch.vsplit.html#torch.vsplit "torch.vsplit")  | Splits `input`, a tensor with two or more dimensions, into multiple tensors vertically according to `indices_or_sections`.  |
| [`vstack`](https://docs.pytorch.org/docs/stable/generated/torch.vstack.html#torch.vstack "torch.vstack")  | Stack tensors in sequence vertically (row wise).  |
| [`where`](https://docs.pytorch.org/docs/stable/generated/torch.where.html#torch.where "torch.where")  | Return a tensor of elements selected from either `input` or `other`, depending on `condition`.  |
## Accelerators[#](https://docs.pytorch.org/docs/stable/torch.html#accelerators "Link to this heading")
Within the PyTorch repo, we define an “Accelerator” as a [`torch.device`](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.device "torch.device") that is being used alongside a CPU to speed up computation. These devices use an asynchronous execution scheme, using [`torch.Stream`](https://docs.pytorch.org/docs/stable/generated/torch.Stream.html#torch.Stream "torch.Stream") and [`torch.Event`](https://docs.pytorch.org/docs/stable/generated/torch.Event.html#torch.Event "torch.Event") as their main way to perform synchronization. We also assume that only one such accelerator can be available at once on a given host. This allows us to use the current accelerator as the default device for relevant concepts such as pinned memory, Stream device_type, FSDP, etc.
As of today, accelerator devices are (in no particular order) [“CUDA”](https://docs.pytorch.org/docs/stable/cuda.html), [“MTIA”](https://docs.pytorch.org/docs/stable/mtia.html), [“XPU”](https://docs.pytorch.org/docs/stable/xpu.html), [“MPS”](https://docs.pytorch.org/docs/stable/mps.html), “HPU”, and PrivateUse1 (many device not in the PyTorch repo itself).
Many tools in the PyTorch Ecosystem use fork to create subprocesses (for example dataloading or intra-op parallelism), it is thus important to delay as much as possible any operation that would prevent further forks. This is especially important here as most accelerator’s initialization has such effect. In practice, you should keep in mind that checking [`torch.accelerator.current_accelerator()`](https://docs.pytorch.org/docs/stable/generated/torch.accelerator.current_accelerator.html#torch.accelerator.current_accelerator "torch.accelerator.current_accelerator") is a compile-time check by default, it is thus always fork-safe. On the contrary, passing the `check_available=True` flag to this function or calling [`torch.accelerator.is_available()`](https://docs.pytorch.org/docs/stable/generated/torch.accelerator.is_available.html#torch.accelerator.is_available "torch.accelerator.is_available") will usually prevent later fork.
Some backends provide an experimental opt-in option to make the runtime availability check fork-safe. When using the CUDA device `PYTORCH_NVML_BASED_CUDA_CHECK=1` can be used for example.
| [`Stream`](https://docs.pytorch.org/docs/stable/generated/torch.Stream.html#torch.Stream "torch.Stream")  | An in-order queue of executing the respective tasks asynchronously in first in first out (FIFO) order.  |
| --- | --- |
| [`Event`](https://docs.pytorch.org/docs/stable/generated/torch.Event.html#torch.Event "torch.Event")  | Query and record Stream status to identify or control dependencies across Stream and measure timing.  |
## Generators[#](https://docs.pytorch.org/docs/stable/torch.html#generators "Link to this heading")
| [`Generator`](https://docs.pytorch.org/docs/stable/generated/torch.Generator.html#torch.Generator "torch.Generator")  | Creates and returns a generator object that manages the state of the algorithm which produces pseudo random numbers.  |
| --- | --- |
## Random sampling[#](https://docs.pytorch.org/docs/stable/torch.html#random-sampling "Link to this heading")
| [`seed`](https://docs.pytorch.org/docs/stable/generated/torch.seed.html#torch.seed "torch.seed")  | Sets the seed for generating random numbers to a non-deterministic random number on all devices.  |
| --- | --- |
| [`manual_seed`](https://docs.pytorch.org/docs/stable/generated/torch.manual_seed.html#torch.manual_seed "torch.manual_seed")  | Sets the seed for generating random numbers on all devices.  |
| [`initial_seed`](https://docs.pytorch.org/docs/stable/generated/torch.initial_seed.html#torch.initial_seed "torch.initial_seed")  | Returns the initial seed for generating random numbers as a Python long.  |
| [`get_rng_state`](https://docs.pytorch.org/docs/stable/generated/torch.get_rng_state.html#torch.get_rng_state "torch.get_rng_state")  | Returns the random number generator state as a torch.ByteTensor.  |
| [`set_rng_state`](https://docs.pytorch.org/docs/stable/generated/torch.set_rng_state.html#torch.set_rng_state "torch.set_rng_state")  | Sets the random number generator state.  |

torch.default_generator _Returns the default CPU torch.Generator_[#](https://docs.pytorch.org/docs/stable/torch.html#torch.torch.default_generator "Link to this definition")

| [`bernoulli`](https://docs.pytorch.org/docs/stable/generated/torch.bernoulli.html#torch.bernoulli "torch.bernoulli")  | Draws binary random numbers (0 or 1) from a Bernoulli distribution.  |
| --- | --- |
| [`multinomial`](https://docs.pytorch.org/docs/stable/generated/torch.multinomial.html#torch.multinomial "torch.multinomial")  | Returns a tensor where each row contains `num_samples` indices sampled from the multinomial (a stricter definition would be multivariate, refer to [`torch.distributions.multinomial.Multinomial`](https://docs.pytorch.org/docs/stable/distributions.html#torch.distributions.multinomial.Multinomial "torch.distributions.multinomial.Multinomial") for more details) probability distribution located in the corresponding row of tensor `input`.  |
| [`normal`](https://docs.pytorch.org/docs/stable/generated/torch.normal.html#torch.normal "torch.normal")  | Returns a tensor of random numbers drawn from separate normal distributions whose mean and standard deviation are given.  |
| [`poisson`](https://docs.pytorch.org/docs/stable/generated/torch.poisson.html#torch.poisson "torch.poisson")  | Returns a tensor of the same size as `input` with each element sampled from a Poisson distribution with rate parameter given by the corresponding element in `input` i.e.,  |
| [`rand`](https://docs.pytorch.org/docs/stable/generated/torch.rand.html#torch.rand "torch.rand")  | Returns a tensor filled with random numbers from a uniform distribution on the interval [0,1)[0, 1)[0,1)  |
| [`rand_like`](https://docs.pytorch.org/docs/stable/generated/torch.rand_like.html#torch.rand_like "torch.rand_like")  | Returns a tensor with the same size as `input` that is filled with random numbers from a uniform distribution on the interval [0,1)[0, 1)[0,1).  |
| [`randint`](https://docs.pytorch.org/docs/stable/generated/torch.randint.html#torch.randint "torch.randint")  | Returns a tensor filled with random integers generated uniformly between `low` (inclusive) and `high` (exclusive).  |
| [`randint_like`](https://docs.pytorch.org/docs/stable/generated/torch.randint_like.html#torch.randint_like "torch.randint_like")  | Returns a tensor with the same shape as Tensor `input` filled with random integers generated uniformly between `low` (inclusive) and `high` (exclusive).  |
| [`randn`](https://docs.pytorch.org/docs/stable/generated/torch.randn.html#torch.randn "torch.randn")  | Returns a tensor filled with random numbers from a normal distribution with mean 0 and variance 1 (also called the standard normal distribution).  |
| [`randn_like`](https://docs.pytorch.org/docs/stable/generated/torch.randn_like.html#torch.randn_like "torch.randn_like")  | Returns a tensor with the same size as `input` that is filled with random numbers from a normal distribution with mean 0 and variance 1.  |
| [`randperm`](https://docs.pytorch.org/docs/stable/generated/torch.randperm.html#torch.randperm "torch.randperm")  | Returns a random permutation of integers from `0` to `n - 1`.  |
### In-place random sampling[#](https://docs.pytorch.org/docs/stable/torch.html#in-place-random-sampling "Link to this heading")
There are a few more in-place random sampling functions defined on Tensors as well. Click through to refer to their documentation:
  * [`torch.Tensor.bernoulli_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.bernoulli_.html#torch.Tensor.bernoulli_ "torch.Tensor.bernoulli_") - in-place version of [`torch.bernoulli()`](https://docs.pytorch.org/docs/stable/generated/torch.bernoulli.html#torch.bernoulli "torch.bernoulli")
  * [`torch.Tensor.cauchy_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.cauchy_.html#torch.Tensor.cauchy_ "torch.Tensor.cauchy_") - numbers drawn from the Cauchy distribution
  * [`torch.Tensor.exponential_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.exponential_.html#torch.Tensor.exponential_ "torch.Tensor.exponential_") - numbers drawn from the exponential distribution
  * [`torch.Tensor.geometric_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.geometric_.html#torch.Tensor.geometric_ "torch.Tensor.geometric_") - elements drawn from the geometric distribution
  * [`torch.Tensor.log_normal_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.log_normal_.html#torch.Tensor.log_normal_ "torch.Tensor.log_normal_") - samples from the log-normal distribution
  * [`torch.Tensor.normal_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.normal_.html#torch.Tensor.normal_ "torch.Tensor.normal_") - in-place version of [`torch.normal()`](https://docs.pytorch.org/docs/stable/generated/torch.normal.html#torch.normal "torch.normal")
  * [`torch.Tensor.random_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.random_.html#torch.Tensor.random_ "torch.Tensor.random_") - numbers sampled from the discrete uniform distribution
  * [`torch.Tensor.uniform_()`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.uniform_.html#torch.Tensor.uniform_ "torch.Tensor.uniform_") - numbers sampled from the continuous uniform distribution


### Quasi-random sampling[#](https://docs.pytorch.org/docs/stable/torch.html#quasi-random-sampling "Link to this heading")
| [`quasirandom.SobolEngine`](https://docs.pytorch.org/docs/stable/generated/torch.quasirandom.SobolEngine.html#torch.quasirandom.SobolEngine "torch.quasirandom.SobolEngine")  | The [`torch.quasirandom.SobolEngine`](https://docs.pytorch.org/docs/stable/generated/torch.quasirandom.SobolEngine.html#torch.quasirandom.SobolEngine "torch.quasirandom.SobolEngine") is an engine for generating (scrambled) Sobol sequences.  |
| --- | --- |
## Serialization[#](https://docs.pytorch.org/docs/stable/torch.html#serialization "Link to this heading")
| [`save`](https://docs.pytorch.org/docs/stable/generated/torch.save.html#torch.save "torch.save")  | Saves an object to a disk file.  |
| --- | --- |
| [`load`](https://docs.pytorch.org/docs/stable/generated/torch.load.html#torch.load "torch.load")  | Loads an object saved with [`torch.save()`](https://docs.pytorch.org/docs/stable/generated/torch.save.html#torch.save "torch.save") from a file.  |
## Parallelism[#](https://docs.pytorch.org/docs/stable/torch.html#parallelism "Link to this heading")
| [`get_num_threads`](https://docs.pytorch.org/docs/stable/generated/torch.get_num_threads.html#torch.get_num_threads "torch.get_num_threads")  | Returns the number of threads used for parallelizing CPU operations  |
| --- | --- |
| [`set_num_threads`](https://docs.pytorch.org/docs/stable/generated/torch.set_num_threads.html#torch.set_num_threads "torch.set_num_threads")  | Sets the number of threads used for intraop parallelism on CPU.  |
| [`get_num_interop_threads`](https://docs.pytorch.org/docs/stable/generated/torch.get_num_interop_threads.html#torch.get_num_interop_threads "torch.get_num_interop_threads")  | Returns the number of threads used for inter-op parallelism on CPU (e.g. in JIT interpreter).  |
| [`set_num_interop_threads`](https://docs.pytorch.org/docs/stable/generated/torch.set_num_interop_threads.html#torch.set_num_interop_threads "torch.set_num_interop_threads")  | Sets the number of threads used for interop parallelism (e.g. in JIT interpreter) on CPU.  |
## Locally disabling gradient computation[#](https://docs.pytorch.org/docs/stable/torch.html#locally-disabling-gradient-computation "Link to this heading")
The context managers [`torch.no_grad()`](https://docs.pytorch.org/docs/stable/generated/torch.no_grad.html#torch.no_grad "torch.no_grad"), [`torch.enable_grad()`](https://docs.pytorch.org/docs/stable/generated/torch.enable_grad.html#torch.enable_grad "torch.enable_grad"), and `torch.set_grad_enabled()` are helpful for locally disabling and enabling gradient computation. See [Locally disabling gradient computation](https://docs.pytorch.org/docs/stable/autograd.html#locally-disable-grad) for more details on their usage. These context managers are thread local, so they won’t work if you send work to another thread using the `threading` module, etc.
Examples:

```
>>> x = torch.zeros(1, requires_grad=True)
>>> with torch.no_grad():
...     y = x * 2
>>> y.requires_grad
False

>>> is_train = False
>>> with torch.set_grad_enabled(is_train):
...     y = x * 2
>>> y.requires_grad
False

>>> torch.set_grad_enabled(True)  # this can also be used as a function
>>> y = x * 2
>>> y.requires_grad
True

>>> torch.set_grad_enabled(False)
>>> y = x * 2
>>> y.requires_grad
False

```
Copy to clipboard
| [`no_grad`](https://docs.pytorch.org/docs/stable/generated/torch.no_grad.html#torch.no_grad "torch.no_grad")  | Context-manager that disables gradient calculation.  |
| --- | --- |
| [`enable_grad`](https://docs.pytorch.org/docs/stable/generated/torch.enable_grad.html#torch.enable_grad "torch.enable_grad")  | Context-manager that enables gradient calculation.  |
| [`autograd.grad_mode.set_grad_enabled`](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.set_grad_enabled.html#torch.autograd.grad_mode.set_grad_enabled "torch.autograd.grad_mode.set_grad_enabled")  | Context-manager that sets gradient calculation on or off.  |
| [`is_grad_enabled`](https://docs.pytorch.org/docs/stable/generated/torch.is_grad_enabled.html#torch.is_grad_enabled "torch.is_grad_enabled")  | Returns True if grad mode is currently enabled.  |
| [`autograd.grad_mode.inference_mode`](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html#torch.autograd.grad_mode.inference_mode "torch.autograd.grad_mode.inference_mode")  | Context manager that enables or disables inference mode.  |
| [`is_inference_mode_enabled`](https://docs.pytorch.org/docs/stable/generated/torch.is_inference_mode_enabled.html#torch.is_inference_mode_enabled "torch.is_inference_mode_enabled")  | Returns True if inference mode is currently enabled.  |
## Math operations[#](https://docs.pytorch.org/docs/stable/torch.html#math-operations "Link to this heading")
### Constants[#](https://docs.pytorch.org/docs/stable/torch.html#constants "Link to this heading")
| `inf`  | A floating-point positive infinity. Alias for `math.inf`.  |
| --- | --- |
| `nan`  | A floating-point “not a number” value. This value is not a legal number. Alias for `math.nan`.  |
### Pointwise Ops[#](https://docs.pytorch.org/docs/stable/torch.html#pointwise-ops "Link to this heading")
| [`abs`](https://docs.pytorch.org/docs/stable/generated/torch.abs.html#torch.abs "torch.abs")  | Computes the absolute value of each element in `input`.  |
| --- | --- |
| [`absolute`](https://docs.pytorch.org/docs/stable/generated/torch.absolute.html#torch.absolute "torch.absolute")  | Alias for [`torch.abs()`](https://docs.pytorch.org/docs/stable/generated/torch.abs.html#torch.abs "torch.abs")  |
| [`acos`](https://docs.pytorch.org/docs/stable/generated/torch.acos.html#torch.acos "torch.acos")  | Returns a new tensor with the arccosine (in radians) of each element in `input`.  |
| [`arccos`](https://docs.pytorch.org/docs/stable/generated/torch.arccos.html#torch.arccos "torch.arccos")  | Alias for [`torch.acos()`](https://docs.pytorch.org/docs/stable/generated/torch.acos.html#torch.acos "torch.acos").  |
| [`acosh`](https://docs.pytorch.org/docs/stable/generated/torch.acosh.html#torch.acosh "torch.acosh")  | Returns a new tensor with the inverse hyperbolic cosine of the elements of `input`.  |
| [`arccosh`](https://docs.pytorch.org/docs/stable/generated/torch.arccosh.html#torch.arccosh "torch.arccosh")  | Alias for [`torch.acosh()`](https://docs.pytorch.org/docs/stable/generated/torch.acosh.html#torch.acosh "torch.acosh").  |
| [`add`](https://docs.pytorch.org/docs/stable/generated/torch.add.html#torch.add "torch.add")  | Adds `other`, scaled by `alpha`, to `input`.  |
| [`addcdiv`](https://docs.pytorch.org/docs/stable/generated/torch.addcdiv.html#torch.addcdiv "torch.addcdiv")  | Performs the element-wise division of `tensor1` by `tensor2`, multiplies the result by the scalar `value` and adds it to `input`.  |
| [`addcmul`](https://docs.pytorch.org/docs/stable/generated/torch.addcmul.html#torch.addcmul "torch.addcmul")  | Performs the element-wise multiplication of `tensor1` by `tensor2`, multiplies the result by the scalar `value` and adds it to `input`.  |
| [`angle`](https://docs.pytorch.org/docs/stable/generated/torch.angle.html#torch.angle "torch.angle")  | Computes the element-wise angle (in radians) of the given `input` tensor.  |
| [`asin`](https://docs.pytorch.org/docs/stable/generated/torch.asin.html#torch.asin "torch.asin")  | Returns a new tensor with the arcsine of the elements (in radians) in the `input` tensor.  |
| [`arcsin`](https://docs.pytorch.org/docs/stable/generated/torch.arcsin.html#torch.arcsin "torch.arcsin")  | Alias for [`torch.asin()`](https://docs.pytorch.org/docs/stable/generated/torch.asin.html#torch.asin "torch.asin").  |
| [`asinh`](https://docs.pytorch.org/docs/stable/generated/torch.asinh.html#torch.asinh "torch.asinh")  | Returns a new tensor with the inverse hyperbolic sine of the elements of `input`.  |
| [`arcsinh`](https://docs.pytorch.org/docs/stable/generated/torch.arcsinh.html#torch.arcsinh "torch.arcsinh")  | Alias for [`torch.asinh()`](https://docs.pytorch.org/docs/stable/generated/torch.asinh.html#torch.asinh "torch.asinh").  |
| [`atan`](https://docs.pytorch.org/docs/stable/generated/torch.atan.html#torch.atan "torch.atan")  | Returns a new tensor with the arctangent of the elements (in radians) in the `input` tensor.  |
| [`arctan`](https://docs.pytorch.org/docs/stable/generated/torch.arctan.html#torch.arctan "torch.arctan")  | Alias for [`torch.atan()`](https://docs.pytorch.org/docs/stable/generated/torch.atan.html#torch.atan "torch.atan").  |
| [`atanh`](https://docs.pytorch.org/docs/stable/generated/torch.atanh.html#torch.atanh "torch.atanh")  | Returns a new tensor with the inverse hyperbolic tangent of the elements of `input`.  |
| [`arctanh`](https://docs.pytorch.org/docs/stable/generated/torch.arctanh.html#torch.arctanh "torch.arctanh")  | Alias for [`torch.atanh()`](https://docs.pytorch.org/docs/stable/generated/torch.atanh.html#torch.atanh "torch.atanh").  |
| [`atan2`](https://docs.pytorch.org/docs/stable/generated/torch.atan2.html#torch.atan2 "torch.atan2")  | Element-wise arctangent of inputi/otheri\text{input}_{i} / \text{other}_{i}inputi​/otheri​ with consideration of the quadrant.  |
| [`arctan2`](https://docs.pytorch.org/docs/stable/generated/torch.arctan2.html#torch.arctan2 "torch.arctan2")  | Alias for [`torch.atan2()`](https://docs.pytorch.org/docs/stable/generated/torch.atan2.html#torch.atan2 "torch.atan2").  |
| [`bitwise_not`](https://docs.pytorch.org/docs/stable/generated/torch.bitwise_not.html#torch.bitwise_not "torch.bitwise_not")  | Computes the bitwise NOT of the given input tensor.  |
| [`bitwise_and`](https://docs.pytorch.org/docs/stable/generated/torch.bitwise_and.html#torch.bitwise_and "torch.bitwise_and")  | Computes the bitwise AND of `input` and `other`.  |
| [`bitwise_or`](https://docs.pytorch.org/docs/stable/generated/torch.bitwise_or.html#torch.bitwise_or "torch.bitwise_or")  | Computes the bitwise OR of `input` and `other`.  |
| [`bitwise_xor`](https://docs.pytorch.org/docs/stable/generated/torch.bitwise_xor.html#torch.bitwise_xor "torch.bitwise_xor")  | Computes the bitwise XOR of `input` and `other`.  |
| [`bitwise_left_shift`](https://docs.pytorch.org/docs/stable/generated/torch.bitwise_left_shift.html#torch.bitwise_left_shift "torch.bitwise_left_shift")  | Computes the left arithmetic shift of `input` by `other` bits.  |
| [`bitwise_right_shift`](https://docs.pytorch.org/docs/stable/generated/torch.bitwise_right_shift.html#torch.bitwise_right_shift "torch.bitwise_right_shift")  | Computes the right arithmetic shift of `input` by `other` bits.  |
| [`ceil`](https://docs.pytorch.org/docs/stable/generated/torch.ceil.html#torch.ceil "torch.ceil")  | Returns a new tensor with the ceil of the elements of `input`, the smallest integer greater than or equal to each element.  |
| [`clamp`](https://docs.pytorch.org/docs/stable/generated/torch.clamp.html#torch.clamp "torch.clamp")  | Clamps all elements in `input` into the range [ [`min`](https://docs.pytorch.org/docs/stable/generated/torch.min.html#torch.min "torch.min"), [`max`](https://docs.pytorch.org/docs/stable/generated/torch.max.html#torch.max "torch.max") ].  |
| [`clip`](https://docs.pytorch.org/docs/stable/generated/torch.clip.html#torch.clip "torch.clip")  | Alias for [`torch.clamp()`](https://docs.pytorch.org/docs/stable/generated/torch.clamp.html#torch.clamp "torch.clamp").  |
| [`conj_physical`](https://docs.pytorch.org/docs/stable/generated/torch.conj_physical.html#torch.conj_physical "torch.conj_physical")  | Computes the element-wise conjugate of the given `input` tensor.  |
| [`copysign`](https://docs.pytorch.org/docs/stable/generated/torch.copysign.html#torch.copysign "torch.copysign")  | Create a new floating-point tensor with the magnitude of `input` and the sign of `other`, elementwise.  |
| [`cos`](https://docs.pytorch.org/docs/stable/generated/torch.cos.html#torch.cos "torch.cos")  | Returns a new tensor with the cosine of the elements of `input` given in radians.  |
| [`cosh`](https://docs.pytorch.org/docs/stable/generated/torch.cosh.html#torch.cosh "torch.cosh")  | Returns a new tensor with the hyperbolic cosine of the elements of `input`.  |
| [`deg2rad`](https://docs.pytorch.org/docs/stable/generated/torch.deg2rad.html#torch.deg2rad "torch.deg2rad")  | Returns a new tensor with each of the elements of `input` converted from angles in degrees to radians.  |
| [`div`](https://docs.pytorch.org/docs/stable/generated/torch.div.html#torch.div "torch.div")  | Divides each element of the input `input` by the corresponding element of `other`.  |
| [`divide`](https://docs.pytorch.org/docs/stable/generated/torch.divide.html#torch.divide "torch.divide")  | Alias for [`torch.div()`](https://docs.pytorch.org/docs/stable/generated/torch.div.html#torch.div "torch.div").  |
| [`digamma`](https://docs.pytorch.org/docs/stable/generated/torch.digamma.html#torch.digamma "torch.digamma")  | Alias for [`torch.special.digamma()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.digamma "torch.special.digamma").  |
| [`erf`](https://docs.pytorch.org/docs/stable/generated/torch.erf.html#torch.erf "torch.erf")  | Alias for [`torch.special.erf()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.erf "torch.special.erf").  |
| [`erfc`](https://docs.pytorch.org/docs/stable/generated/torch.erfc.html#torch.erfc "torch.erfc")  | Alias for [`torch.special.erfc()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.erfc "torch.special.erfc").  |
| [`erfinv`](https://docs.pytorch.org/docs/stable/generated/torch.erfinv.html#torch.erfinv "torch.erfinv")  | Alias for [`torch.special.erfinv()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.erfinv "torch.special.erfinv").  |
| [`exp`](https://docs.pytorch.org/docs/stable/generated/torch.exp.html#torch.exp "torch.exp")  | Returns a new tensor with the exponential of the elements of the input tensor `input`.  |
| [`exp2`](https://docs.pytorch.org/docs/stable/generated/torch.exp2.html#torch.exp2 "torch.exp2")  | Alias for [`torch.special.exp2()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.exp2 "torch.special.exp2").  |
| [`expm1`](https://docs.pytorch.org/docs/stable/generated/torch.expm1.html#torch.expm1 "torch.expm1")  | Alias for [`torch.special.expm1()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.expm1 "torch.special.expm1").  |
| [`fake_quantize_per_channel_affine`](https://docs.pytorch.org/docs/stable/generated/torch.fake_quantize_per_channel_affine.html#torch.fake_quantize_per_channel_affine "torch.fake_quantize_per_channel_affine")  | Returns a new tensor with the data in `input` fake quantized per channel using `scale`, `zero_point`, `quant_min` and `quant_max`, across the channel specified by `axis`.  |
| [`fake_quantize_per_tensor_affine`](https://docs.pytorch.org/docs/stable/generated/torch.fake_quantize_per_tensor_affine.html#torch.fake_quantize_per_tensor_affine "torch.fake_quantize_per_tensor_affine")  | Returns a new tensor with the data in `input` fake quantized using `scale`, `zero_point`, `quant_min` and `quant_max`.  |
| [`fix`](https://docs.pytorch.org/docs/stable/generated/torch.fix.html#torch.fix "torch.fix")  | Alias for [`torch.trunc()`](https://docs.pytorch.org/docs/stable/generated/torch.trunc.html#torch.trunc "torch.trunc")  |
| [`float_power`](https://docs.pytorch.org/docs/stable/generated/torch.float_power.html#torch.float_power "torch.float_power")  | Raises `input` to the power of `exponent`, elementwise, in double precision.  |
| [`floor`](https://docs.pytorch.org/docs/stable/generated/torch.floor.html#torch.floor "torch.floor")  | Returns a new tensor with the floor of the elements of `input`, the largest integer less than or equal to each element.  |
| [`floor_divide`](https://docs.pytorch.org/docs/stable/generated/torch.floor_divide.html#torch.floor_divide "torch.floor_divide")  |   |
| [`fmod`](https://docs.pytorch.org/docs/stable/generated/torch.fmod.html#torch.fmod "torch.fmod")  | Applies C++'s [std::fmod](https://en.cppreference.com/w/cpp/numeric/math/fmod) entrywise.  |
| [`frac`](https://docs.pytorch.org/docs/stable/generated/torch.frac.html#torch.frac "torch.frac")  | Computes the fractional portion of each element in `input`.  |
| [`frexp`](https://docs.pytorch.org/docs/stable/generated/torch.frexp.html#torch.frexp "torch.frexp")  | Decomposes `input` into mantissa and exponent tensors such that input=mantissa×2exponent\text{input} = \text{mantissa} \times 2^{\text{exponent}}input=mantissa×2exponent.  |
| [`gradient`](https://docs.pytorch.org/docs/stable/generated/torch.gradient.html#torch.gradient "torch.gradient")  | Estimates the gradient of a function g:Rn→Rg : \mathbb{R}^n \rightarrow \mathbb{R}g:Rn→R in one or more dimensions using the [second-order accurate central differences method](https://www.ams.org/journals/mcom/1988-51-184/S0025-5718-1988-0935077-0/S0025-5718-1988-0935077-0.pdf) and either first or second order estimates at the boundaries.  |
| [`imag`](https://docs.pytorch.org/docs/stable/generated/torch.imag.html#torch.imag "torch.imag")  | Returns a new tensor containing imaginary values of the `self` tensor.  |
| [`ldexp`](https://docs.pytorch.org/docs/stable/generated/torch.ldexp.html#torch.ldexp "torch.ldexp")  | Multiplies `input` by 2 ** `other`.  |
| [`lerp`](https://docs.pytorch.org/docs/stable/generated/torch.lerp.html#torch.lerp "torch.lerp")  | Does a linear interpolation of two tensors `start` (given by `input`) and `end` based on a scalar or tensor `weight` and returns the resulting `out` tensor.  |
| [`lgamma`](https://docs.pytorch.org/docs/stable/generated/torch.lgamma.html#torch.lgamma "torch.lgamma")  | Computes the natural logarithm of the absolute value of the gamma function on `input`.  |
| [`log`](https://docs.pytorch.org/docs/stable/generated/torch.log.html#torch.log "torch.log")  | Returns a new tensor with the natural logarithm of the elements of `input`.  |
| [`log10`](https://docs.pytorch.org/docs/stable/generated/torch.log10.html#torch.log10 "torch.log10")  | Returns a new tensor with the logarithm to the base 10 of the elements of `input`.  |
| [`log1p`](https://docs.pytorch.org/docs/stable/generated/torch.log1p.html#torch.log1p "torch.log1p")  | Returns a new tensor with the natural logarithm of (1 + `input`).  |
| [`log2`](https://docs.pytorch.org/docs/stable/generated/torch.log2.html#torch.log2 "torch.log2")  | Returns a new tensor with the logarithm to the base 2 of the elements of `input`.  |
| [`logaddexp`](https://docs.pytorch.org/docs/stable/generated/torch.logaddexp.html#torch.logaddexp "torch.logaddexp")  | Logarithm of the sum of exponentiations of the inputs.  |
| [`logaddexp2`](https://docs.pytorch.org/docs/stable/generated/torch.logaddexp2.html#torch.logaddexp2 "torch.logaddexp2")  | Logarithm of the sum of exponentiations of the inputs in base-2.  |
| [`logical_and`](https://docs.pytorch.org/docs/stable/generated/torch.logical_and.html#torch.logical_and "torch.logical_and")  | Computes the element-wise logical AND of the given input tensors.  |
| [`logical_not`](https://docs.pytorch.org/docs/stable/generated/torch.logical_not.html#torch.logical_not "torch.logical_not")  | Computes the element-wise logical NOT of the given input tensor.  |
| [`logical_or`](https://docs.pytorch.org/docs/stable/generated/torch.logical_or.html#torch.logical_or "torch.logical_or")  | Computes the element-wise logical OR of the given input tensors.  |
| [`logical_xor`](https://docs.pytorch.org/docs/stable/generated/torch.logical_xor.html#torch.logical_xor "torch.logical_xor")  | Computes the element-wise logical XOR of the given input tensors.  |
| [`logit`](https://docs.pytorch.org/docs/stable/generated/torch.logit.html#torch.logit "torch.logit")  | Alias for [`torch.special.logit()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.logit "torch.special.logit").  |
| [`hypot`](https://docs.pytorch.org/docs/stable/generated/torch.hypot.html#torch.hypot "torch.hypot")  | Given the legs of a right triangle, return its hypotenuse.  |
| [`i0`](https://docs.pytorch.org/docs/stable/generated/torch.i0.html#torch.i0 "torch.i0")  | Alias for [`torch.special.i0()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.i0 "torch.special.i0").  |
| [`igamma`](https://docs.pytorch.org/docs/stable/generated/torch.igamma.html#torch.igamma "torch.igamma")  | Alias for [`torch.special.gammainc()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.gammainc "torch.special.gammainc").  |
| [`igammac`](https://docs.pytorch.org/docs/stable/generated/torch.igammac.html#torch.igammac "torch.igammac")  | Alias for [`torch.special.gammaincc()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.gammaincc "torch.special.gammaincc").  |
| [`mul`](https://docs.pytorch.org/docs/stable/generated/torch.mul.html#torch.mul "torch.mul")  | Multiplies `input` by `other`.  |
| [`multiply`](https://docs.pytorch.org/docs/stable/generated/torch.multiply.html#torch.multiply "torch.multiply")  | Alias for [`torch.mul()`](https://docs.pytorch.org/docs/stable/generated/torch.mul.html#torch.mul "torch.mul").  |
| [`mvlgamma`](https://docs.pytorch.org/docs/stable/generated/torch.mvlgamma.html#torch.mvlgamma "torch.mvlgamma")  | Alias for [`torch.special.multigammaln()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.multigammaln "torch.special.multigammaln").  |
| [`nan_to_num`](https://docs.pytorch.org/docs/stable/generated/torch.nan_to_num.html#torch.nan_to_num "torch.nan_to_num")  | Replaces `NaN`, positive infinity, and negative infinity values in `input` with the values specified by `nan`, `posinf`, and `neginf`, respectively.  |
| [`neg`](https://docs.pytorch.org/docs/stable/generated/torch.neg.html#torch.neg "torch.neg")  | Returns a new tensor with the negative of the elements of `input`.  |
| [`negative`](https://docs.pytorch.org/docs/stable/generated/torch.negative.html#torch.negative "torch.negative")  | Alias for [`torch.neg()`](https://docs.pytorch.org/docs/stable/generated/torch.neg.html#torch.neg "torch.neg")  |
| [`nextafter`](https://docs.pytorch.org/docs/stable/generated/torch.nextafter.html#torch.nextafter "torch.nextafter")  | Return the next floating-point value after `input` towards `other`, elementwise.  |
| [`polygamma`](https://docs.pytorch.org/docs/stable/generated/torch.polygamma.html#torch.polygamma "torch.polygamma")  | Alias for [`torch.special.polygamma()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.polygamma "torch.special.polygamma").  |
| [`positive`](https://docs.pytorch.org/docs/stable/generated/torch.positive.html#torch.positive "torch.positive")  | Returns `input`.  |
| [`pow`](https://docs.pytorch.org/docs/stable/generated/torch.pow.html#torch.pow "torch.pow")  | Takes the power of each element in `input` with `exponent` and returns a tensor with the result.  |
| [`quantized_batch_norm`](https://docs.pytorch.org/docs/stable/generated/torch.quantized_batch_norm.html#torch.quantized_batch_norm "torch.quantized_batch_norm")  | Applies batch normalization on a 4D (NCHW) quantized tensor.  |
| [`quantized_max_pool1d`](https://docs.pytorch.org/docs/stable/generated/torch.quantized_max_pool1d.html#torch.quantized_max_pool1d "torch.quantized_max_pool1d")  | Applies a 1D max pooling over an input quantized tensor composed of several input planes.  |
| [`quantized_max_pool2d`](https://docs.pytorch.org/docs/stable/generated/torch.quantized_max_pool2d.html#torch.quantized_max_pool2d "torch.quantized_max_pool2d")  | Applies a 2D max pooling over an input quantized tensor composed of several input planes.  |
| [`rad2deg`](https://docs.pytorch.org/docs/stable/generated/torch.rad2deg.html#torch.rad2deg "torch.rad2deg")  | Returns a new tensor with each of the elements of `input` converted from angles in radians to degrees.  |
| [`real`](https://docs.pytorch.org/docs/stable/generated/torch.real.html#torch.real "torch.real")  | Returns a new tensor containing real values of the `self` tensor.  |
| [`reciprocal`](https://docs.pytorch.org/docs/stable/generated/torch.reciprocal.html#torch.reciprocal "torch.reciprocal")  | Returns a new tensor with the reciprocal of the elements of `input`  |
| [`remainder`](https://docs.pytorch.org/docs/stable/generated/torch.remainder.html#torch.remainder "torch.remainder")  | Computes [Python's modulus operation](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations) entrywise.  |
| [`round`](https://docs.pytorch.org/docs/stable/generated/torch.round.html#torch.round "torch.round")  | Rounds elements of `input` to the nearest integer.  |
| [`rsqrt`](https://docs.pytorch.org/docs/stable/generated/torch.rsqrt.html#torch.rsqrt "torch.rsqrt")  | Returns a new tensor with the reciprocal of the square-root of each of the elements of `input`.  |
| [`sigmoid`](https://docs.pytorch.org/docs/stable/generated/torch.sigmoid.html#torch.sigmoid "torch.sigmoid")  | Alias for [`torch.special.expit()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.expit "torch.special.expit").  |
| [`sign`](https://docs.pytorch.org/docs/stable/generated/torch.sign.html#torch.sign "torch.sign")  | Returns a new tensor with the signs of the elements of `input`.  |
| [`sgn`](https://docs.pytorch.org/docs/stable/generated/torch.sgn.html#torch.sgn "torch.sgn")  | This function is an extension of torch.sign() to complex tensors.  |
| [`signbit`](https://docs.pytorch.org/docs/stable/generated/torch.signbit.html#torch.signbit "torch.signbit")  | Tests if each element of `input` has its sign bit set or not.  |
| [`sin`](https://docs.pytorch.org/docs/stable/generated/torch.sin.html#torch.sin "torch.sin")  | Returns a new tensor with the sine of the elements in the `input` tensor, where each value in this input tensor is in radians.  |
| [`sinc`](https://docs.pytorch.org/docs/stable/generated/torch.sinc.html#torch.sinc "torch.sinc")  | Alias for [`torch.special.sinc()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.sinc "torch.special.sinc").  |
| [`sinh`](https://docs.pytorch.org/docs/stable/generated/torch.sinh.html#torch.sinh "torch.sinh")  | Returns a new tensor with the hyperbolic sine of the elements of `input`.  |
| [`softmax`](https://docs.pytorch.org/docs/stable/generated/torch.softmax.html#torch.softmax "torch.softmax")  | Alias for [`torch.nn.functional.softmax()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html#torch.nn.functional.softmax "torch.nn.functional.softmax").  |
| [`sqrt`](https://docs.pytorch.org/docs/stable/generated/torch.sqrt.html#torch.sqrt "torch.sqrt")  | Returns a new tensor with the square-root of the elements of `input`.  |
| [`square`](https://docs.pytorch.org/docs/stable/generated/torch.square.html#torch.square "torch.square")  | Returns a new tensor with the square of the elements of `input`.  |
| [`sub`](https://docs.pytorch.org/docs/stable/generated/torch.sub.html#torch.sub "torch.sub")  | Subtracts `other`, scaled by `alpha`, from `input`.  |
| [`subtract`](https://docs.pytorch.org/docs/stable/generated/torch.subtract.html#torch.subtract "torch.subtract")  | Alias for [`torch.sub()`](https://docs.pytorch.org/docs/stable/generated/torch.sub.html#torch.sub "torch.sub").  |
| [`tan`](https://docs.pytorch.org/docs/stable/generated/torch.tan.html#torch.tan "torch.tan")  | Returns a new tensor with the tangent of the elements in the `input` tensor, where each value in this input tensor is in radians.  |
| [`tanh`](https://docs.pytorch.org/docs/stable/generated/torch.tanh.html#torch.tanh "torch.tanh")  | Returns a new tensor with the hyperbolic tangent of the elements of `input`.  |
| [`true_divide`](https://docs.pytorch.org/docs/stable/generated/torch.true_divide.html#torch.true_divide "torch.true_divide")  | Alias for [`torch.div()`](https://docs.pytorch.org/docs/stable/generated/torch.div.html#torch.div "torch.div") with `rounding_mode=None`.  |
| [`trunc`](https://docs.pytorch.org/docs/stable/generated/torch.trunc.html#torch.trunc "torch.trunc")  | Returns a new tensor with the truncated integer values of the elements of `input`.  |
| [`xlogy`](https://docs.pytorch.org/docs/stable/generated/torch.xlogy.html#torch.xlogy "torch.xlogy")  | Alias for [`torch.special.xlogy()`](https://docs.pytorch.org/docs/stable/special.html#torch.special.xlogy "torch.special.xlogy").  |
### Reduction Ops[#](https://docs.pytorch.org/docs/stable/torch.html#reduction-ops "Link to this heading")
| [`argmax`](https://docs.pytorch.org/docs/stable/generated/torch.argmax.html#torch.argmax "torch.argmax")  | Returns the indices of the maximum value of all elements in the `input` tensor.  |
| --- | --- |
| [`argmin`](https://docs.pytorch.org/docs/stable/generated/torch.argmin.html#torch.argmin "torch.argmin")  | Returns the indices of the minimum value(s) of the flattened tensor or along a dimension  |
| [`amax`](https://docs.pytorch.org/docs/stable/generated/torch.amax.html#torch.amax "torch.amax")  | Returns the maximum value of each slice of the `input` tensor in the given dimension(s) `dim`.  |
| [`amin`](https://docs.pytorch.org/docs/stable/generated/torch.amin.html#torch.amin "torch.amin")  | Returns the minimum value of each slice of the `input` tensor in the given dimension(s) `dim`.  |
| [`aminmax`](https://docs.pytorch.org/docs/stable/generated/torch.aminmax.html#torch.aminmax "torch.aminmax")  | Computes the minimum and maximum values of the `input` tensor.  |
| [`all`](https://docs.pytorch.org/docs/stable/generated/torch.all.html#torch.all "torch.all")  | Tests if all elements in `input` evaluate to True.  |
| [`any`](https://docs.pytorch.org/docs/stable/generated/torch.any.html#torch.any "torch.any")  | Tests if any element in `input` evaluates to True.  |
| [`max`](https://docs.pytorch.org/docs/stable/generated/torch.max.html#torch.max "torch.max")  | Returns the maximum value of all elements in the `input` tensor.  |
| [`min`](https://docs.pytorch.org/docs/stable/generated/torch.min.html#torch.min "torch.min")  | Returns the minimum value of all elements in the `input` tensor.  |
| [`dist`](https://docs.pytorch.org/docs/stable/generated/torch.dist.html#torch.dist "torch.dist")  | Returns the p-norm of (`input` - `other`)  |
| [`logsumexp`](https://docs.pytorch.org/docs/stable/generated/torch.logsumexp.html#torch.logsumexp "torch.logsumexp")  | Returns the log of summed exponentials of each row of the `input` tensor in the given dimension `dim`.  |
| [`mean`](https://docs.pytorch.org/docs/stable/generated/torch.mean.html#torch.mean "torch.mean")  |   |
| [`nanmean`](https://docs.pytorch.org/docs/stable/generated/torch.nanmean.html#torch.nanmean "torch.nanmean")  | Computes the mean of all non-NaN elements along the specified dimensions.  |
| [`median`](https://docs.pytorch.org/docs/stable/generated/torch.median.html#torch.median "torch.median")  | Returns the median of the values in `input`.  |
| [`nanmedian`](https://docs.pytorch.org/docs/stable/generated/torch.nanmedian.html#torch.nanmedian "torch.nanmedian")  | Returns the median of the values in `input`, ignoring `NaN` values.  |
| [`mode`](https://docs.pytorch.org/docs/stable/generated/torch.mode.html#torch.mode "torch.mode")  | Returns a namedtuple `(values, indices)` where `values` is the mode value of each row of the `input` tensor in the given dimension `dim`, i.e. a value which appears most often in that row, and `indices` is the index location of each mode value found.  |
| [`norm`](https://docs.pytorch.org/docs/stable/generated/torch.norm.html#torch.norm "torch.norm")  | Returns the matrix norm or vector norm of a given tensor.  |
| [`nansum`](https://docs.pytorch.org/docs/stable/generated/torch.nansum.html#torch.nansum "torch.nansum")  | Returns the sum of all elements, treating Not a Numbers (NaNs) as zero.  |
| [`prod`](https://docs.pytorch.org/docs/stable/generated/torch.prod.html#torch.prod "torch.prod")  | Returns the product of all elements in the `input` tensor.  |
| [`quantile`](https://docs.pytorch.org/docs/stable/generated/torch.quantile.html#torch.quantile "torch.quantile")  | Computes the q-th quantiles of each row of the `input` tensor along the dimension `dim`.  |
| [`nanquantile`](https://docs.pytorch.org/docs/stable/generated/torch.nanquantile.html#torch.nanquantile "torch.nanquantile")  | This is a variant of [`torch.quantile()`](https://docs.pytorch.org/docs/stable/generated/torch.quantile.html#torch.quantile "torch.quantile") that "ignores" `NaN` values, computing the quantiles `q` as if `NaN` values in `input` did not exist.  |
| [`std`](https://docs.pytorch.org/docs/stable/generated/torch.std.html#torch.std "torch.std")  | Calculates the standard deviation over the dimensions specified by `dim`.  |
| [`std_mean`](https://docs.pytorch.org/docs/stable/generated/torch.std_mean.html#torch.std_mean "torch.std_mean")  | Calculates the standard deviation and mean over the dimensions specified by `dim`.  |
| [`sum`](https://docs.pytorch.org/docs/stable/generated/torch.sum.html#torch.sum "torch.sum")  | Returns the sum of all elements in the `input` tensor.  |
| [`unique`](https://docs.pytorch.org/docs/stable/generated/torch.unique.html#torch.unique "torch.unique")  | Returns the unique elements of the input tensor.  |
| [`unique_consecutive`](https://docs.pytorch.org/docs/stable/generated/torch.unique_consecutive.html#torch.unique_consecutive "torch.unique_consecutive")  | Eliminates all but the first element from every consecutive group of equivalent elements.  |
| [`var`](https://docs.pytorch.org/docs/stable/generated/torch.var.html#torch.var "torch.var")  | Calculates the variance over the dimensions specified by `dim`.  |
| [`var_mean`](https://docs.pytorch.org/docs/stable/generated/torch.var_mean.html#torch.var_mean "torch.var_mean")  | Calculates the variance and mean over the dimensions specified by `dim`.  |
| [`count_nonzero`](https://docs.pytorch.org/docs/stable/generated/torch.count_nonzero.html#torch.count_nonzero "torch.count_nonzero")  | Counts the number of non-zero values in the tensor `input` along the given `dim`.  |
| [`hash_tensor`](https://docs.pytorch.org/docs/stable/generated/torch.hash_tensor.html#torch.hash_tensor "torch.hash_tensor")  | Returns a hash of all elements in the `input` tensor.  |
### Comparison Ops[#](https://docs.pytorch.org/docs/stable/torch.html#comparison-ops "Link to this heading")
| [`allclose`](https://docs.pytorch.org/docs/stable/generated/torch.allclose.html#torch.allclose "torch.allclose")  | This function checks if `input` and `other` satisfy the condition:  |
| --- | --- |
| [`argsort`](https://docs.pytorch.org/docs/stable/generated/torch.argsort.html#torch.argsort "torch.argsort")  | Returns the indices that sort a tensor along a given dimension in ascending order by value.  |
| [`eq`](https://docs.pytorch.org/docs/stable/generated/torch.eq.html#torch.eq "torch.eq")  | Computes element-wise equality  |
| [`equal`](https://docs.pytorch.org/docs/stable/generated/torch.equal.html#torch.equal "torch.equal")  | `True` if two tensors have the same size and elements, `False` otherwise.  |
| [`ge`](https://docs.pytorch.org/docs/stable/generated/torch.ge.html#torch.ge "torch.ge")  | Computes input≥other\text{input} \geq \text{other}input≥other element-wise.  |
| [`greater_equal`](https://docs.pytorch.org/docs/stable/generated/torch.greater_equal.html#torch.greater_equal "torch.greater_equal")  | Alias for [`torch.ge()`](https://docs.pytorch.org/docs/stable/generated/torch.ge.html#torch.ge "torch.ge").  |
| [`gt`](https://docs.pytorch.org/docs/stable/generated/torch.gt.html#torch.gt "torch.gt")  | Computes input>other\text{input} > \text{other}input>other element-wise.  |
| [`greater`](https://docs.pytorch.org/docs/stable/generated/torch.greater.html#torch.greater "torch.greater")  | Alias for [`torch.gt()`](https://docs.pytorch.org/docs/stable/generated/torch.gt.html#torch.gt "torch.gt").  |
| [`isclose`](https://docs.pytorch.org/docs/stable/generated/torch.isclose.html#torch.isclose "torch.isclose")  | Returns a new tensor with boolean elements representing if each element of `input` is "close" to the corresponding element of `other`.  |
| [`isfinite`](https://docs.pytorch.org/docs/stable/generated/torch.isfinite.html#torch.isfinite "torch.isfinite")  | Returns a new tensor with boolean elements representing if each element is finite or not.  |
| [`isin`](https://docs.pytorch.org/docs/stable/generated/torch.isin.html#torch.isin "torch.isin")  | Tests if each element of `elements` is in `test_elements`.  |
| [`isinf`](https://docs.pytorch.org/docs/stable/generated/torch.isinf.html#torch.isinf "torch.isinf")  | Tests if each element of `input` is infinite (positive or negative infinity) or not.  |
| [`isposinf`](https://docs.pytorch.org/docs/stable/generated/torch.isposinf.html#torch.isposinf "torch.isposinf")  | Tests if each element of `input` is positive infinity or not.  |
| [`isneginf`](https://docs.pytorch.org/docs/stable/generated/torch.isneginf.html#torch.isneginf "torch.isneginf")  | Tests if each element of `input` is negative infinity or not.  |
| [`isnan`](https://docs.pytorch.org/docs/stable/generated/torch.isnan.html#torch.isnan "torch.isnan")  | Returns a new tensor with boolean elements representing if each element of `input` is NaN or not.  |
| [`isreal`](https://docs.pytorch.org/docs/stable/generated/torch.isreal.html#torch.isreal "torch.isreal")  | Returns a new tensor with boolean elements representing if each element of `input` is real-valued or not.  |
| [`kthvalue`](https://docs.pytorch.org/docs/stable/generated/torch.kthvalue.html#torch.kthvalue "torch.kthvalue")  | Returns a namedtuple `(values, indices)` where `values` is the `k` th smallest element of each row of the `input` tensor in the given dimension `dim`.  |
| [`le`](https://docs.pytorch.org/docs/stable/generated/torch.le.html#torch.le "torch.le")  | Computes input≤other\text{input} \leq \text{other}input≤other element-wise.  |
| [`less_equal`](https://docs.pytorch.org/docs/stable/generated/torch.less_equal.html#torch.less_equal "torch.less_equal")  | Alias for [`torch.le()`](https://docs.pytorch.org/docs/stable/generated/torch.le.html#torch.le "torch.le").  |
| [`lt`](https://docs.pytorch.org/docs/stable/generated/torch.lt.html#torch.lt "torch.lt")  | Computes input<other\text{input} < \text{other}input<other element-wise.  |
| [`less`](https://docs.pytorch.org/docs/stable/generated/torch.less.html#torch.less "torch.less")  | Alias for [`torch.lt()`](https://docs.pytorch.org/docs/stable/generated/torch.lt.html#torch.lt "torch.lt").  |
| [`maximum`](https://docs.pytorch.org/docs/stable/generated/torch.maximum.html#torch.maximum "torch.maximum")  | Computes the element-wise maximum of `input` and `other`.  |
| [`minimum`](https://docs.pytorch.org/docs/stable/generated/torch.minimum.html#torch.minimum "torch.minimum")  | Computes the element-wise minimum of `input` and `other`.  |
| [`fmax`](https://docs.pytorch.org/docs/stable/generated/torch.fmax.html#torch.fmax "torch.fmax")  | Computes the element-wise maximum of `input` and `other`.  |
| [`fmin`](https://docs.pytorch.org/docs/stable/generated/torch.fmin.html#torch.fmin "torch.fmin")  | Computes the element-wise minimum of `input` and `other`.  |
| [`ne`](https://docs.pytorch.org/docs/stable/generated/torch.ne.html#torch.ne "torch.ne")  | Computes input≠other\text{input} \neq \text{other}input=other element-wise.  |
| [`not_equal`](https://docs.pytorch.org/docs/stable/generated/torch.not_equal.html#torch.not_equal "torch.not_equal")  | Alias for [`torch.ne()`](https://docs.pytorch.org/docs/stable/generated/torch.ne.html#torch.ne "torch.ne").  |
| [`sort`](https://docs.pytorch.org/docs/stable/generated/torch.sort.html#torch.sort "torch.sort")  | Sorts the elements of the `input` tensor along a given dimension in ascending order by value.  |
| [`topk`](https://docs.pytorch.org/docs/stable/generated/torch.topk.html#torch.topk "torch.topk")  | Returns the `k` largest elements of the given `input` tensor along a given dimension.  |
| [`msort`](https://docs.pytorch.org/docs/stable/generated/torch.msort.html#torch.msort "torch.msort")  | Sorts the elements of the `input` tensor along its first dimension in ascending order by value.  |
### Spectral Ops[#](https://docs.pytorch.org/docs/stable/torch.html#spectral-ops "Link to this heading")
| [`stft`](https://docs.pytorch.org/docs/stable/generated/torch.stft.html#torch.stft "torch.stft")  | Short-time Fourier transform (STFT).  |
| --- | --- |
| [`istft`](https://docs.pytorch.org/docs/stable/generated/torch.istft.html#torch.istft "torch.istft")  | Inverse short time Fourier Transform.  |
| [`bartlett_window`](https://docs.pytorch.org/docs/stable/generated/torch.bartlett_window.html#torch.bartlett_window "torch.bartlett_window")  | Bartlett window function.  |
| [`blackman_window`](https://docs.pytorch.org/docs/stable/generated/torch.blackman_window.html#torch.blackman_window "torch.blackman_window")  | Blackman window function.  |
| [`hamming_window`](https://docs.pytorch.org/docs/stable/generated/torch.hamming_window.html#torch.hamming_window "torch.hamming_window")  | Hamming window function.  |
| [`hann_window`](https://docs.pytorch.org/docs/stable/generated/torch.hann_window.html#torch.hann_window "torch.hann_window")  | Hann window function.  |
| [`kaiser_window`](https://docs.pytorch.org/docs/stable/generated/torch.kaiser_window.html#torch.kaiser_window "torch.kaiser_window")  | Computes the Kaiser window with window length `window_length` and shape parameter `beta`.  |
### Other Operations[#](https://docs.pytorch.org/docs/stable/torch.html#other-operations "Link to this heading")
| [`atleast_1d`](https://docs.pytorch.org/docs/stable/generated/torch.atleast_1d.html#torch.atleast_1d "torch.atleast_1d")  | Returns a 1-dimensional view of each input tensor with zero dimensions.  |
| --- | --- |
| [`atleast_2d`](https://docs.pytorch.org/docs/stable/generated/torch.atleast_2d.html#torch.atleast_2d "torch.atleast_2d")  | Returns a 2-dimensional view of each input tensor with zero dimensions.  |
| [`atleast_3d`](https://docs.pytorch.org/docs/stable/generated/torch.atleast_3d.html#torch.atleast_3d "torch.atleast_3d")  | Returns a 3-dimensional view of each input tensor with zero dimensions.  |
| [`bincount`](https://docs.pytorch.org/docs/stable/generated/torch.bincount.html#torch.bincount "torch.bincount")  | Count the frequency of each value in an array of non-negative ints.  |
| [`block_diag`](https://docs.pytorch.org/docs/stable/generated/torch.block_diag.html#torch.block_diag "torch.block_diag")  | Create a block diagonal matrix from provided tensors.  |
| [`broadcast_tensors`](https://docs.pytorch.org/docs/stable/generated/torch.broadcast_tensors.html#torch.broadcast_tensors "torch.broadcast_tensors")  | Broadcasts the given tensors according to [Broadcasting semantics](https://docs.pytorch.org/docs/stable/notes/broadcasting.html#broadcasting-semantics).  |
| [`broadcast_to`](https://docs.pytorch.org/docs/stable/generated/torch.broadcast_to.html#torch.broadcast_to "torch.broadcast_to")  | Broadcasts `input` to the shape `shape`.  |
| [`broadcast_shapes`](https://docs.pytorch.org/docs/stable/generated/torch.broadcast_shapes.html#torch.broadcast_shapes "torch.broadcast_shapes")  | Similar to [`broadcast_tensors()`](https://docs.pytorch.org/docs/stable/generated/torch.broadcast_tensors.html#torch.broadcast_tensors "torch.broadcast_tensors") but for shapes.  |
| [`bucketize`](https://docs.pytorch.org/docs/stable/generated/torch.bucketize.html#torch.bucketize "torch.bucketize")  | Returns the indices of the buckets to which each value in the `input` belongs, where the boundaries of the buckets are set by `boundaries`.  |
| [`cartesian_prod`](https://docs.pytorch.org/docs/stable/generated/torch.cartesian_prod.html#torch.cartesian_prod "torch.cartesian_prod")  | Do cartesian product of the given sequence of tensors.  |
| [`cdist`](https://docs.pytorch.org/docs/stable/generated/torch.cdist.html#torch.cdist "torch.cdist")  | Computes batched the p-norm distance between each pair of the two collections of row vectors.  |
| [`clone`](https://docs.pytorch.org/docs/stable/generated/torch.clone.html#torch.clone "torch.clone")  | Returns a copy of `input`.  |
| [`combinations`](https://docs.pytorch.org/docs/stable/generated/torch.combinations.html#torch.combinations "torch.combinations")  | Compute combinations of length rrr of the given tensor.  |
| [`corrcoef`](https://docs.pytorch.org/docs/stable/generated/torch.corrcoef.html#torch.corrcoef "torch.corrcoef")  | Estimates the Pearson product-moment correlation coefficient matrix of the variables given by the `input` matrix, where rows are the variables and columns are the observations.  |
| [`cov`](https://docs.pytorch.org/docs/stable/generated/torch.cov.html#torch.cov "torch.cov")  | Estimates the covariance matrix of the variables given by the `input` matrix, where rows are the variables and columns are the observations.  |
| [`cross`](https://docs.pytorch.org/docs/stable/generated/torch.cross.html#torch.cross "torch.cross")  | Returns the cross product of vectors in dimension `dim` of `input` and `other`.  |
| [`cummax`](https://docs.pytorch.org/docs/stable/generated/torch.cummax.html#torch.cummax "torch.cummax")  | Returns a namedtuple `(values, indices)` where `values` is the cumulative maximum of elements of `input` in the dimension `dim`.  |
| [`cummin`](https://docs.pytorch.org/docs/stable/generated/torch.cummin.html#torch.cummin "torch.cummin")  | Returns a namedtuple `(values, indices)` where `values` is the cumulative minimum of elements of `input` in the dimension `dim`.  |
| [`cumprod`](https://docs.pytorch.org/docs/stable/generated/torch.cumprod.html#torch.cumprod "torch.cumprod")  | Returns the cumulative product of elements of `input` in the dimension `dim`.  |
| [`cumsum`](https://docs.pytorch.org/docs/stable/generated/torch.cumsum.html#torch.cumsum "torch.cumsum")  | Returns the cumulative sum of elements of `input` in the dimension `dim`.  |
| [`diag`](https://docs.pytorch.org/docs/stable/generated/torch.diag.html#torch.diag "torch.diag")  |
  * If `input` is a vector (1-D tensor), then returns a 2-D square tensor

 |
| [`diag_embed`](https://docs.pytorch.org/docs/stable/generated/torch.diag_embed.html#torch.diag_embed "torch.diag_embed")  | Creates a tensor whose diagonals of certain 2D planes (specified by `dim1` and `dim2`) are filled by `input`.  |
| [`diagflat`](https://docs.pytorch.org/docs/stable/generated/torch.diagflat.html#torch.diagflat "torch.diagflat")  |
  * If `input` is a vector (1-D tensor), then returns a 2-D square tensor

 |
| [`diagonal`](https://docs.pytorch.org/docs/stable/generated/torch.diagonal.html#torch.diagonal "torch.diagonal")  | Returns a partial view of `input` with the its diagonal elements with respect to `dim1` and `dim2` appended as a dimension at the end of the shape.  |
| [`diff`](https://docs.pytorch.org/docs/stable/generated/torch.diff.html#torch.diff "torch.diff")  | Computes the n-th forward difference along the given dimension.  |
| [`einsum`](https://docs.pytorch.org/docs/stable/generated/torch.einsum.html#torch.einsum "torch.einsum")  | Sums the product of the elements of the input `operands` along dimensions specified using a notation based on the Einstein summation convention.  |
| [`flatten`](https://docs.pytorch.org/docs/stable/generated/torch.flatten.html#torch.flatten "torch.flatten")  | Flattens `input` by reshaping it into a one-dimensional tensor.  |
| [`flip`](https://docs.pytorch.org/docs/stable/generated/torch.flip.html#torch.flip "torch.flip")  | Reverse the order of an n-D tensor along given axis in dims.  |
| [`fliplr`](https://docs.pytorch.org/docs/stable/generated/torch.fliplr.html#torch.fliplr "torch.fliplr")  | Flip tensor in the left/right direction, returning a new tensor.  |
| [`flipud`](https://docs.pytorch.org/docs/stable/generated/torch.flipud.html#torch.flipud "torch.flipud")  | Flip tensor in the up/down direction, returning a new tensor.  |
| [`kron`](https://docs.pytorch.org/docs/stable/generated/torch.kron.html#torch.kron "torch.kron")  | Computes the Kronecker product, denoted by ⊗\otimes⊗, of `input` and `other`.  |
| [`rot90`](https://docs.pytorch.org/docs/stable/generated/torch.rot90.html#torch.rot90 "torch.rot90")  | Rotate an n-D tensor by 90 degrees in the plane specified by dims axis.  |
| [`gcd`](https://docs.pytorch.org/docs/stable/generated/torch.gcd.html#torch.gcd "torch.gcd")  | Computes the element-wise greatest common divisor (GCD) of `input` and `other`.  |
| [`histc`](https://docs.pytorch.org/docs/stable/generated/torch.histc.html#torch.histc "torch.histc")  | Computes the histogram of a tensor.  |
| [`histogram`](https://docs.pytorch.org/docs/stable/generated/torch.histogram.html#torch.histogram "torch.histogram")  | Computes a histogram of the values in a tensor.  |
| [`histogramdd`](https://docs.pytorch.org/docs/stable/generated/torch.histogramdd.html#torch.histogramdd "torch.histogramdd")  | Computes a multi-dimensional histogram of the values in a tensor.  |
| [`meshgrid`](https://docs.pytorch.org/docs/stable/generated/torch.meshgrid.html#torch.meshgrid "torch.meshgrid")  | Creates grids of coordinates specified by the 1D inputs in attr:tensors.  |
| [`lcm`](https://docs.pytorch.org/docs/stable/generated/torch.lcm.html#torch.lcm "torch.lcm")  | Computes the element-wise least common multiple (LCM) of `input` and `other`.  |
| [`logcumsumexp`](https://docs.pytorch.org/docs/stable/generated/torch.logcumsumexp.html#torch.logcumsumexp "torch.logcumsumexp")  | Returns the logarithm of the cumulative summation of the exponentiation of elements of `input` in the dimension `dim`.  |
| [`ravel`](https://docs.pytorch.org/docs/stable/generated/torch.ravel.html#torch.ravel "torch.ravel")  | Return a contiguous flattened tensor.  |
| [`renorm`](https://docs.pytorch.org/docs/stable/generated/torch.renorm.html#torch.renorm "torch.renorm")  | Returns a tensor where each sub-tensor of `input` along dimension `dim` is normalized such that the p-norm of the sub-tensor is lower than the value `maxnorm`  |
| [`repeat_interleave`](https://docs.pytorch.org/docs/stable/generated/torch.repeat_interleave.html#torch.repeat_interleave "torch.repeat_interleave")  | Repeat elements of a tensor.  |
| [`roll`](https://docs.pytorch.org/docs/stable/generated/torch.roll.html#torch.roll "torch.roll")  | Roll the tensor `input` along the given dimension(s).  |
| [`searchsorted`](https://docs.pytorch.org/docs/stable/generated/torch.searchsorted.html#torch.searchsorted "torch.searchsorted")  | Find the indices from the _innermost_ dimension of `sorted_sequence` such that, if the corresponding values in `values` were inserted before the indices, when sorted, the order of the corresponding _innermost_ dimension within `sorted_sequence` would be preserved.  |
| [`tensordot`](https://docs.pytorch.org/docs/stable/generated/torch.tensordot.html#torch.tensordot "torch.tensordot")  | Returns a contraction of a and b over multiple dimensions.  |
| [`trace`](https://docs.pytorch.org/docs/stable/generated/torch.trace.html#torch.trace "torch.trace")  | Returns the sum of the elements of the diagonal of the input 2-D matrix.  |
| [`tril`](https://docs.pytorch.org/docs/stable/generated/torch.tril.html#torch.tril "torch.tril")  | Returns the lower triangular part of the matrix (2-D tensor) or batch of matrices `input`, the other elements of the result tensor `out` are set to 0.  |
| [`tril_indices`](https://docs.pytorch.org/docs/stable/generated/torch.tril_indices.html#torch.tril_indices "torch.tril_indices")  | Returns the indices of the lower triangular part of a `row`-by- `col` matrix in a 2-by-N Tensor, where the first row contains row coordinates of all indices and the second row contains column coordinates.  |
| [`triu`](https://docs.pytorch.org/docs/stable/generated/torch.triu.html#torch.triu "torch.triu")  | Returns the upper triangular part of a matrix (2-D tensor) or batch of matrices `input`, the other elements of the result tensor `out` are set to 0.  |
| [`triu_indices`](https://docs.pytorch.org/docs/stable/generated/torch.triu_indices.html#torch.triu_indices "torch.triu_indices")  | Returns the indices of the upper triangular part of a `row` by `col` matrix in a 2-by-N Tensor, where the first row contains row coordinates of all indices and the second row contains column coordinates.  |
| [`unflatten`](https://docs.pytorch.org/docs/stable/generated/torch.unflatten.html#torch.unflatten "torch.unflatten")  | Expands a dimension of the input tensor over multiple dimensions.  |
| [`vander`](https://docs.pytorch.org/docs/stable/generated/torch.vander.html#torch.vander "torch.vander")  | Generates a Vandermonde matrix.  |
| [`view_as_real`](https://docs.pytorch.org/docs/stable/generated/torch.view_as_real.html#torch.view_as_real "torch.view_as_real")  | Returns a view of `input` as a real tensor.  |
| [`view_as_complex`](https://docs.pytorch.org/docs/stable/generated/torch.view_as_complex.html#torch.view_as_complex "torch.view_as_complex")  | Returns a view of `input` as a complex tensor.  |
| [`resolve_conj`](https://docs.pytorch.org/docs/stable/generated/torch.resolve_conj.html#torch.resolve_conj "torch.resolve_conj")  | Returns a new tensor with materialized conjugation if `input`'s conjugate bit is set to True, else returns `input`.  |
| [`resolve_neg`](https://docs.pytorch.org/docs/stable/generated/torch.resolve_neg.html#torch.resolve_neg "torch.resolve_neg")  | Returns a new tensor with materialized negation if `input`'s negative bit is set to True, else returns `input`.  |
### BLAS and LAPACK Operations[#](https://docs.pytorch.org/docs/stable/torch.html#blas-and-lapack-operations "Link to this heading")
| [`addbmm`](https://docs.pytorch.org/docs/stable/generated/torch.addbmm.html#torch.addbmm "torch.addbmm")  | Performs a batch matrix-matrix product of matrices stored in `batch1` and `batch2`, with a reduced add step (all matrix multiplications get accumulated along the first dimension).  |
| --- | --- |
| [`addmm`](https://docs.pytorch.org/docs/stable/generated/torch.addmm.html#torch.addmm "torch.addmm")  | Performs a matrix multiplication of the matrices `mat1` and `mat2`.  |
| [`addmv`](https://docs.pytorch.org/docs/stable/generated/torch.addmv.html#torch.addmv "torch.addmv")  | Performs a matrix-vector product of the matrix `mat` and the vector `vec`.  |
| [`addr`](https://docs.pytorch.org/docs/stable/generated/torch.addr.html#torch.addr "torch.addr")  | Performs the outer-product of vectors `vec1` and `vec2` and adds it to the matrix `input`.  |
| [`baddbmm`](https://docs.pytorch.org/docs/stable/generated/torch.baddbmm.html#torch.baddbmm "torch.baddbmm")  | Performs a batch matrix-matrix product of matrices in `batch1` and `batch2`.  |
| [`bmm`](https://docs.pytorch.org/docs/stable/generated/torch.bmm.html#torch.bmm "torch.bmm")  | Performs a batch matrix-matrix product of matrices stored in `input` and `mat2`.  |
| [`chain_matmul`](https://docs.pytorch.org/docs/stable/generated/torch.chain_matmul.html#torch.chain_matmul "torch.chain_matmul")  | Returns the matrix product of the NNN 2-D tensors.  |
| [`cholesky`](https://docs.pytorch.org/docs/stable/generated/torch.cholesky.html#torch.cholesky "torch.cholesky")  | Computes the Cholesky decomposition of a symmetric positive-definite matrix AAA or for batches of symmetric positive-definite matrices.  |
| [`cholesky_inverse`](https://docs.pytorch.org/docs/stable/generated/torch.cholesky_inverse.html#torch.cholesky_inverse "torch.cholesky_inverse")  | Computes the inverse of a complex Hermitian or real symmetric positive-definite matrix given its Cholesky decomposition.  |
| [`cholesky_solve`](https://docs.pytorch.org/docs/stable/generated/torch.cholesky_solve.html#torch.cholesky_solve "torch.cholesky_solve")  | Computes the solution of a system of linear equations with complex Hermitian or real symmetric positive-definite lhs given its Cholesky decomposition.  |
| [`dot`](https://docs.pytorch.org/docs/stable/generated/torch.dot.html#torch.dot "torch.dot")  | Computes the dot product of two 1D tensors.  |
| [`geqrf`](https://docs.pytorch.org/docs/stable/generated/torch.geqrf.html#torch.geqrf "torch.geqrf")  | This is a low-level function for calling LAPACK's geqrf directly.  |
| [`ger`](https://docs.pytorch.org/docs/stable/generated/torch.ger.html#torch.ger "torch.ger")  | Alias of [`torch.outer()`](https://docs.pytorch.org/docs/stable/generated/torch.outer.html#torch.outer "torch.outer").  |
| [`inner`](https://docs.pytorch.org/docs/stable/generated/torch.inner.html#torch.inner "torch.inner")  | Computes the dot product for 1D tensors.  |
| [`inverse`](https://docs.pytorch.org/docs/stable/generated/torch.inverse.html#torch.inverse "torch.inverse")  | Alias for [`torch.linalg.inv()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.inv.html#torch.linalg.inv "torch.linalg.inv")  |
| [`det`](https://docs.pytorch.org/docs/stable/generated/torch.det.html#torch.det "torch.det")  | Alias for [`torch.linalg.det()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.det.html#torch.linalg.det "torch.linalg.det")  |
| [`logdet`](https://docs.pytorch.org/docs/stable/generated/torch.logdet.html#torch.logdet "torch.logdet")  | Calculates log determinant of a square matrix or batches of square matrices.  |
| [`slogdet`](https://docs.pytorch.org/docs/stable/generated/torch.slogdet.html#torch.slogdet "torch.slogdet")  | Alias for [`torch.linalg.slogdet()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.slogdet.html#torch.linalg.slogdet "torch.linalg.slogdet")  |
| [`lu`](https://docs.pytorch.org/docs/stable/generated/torch.lu.html#torch.lu "torch.lu")  | Computes the LU factorization of a matrix or batches of matrices `A`.  |
| [`lu_solve`](https://docs.pytorch.org/docs/stable/generated/torch.lu_solve.html#torch.lu_solve "torch.lu_solve")  | Returns the LU solve of the linear system Ax=bAx = bAx=b using the partially pivoted LU factorization of A from [`lu_factor()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.lu_factor.html#torch.linalg.lu_factor "torch.linalg.lu_factor").  |
| [`lu_unpack`](https://docs.pytorch.org/docs/stable/generated/torch.lu_unpack.html#torch.lu_unpack "torch.lu_unpack")  | Unpacks the LU decomposition returned by [`lu_factor()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.lu_factor.html#torch.linalg.lu_factor "torch.linalg.lu_factor") into the P, L, U matrices.  |
| [`matmul`](https://docs.pytorch.org/docs/stable/generated/torch.matmul.html#torch.matmul "torch.matmul")  | Matrix product of two tensors.  |
| [`matrix_power`](https://docs.pytorch.org/docs/stable/generated/torch.matrix_power.html#torch.matrix_power "torch.matrix_power")  | Alias for [`torch.linalg.matrix_power()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.matrix_power.html#torch.linalg.matrix_power "torch.linalg.matrix_power")  |
| [`matrix_exp`](https://docs.pytorch.org/docs/stable/generated/torch.matrix_exp.html#torch.matrix_exp "torch.matrix_exp")  | Alias for [`torch.linalg.matrix_exp()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.matrix_exp.html#torch.linalg.matrix_exp "torch.linalg.matrix_exp").  |
| [`mm`](https://docs.pytorch.org/docs/stable/generated/torch.mm.html#torch.mm "torch.mm")  | Performs a matrix multiplication of the matrices `input` and `mat2`.  |
| [`mv`](https://docs.pytorch.org/docs/stable/generated/torch.mv.html#torch.mv "torch.mv")  | Performs a matrix-vector product of the matrix `input` and the vector `vec`.  |
| [`orgqr`](https://docs.pytorch.org/docs/stable/generated/torch.orgqr.html#torch.orgqr "torch.orgqr")  | Alias for [`torch.linalg.householder_product()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.householder_product.html#torch.linalg.householder_product "torch.linalg.householder_product").  |
| [`ormqr`](https://docs.pytorch.org/docs/stable/generated/torch.ormqr.html#torch.ormqr "torch.ormqr")  | Computes the matrix-matrix multiplication of a product of Householder matrices with a general matrix.  |
| [`outer`](https://docs.pytorch.org/docs/stable/generated/torch.outer.html#torch.outer "torch.outer")  | Outer product of `input` and `vec2`.  |
| [`pinverse`](https://docs.pytorch.org/docs/stable/generated/torch.pinverse.html#torch.pinverse "torch.pinverse")  | Alias for [`torch.linalg.pinv()`](https://docs.pytorch.org/docs/stable/generated/torch.linalg.pinv.html#torch.linalg.pinv "torch.linalg.pinv")  |
| [`qr`](https://docs.pytorch.org/docs/stable/generated/torch.qr.html#torch.qr "torch.qr")  | Computes the QR decomposition of a matrix or a batch of matrices `input`, and returns a namedtuple (Q, R) of tensors such that input=QR\text{input} = Q Rinput=QR with QQQ being an orthogonal matrix or batch of orthogonal matrices and RRR being an upper triangular matrix or batch of upper triangular matrices.  |
| [`svd`](https://docs.pytorch.org/docs/stable/generated/torch.svd.html#torch.svd "torch.svd")  | Computes the singular value decomposition of either a matrix or batch of matrices `input`.  |
| [`svd_lowrank`](https://docs.pytorch.org/docs/stable/generated/torch.svd_lowrank.html#torch.svd_lowrank "torch.svd_lowrank")  | Return the singular value decomposition `(U, S, V)` of a matrix, batches of matrices, or a sparse matrix AAA such that A≈Udiag⁡(S)VHA \approx U \operatorname{diag}(S) V^{\text{H}}A≈Udiag(S)VH.  |
| [`pca_lowrank`](https://docs.pytorch.org/docs/stable/generated/torch.pca_lowrank.html#torch.pca_lowrank "torch.pca_lowrank")  | Performs linear Principal Component Analysis (PCA) on a low-rank matrix, batches of such matrices, or sparse matrix.  |
| [`lobpcg`](https://docs.pytorch.org/docs/stable/generated/torch.lobpcg.html#torch.lobpcg "torch.lobpcg")  | Find the k largest (or smallest) eigenvalues and the corresponding eigenvectors of a symmetric positive definite generalized eigenvalue problem using matrix-free LOBPCG methods.  |
| [`trapz`](https://docs.pytorch.org/docs/stable/generated/torch.trapz.html#torch.trapz "torch.trapz")  | Alias for [`torch.trapezoid()`](https://docs.pytorch.org/docs/stable/generated/torch.trapezoid.html#torch.trapezoid "torch.trapezoid").  |
| [`trapezoid`](https://docs.pytorch.org/docs/stable/generated/torch.trapezoid.html#torch.trapezoid "torch.trapezoid")  | Computes the [trapezoidal rule](https://en.wikipedia.org/wiki/Trapezoidal_rule) along `dim`.  |
| [`cumulative_trapezoid`](https://docs.pytorch.org/docs/stable/generated/torch.cumulative_trapezoid.html#torch.cumulative_trapezoid "torch.cumulative_trapezoid")  |  Cumulatively computes the [trapezoidal rule](https://en.wikipedia.org/wiki/Trapezoidal_rule) along `dim`.  |
| [`triangular_solve`](https://docs.pytorch.org/docs/stable/generated/torch.triangular_solve.html#torch.triangular_solve "torch.triangular_solve")  | Solves a system of equations with a square upper or lower triangular invertible matrix AAA and multiple right-hand sides bbb.  |
| [`vdot`](https://docs.pytorch.org/docs/stable/generated/torch.vdot.html#torch.vdot "torch.vdot")  | Computes the dot product of two 1D vectors along a dimension.  |
### Foreach Operations[#](https://docs.pytorch.org/docs/stable/torch.html#foreach-operations "Link to this heading")
Warning
This API is in beta and subject to future changes. Forward-mode AD is not supported.
| [`_foreach_abs`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_abs.html#torch._foreach_abs "torch._foreach_abs")  | Apply [`torch.abs()`](https://docs.pytorch.org/docs/stable/generated/torch.abs.html#torch.abs "torch.abs") to each Tensor of the input list.  |
| --- | --- |
| [`_foreach_abs_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_abs_.html#torch._foreach_abs_ "torch._foreach_abs_")  | Apply [`torch.abs()`](https://docs.pytorch.org/docs/stable/generated/torch.abs.html#torch.abs "torch.abs") to each Tensor of the input list.  |
| [`_foreach_acos`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_acos.html#torch._foreach_acos "torch._foreach_acos")  | Apply [`torch.acos()`](https://docs.pytorch.org/docs/stable/generated/torch.acos.html#torch.acos "torch.acos") to each Tensor of the input list.  |
| [`_foreach_acos_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_acos_.html#torch._foreach_acos_ "torch._foreach_acos_")  | Apply [`torch.acos()`](https://docs.pytorch.org/docs/stable/generated/torch.acos.html#torch.acos "torch.acos") to each Tensor of the input list.  |
| [`_foreach_asin`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_asin.html#torch._foreach_asin "torch._foreach_asin")  | Apply [`torch.asin()`](https://docs.pytorch.org/docs/stable/generated/torch.asin.html#torch.asin "torch.asin") to each Tensor of the input list.  |
| [`_foreach_asin_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_asin_.html#torch._foreach_asin_ "torch._foreach_asin_")  | Apply [`torch.asin()`](https://docs.pytorch.org/docs/stable/generated/torch.asin.html#torch.asin "torch.asin") to each Tensor of the input list.  |
| [`_foreach_atan`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_atan.html#torch._foreach_atan "torch._foreach_atan")  | Apply [`torch.atan()`](https://docs.pytorch.org/docs/stable/generated/torch.atan.html#torch.atan "torch.atan") to each Tensor of the input list.  |
| [`_foreach_atan_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_atan_.html#torch._foreach_atan_ "torch._foreach_atan_")  | Apply [`torch.atan()`](https://docs.pytorch.org/docs/stable/generated/torch.atan.html#torch.atan "torch.atan") to each Tensor of the input list.  |
| [`_foreach_ceil`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_ceil.html#torch._foreach_ceil "torch._foreach_ceil")  | Apply [`torch.ceil()`](https://docs.pytorch.org/docs/stable/generated/torch.ceil.html#torch.ceil "torch.ceil") to each Tensor of the input list.  |
| [`_foreach_ceil_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_ceil_.html#torch._foreach_ceil_ "torch._foreach_ceil_")  | Apply [`torch.ceil()`](https://docs.pytorch.org/docs/stable/generated/torch.ceil.html#torch.ceil "torch.ceil") to each Tensor of the input list.  |
| [`_foreach_cos`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_cos.html#torch._foreach_cos "torch._foreach_cos")  | Apply [`torch.cos()`](https://docs.pytorch.org/docs/stable/generated/torch.cos.html#torch.cos "torch.cos") to each Tensor of the input list.  |
| [`_foreach_cos_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_cos_.html#torch._foreach_cos_ "torch._foreach_cos_")  | Apply [`torch.cos()`](https://docs.pytorch.org/docs/stable/generated/torch.cos.html#torch.cos "torch.cos") to each Tensor of the input list.  |
| [`_foreach_cosh`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_cosh.html#torch._foreach_cosh "torch._foreach_cosh")  | Apply [`torch.cosh()`](https://docs.pytorch.org/docs/stable/generated/torch.cosh.html#torch.cosh "torch.cosh") to each Tensor of the input list.  |
| [`_foreach_cosh_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_cosh_.html#torch._foreach_cosh_ "torch._foreach_cosh_")  | Apply [`torch.cosh()`](https://docs.pytorch.org/docs/stable/generated/torch.cosh.html#torch.cosh "torch.cosh") to each Tensor of the input list.  |
| [`_foreach_erf`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_erf.html#torch._foreach_erf "torch._foreach_erf")  | Apply [`torch.erf()`](https://docs.pytorch.org/docs/stable/generated/torch.erf.html#torch.erf "torch.erf") to each Tensor of the input list.  |
| [`_foreach_erf_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_erf_.html#torch._foreach_erf_ "torch._foreach_erf_")  | Apply [`torch.erf()`](https://docs.pytorch.org/docs/stable/generated/torch.erf.html#torch.erf "torch.erf") to each Tensor of the input list.  |
| [`_foreach_erfc`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_erfc.html#torch._foreach_erfc "torch._foreach_erfc")  | Apply [`torch.erfc()`](https://docs.pytorch.org/docs/stable/generated/torch.erfc.html#torch.erfc "torch.erfc") to each Tensor of the input list.  |
| [`_foreach_erfc_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_erfc_.html#torch._foreach_erfc_ "torch._foreach_erfc_")  | Apply [`torch.erfc()`](https://docs.pytorch.org/docs/stable/generated/torch.erfc.html#torch.erfc "torch.erfc") to each Tensor of the input list.  |
| [`_foreach_exp`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_exp.html#torch._foreach_exp "torch._foreach_exp")  | Apply [`torch.exp()`](https://docs.pytorch.org/docs/stable/generated/torch.exp.html#torch.exp "torch.exp") to each Tensor of the input list.  |
| [`_foreach_exp_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_exp_.html#torch._foreach_exp_ "torch._foreach_exp_")  | Apply [`torch.exp()`](https://docs.pytorch.org/docs/stable/generated/torch.exp.html#torch.exp "torch.exp") to each Tensor of the input list.  |
| [`_foreach_expm1`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_expm1.html#torch._foreach_expm1 "torch._foreach_expm1")  | Apply [`torch.expm1()`](https://docs.pytorch.org/docs/stable/generated/torch.expm1.html#torch.expm1 "torch.expm1") to each Tensor of the input list.  |
| [`_foreach_expm1_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_expm1_.html#torch._foreach_expm1_ "torch._foreach_expm1_")  | Apply [`torch.expm1()`](https://docs.pytorch.org/docs/stable/generated/torch.expm1.html#torch.expm1 "torch.expm1") to each Tensor of the input list.  |
| [`_foreach_floor`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_floor.html#torch._foreach_floor "torch._foreach_floor")  | Apply [`torch.floor()`](https://docs.pytorch.org/docs/stable/generated/torch.floor.html#torch.floor "torch.floor") to each Tensor of the input list.  |
| [`_foreach_floor_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_floor_.html#torch._foreach_floor_ "torch._foreach_floor_")  | Apply [`torch.floor()`](https://docs.pytorch.org/docs/stable/generated/torch.floor.html#torch.floor "torch.floor") to each Tensor of the input list.  |
| [`_foreach_log`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log.html#torch._foreach_log "torch._foreach_log")  | Apply [`torch.log()`](https://docs.pytorch.org/docs/stable/generated/torch.log.html#torch.log "torch.log") to each Tensor of the input list.  |
| [`_foreach_log_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log_.html#torch._foreach_log_ "torch._foreach_log_")  | Apply [`torch.log()`](https://docs.pytorch.org/docs/stable/generated/torch.log.html#torch.log "torch.log") to each Tensor of the input list.  |
| [`_foreach_log10`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log10.html#torch._foreach_log10 "torch._foreach_log10")  | Apply [`torch.log10()`](https://docs.pytorch.org/docs/stable/generated/torch.log10.html#torch.log10 "torch.log10") to each Tensor of the input list.  |
| [`_foreach_log10_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log10_.html#torch._foreach_log10_ "torch._foreach_log10_")  | Apply [`torch.log10()`](https://docs.pytorch.org/docs/stable/generated/torch.log10.html#torch.log10 "torch.log10") to each Tensor of the input list.  |
| [`_foreach_log1p`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log1p.html#torch._foreach_log1p "torch._foreach_log1p")  | Apply [`torch.log1p()`](https://docs.pytorch.org/docs/stable/generated/torch.log1p.html#torch.log1p "torch.log1p") to each Tensor of the input list.  |
| [`_foreach_log1p_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log1p_.html#torch._foreach_log1p_ "torch._foreach_log1p_")  | Apply [`torch.log1p()`](https://docs.pytorch.org/docs/stable/generated/torch.log1p.html#torch.log1p "torch.log1p") to each Tensor of the input list.  |
| [`_foreach_log2`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log2.html#torch._foreach_log2 "torch._foreach_log2")  | Apply [`torch.log2()`](https://docs.pytorch.org/docs/stable/generated/torch.log2.html#torch.log2 "torch.log2") to each Tensor of the input list.  |
| [`_foreach_log2_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_log2_.html#torch._foreach_log2_ "torch._foreach_log2_")  | Apply [`torch.log2()`](https://docs.pytorch.org/docs/stable/generated/torch.log2.html#torch.log2 "torch.log2") to each Tensor of the input list.  |
| [`_foreach_neg`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_neg.html#torch._foreach_neg "torch._foreach_neg")  | Apply [`torch.neg()`](https://docs.pytorch.org/docs/stable/generated/torch.neg.html#torch.neg "torch.neg") to each Tensor of the input list.  |
| [`_foreach_neg_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_neg_.html#torch._foreach_neg_ "torch._foreach_neg_")  | Apply [`torch.neg()`](https://docs.pytorch.org/docs/stable/generated/torch.neg.html#torch.neg "torch.neg") to each Tensor of the input list.  |
| [`_foreach_tan`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_tan.html#torch._foreach_tan "torch._foreach_tan")  | Apply [`torch.tan()`](https://docs.pytorch.org/docs/stable/generated/torch.tan.html#torch.tan "torch.tan") to each Tensor of the input list.  |
| [`_foreach_tan_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_tan_.html#torch._foreach_tan_ "torch._foreach_tan_")  | Apply [`torch.tan()`](https://docs.pytorch.org/docs/stable/generated/torch.tan.html#torch.tan "torch.tan") to each Tensor of the input list.  |
| [`_foreach_sin`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sin.html#torch._foreach_sin "torch._foreach_sin")  | Apply [`torch.sin()`](https://docs.pytorch.org/docs/stable/generated/torch.sin.html#torch.sin "torch.sin") to each Tensor of the input list.  |
| [`_foreach_sin_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sin_.html#torch._foreach_sin_ "torch._foreach_sin_")  | Apply [`torch.sin()`](https://docs.pytorch.org/docs/stable/generated/torch.sin.html#torch.sin "torch.sin") to each Tensor of the input list.  |
| [`_foreach_sinh`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sinh.html#torch._foreach_sinh "torch._foreach_sinh")  | Apply [`torch.sinh()`](https://docs.pytorch.org/docs/stable/generated/torch.sinh.html#torch.sinh "torch.sinh") to each Tensor of the input list.  |
| [`_foreach_sinh_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sinh_.html#torch._foreach_sinh_ "torch._foreach_sinh_")  | Apply [`torch.sinh()`](https://docs.pytorch.org/docs/stable/generated/torch.sinh.html#torch.sinh "torch.sinh") to each Tensor of the input list.  |
| [`_foreach_round`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_round.html#torch._foreach_round "torch._foreach_round")  | Apply [`torch.round()`](https://docs.pytorch.org/docs/stable/generated/torch.round.html#torch.round "torch.round") to each Tensor of the input list.  |
| [`_foreach_round_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_round_.html#torch._foreach_round_ "torch._foreach_round_")  | Apply [`torch.round()`](https://docs.pytorch.org/docs/stable/generated/torch.round.html#torch.round "torch.round") to each Tensor of the input list.  |
| [`_foreach_sqrt`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sqrt.html#torch._foreach_sqrt "torch._foreach_sqrt")  | Apply [`torch.sqrt()`](https://docs.pytorch.org/docs/stable/generated/torch.sqrt.html#torch.sqrt "torch.sqrt") to each Tensor of the input list.  |
| [`_foreach_sqrt_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sqrt_.html#torch._foreach_sqrt_ "torch._foreach_sqrt_")  | Apply [`torch.sqrt()`](https://docs.pytorch.org/docs/stable/generated/torch.sqrt.html#torch.sqrt "torch.sqrt") to each Tensor of the input list.  |
| [`_foreach_lgamma`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_lgamma.html#torch._foreach_lgamma "torch._foreach_lgamma")  | Apply [`torch.lgamma()`](https://docs.pytorch.org/docs/stable/generated/torch.lgamma.html#torch.lgamma "torch.lgamma") to each Tensor of the input list.  |
| [`_foreach_lgamma_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_lgamma_.html#torch._foreach_lgamma_ "torch._foreach_lgamma_")  | Apply [`torch.lgamma()`](https://docs.pytorch.org/docs/stable/generated/torch.lgamma.html#torch.lgamma "torch.lgamma") to each Tensor of the input list.  |
| [`_foreach_frac`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_frac.html#torch._foreach_frac "torch._foreach_frac")  | Apply [`torch.frac()`](https://docs.pytorch.org/docs/stable/generated/torch.frac.html#torch.frac "torch.frac") to each Tensor of the input list.  |
| [`_foreach_frac_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_frac_.html#torch._foreach_frac_ "torch._foreach_frac_")  | Apply [`torch.frac()`](https://docs.pytorch.org/docs/stable/generated/torch.frac.html#torch.frac "torch.frac") to each Tensor of the input list.  |
| [`_foreach_reciprocal`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_reciprocal.html#torch._foreach_reciprocal "torch._foreach_reciprocal")  | Apply [`torch.reciprocal()`](https://docs.pytorch.org/docs/stable/generated/torch.reciprocal.html#torch.reciprocal "torch.reciprocal") to each Tensor of the input list.  |
| [`_foreach_reciprocal_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_reciprocal_.html#torch._foreach_reciprocal_ "torch._foreach_reciprocal_")  | Apply [`torch.reciprocal()`](https://docs.pytorch.org/docs/stable/generated/torch.reciprocal.html#torch.reciprocal "torch.reciprocal") to each Tensor of the input list.  |
| [`_foreach_sigmoid`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sigmoid.html#torch._foreach_sigmoid "torch._foreach_sigmoid")  | Apply [`torch.sigmoid()`](https://docs.pytorch.org/docs/stable/generated/torch.sigmoid.html#torch.sigmoid "torch.sigmoid") to each Tensor of the input list.  |
| [`_foreach_sigmoid_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_sigmoid_.html#torch._foreach_sigmoid_ "torch._foreach_sigmoid_")  | Apply [`torch.sigmoid()`](https://docs.pytorch.org/docs/stable/generated/torch.sigmoid.html#torch.sigmoid "torch.sigmoid") to each Tensor of the input list.  |
| [`_foreach_trunc`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_trunc.html#torch._foreach_trunc "torch._foreach_trunc")  | Apply [`torch.trunc()`](https://docs.pytorch.org/docs/stable/generated/torch.trunc.html#torch.trunc "torch.trunc") to each Tensor of the input list.  |
| [`_foreach_trunc_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_trunc_.html#torch._foreach_trunc_ "torch._foreach_trunc_")  | Apply [`torch.trunc()`](https://docs.pytorch.org/docs/stable/generated/torch.trunc.html#torch.trunc "torch.trunc") to each Tensor of the input list.  |
| [`_foreach_zero_`](https://docs.pytorch.org/docs/stable/generated/torch._foreach_zero_.html#torch._foreach_zero_ "torch._foreach_zero_")  | Apply `torch.zero()` to each Tensor of the input list.  |
## Utilities[#](https://docs.pytorch.org/docs/stable/torch.html#utilities "Link to this heading")
| [`compiled_with_cxx11_abi`](https://docs.pytorch.org/docs/stable/generated/torch.compiled_with_cxx11_abi.html#torch.compiled_with_cxx11_abi "torch.compiled_with_cxx11_abi")  | Returns whether PyTorch was built with _GLIBCXX_USE_CXX11_ABI=1  |
| --- | --- |
| [`result_type`](https://docs.pytorch.org/docs/stable/generated/torch.result_type.html#torch.result_type "torch.result_type")  | Returns the [`torch.dtype`](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.dtype "torch.dtype") that would result from performing an arithmetic operation on the provided input tensors.  |
| [`can_cast`](https://docs.pytorch.org/docs/stable/generated/torch.can_cast.html#torch.can_cast "torch.can_cast")  | Determines if a type conversion is allowed under PyTorch casting rules described in the type promotion [documentation](https://docs.pytorch.org/docs/stable/tensor_attributes.html#type-promotion-doc).  |
| [`promote_types`](https://docs.pytorch.org/docs/stable/generated/torch.promote_types.html#torch.promote_types "torch.promote_types")  | Returns the [`torch.dtype`](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.dtype "torch.dtype") with the smallest size and scalar kind that is not smaller nor of lower kind than either type1 or type2.  |
| [`use_deterministic_algorithms`](https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html#torch.use_deterministic_algorithms "torch.use_deterministic_algorithms")  | Sets whether PyTorch operations must use "deterministic" algorithms.  |
| [`are_deterministic_algorithms_enabled`](https://docs.pytorch.org/docs/stable/generated/torch.are_deterministic_algorithms_enabled.html#torch.are_deterministic_algorithms_enabled "torch.are_deterministic_algorithms_enabled")  | Returns True if the global deterministic flag is turned on.  |
| [`is_deterministic_algorithms_warn_only_enabled`](https://docs.pytorch.org/docs/stable/generated/torch.is_deterministic_algorithms_warn_only_enabled.html#torch.is_deterministic_algorithms_warn_only_enabled "torch.is_deterministic_algorithms_warn_only_enabled")  | Returns True if the global deterministic flag is set to warn only.  |
| [`set_deterministic_debug_mode`](https://docs.pytorch.org/docs/stable/generated/torch.set_deterministic_debug_mode.html#torch.set_deterministic_debug_mode "torch.set_deterministic_debug_mode")  | Sets the debug mode for deterministic operations.  |
| [`get_deterministic_debug_mode`](https://docs.pytorch.org/docs/stable/generated/torch.get_deterministic_debug_mode.html#torch.get_deterministic_debug_mode "torch.get_deterministic_debug_mode")  | Returns the current value of the debug mode for deterministic operations.  |
| [`set_float32_matmul_precision`](https://docs.pytorch.org/docs/stable/generated/torch.set_float32_matmul_precision.html#torch.set_float32_matmul_precision "torch.set_float32_matmul_precision")  | Sets the internal precision of float32 matrix multiplications.  |
| [`get_float32_matmul_precision`](https://docs.pytorch.org/docs/stable/generated/torch.get_float32_matmul_precision.html#torch.get_float32_matmul_precision "torch.get_float32_matmul_precision")  | Returns the current value of float32 matrix multiplication precision.  |
| [`set_warn_always`](https://docs.pytorch.org/docs/stable/generated/torch.set_warn_always.html#torch.set_warn_always "torch.set_warn_always")  | When this flag is False (default) then some PyTorch warnings may only appear once per process.  |
| [`get_device_module`](https://docs.pytorch.org/docs/stable/generated/torch.get_device_module.html#torch.get_device_module "torch.get_device_module")  | Returns the module associated with a given device(e.g., torch.device('cuda'), "mtia:0", "xpu", ...).  |
| [`is_warn_always_enabled`](https://docs.pytorch.org/docs/stable/generated/torch.is_warn_always_enabled.html#torch.is_warn_always_enabled "torch.is_warn_always_enabled")  | Returns True if the global warn_always flag is turned on.  |
| [`vmap`](https://docs.pytorch.org/docs/stable/generated/torch.vmap.html#torch.vmap "torch.vmap")  | vmap is the vectorizing map; `vmap(func)` returns a new function that maps `func` over some dimension of the inputs.  |
| [`_assert`](https://docs.pytorch.org/docs/stable/generated/torch._assert.html#torch._assert "torch._assert")  | A wrapper around Python's assert which is symbolically traceable.  |
## Symbolic Numbers[#](https://docs.pytorch.org/docs/stable/torch.html#symbolic-numbers "Link to this heading")

_class_ torch.SymInt(_node_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L445)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymInt "Link to this definition")

Like an int (including magic methods), but redirects all operations on the wrapped node. This is used in particular to symbolically record operations in the symbolic shape workflow.

as_integer_ratio()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L627)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymInt.as_integer_ratio "Link to this definition")

Represent this int as an exact integer ratio

Return type:

[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[SymInt](https://docs.pytorch.org/docs/stable/torch.html#torch.SymInt "torch.SymInt"), [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")]

_class_ torch.SymFloat(_node_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L642)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat "Link to this definition")

Like a float (including magic methods), but redirects all operations on the wrapped node. This is used in particular to symbolically record operations in the symbolic shape workflow.

as_integer_ratio()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L742)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.as_integer_ratio "Link to this definition")

Represent this float as an exact integer ratio

Return type:

[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)"), [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")]

conjugate()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L755)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.conjugate "Link to this definition")

Returns the complex conjugate of the float.

Return type:

[_SymFloat_](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat "torch.SymFloat")

hex()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L759)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.hex "Link to this definition")

Returns the hexadecimal representation of the float.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")

is_integer()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L738)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.is_integer "Link to this definition")

Return True if the float is an integer.

_class_ torch.SymBool(_node_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/__init__.py#L764)[#](https://docs.pytorch.org/docs/stable/torch.html#torch.SymBool "Link to this definition")

Like a bool (including magic methods), but redirects all operations on the wrapped node. This is used in particular to symbolically record operations in the symbolic shape workflow.
Unlike regular bools, regular boolean operators will force extra guards instead of symbolically evaluate. Use the bitwise operators instead to handle this.
| [`sym_float`](https://docs.pytorch.org/docs/stable/generated/torch.sym_float.html#torch.sym_float "torch.sym_float")  | SymInt-aware utility for float casting.  |
| --- | --- |
| [`sym_fresh_size`](https://docs.pytorch.org/docs/stable/generated/torch.sym_fresh_size.html#torch.sym_fresh_size "torch.sym_fresh_size")  |   |
| [`sym_int`](https://docs.pytorch.org/docs/stable/generated/torch.sym_int.html#torch.sym_int "torch.sym_int")  | SymInt-aware utility for int casting.  |
| [`sym_max`](https://docs.pytorch.org/docs/stable/generated/torch.sym_max.html#torch.sym_max "torch.sym_max")  | SymInt-aware utility for max which avoids branching on a < b.  |
| [`sym_min`](https://docs.pytorch.org/docs/stable/generated/torch.sym_min.html#torch.sym_min "torch.sym_min")  | SymInt-aware utility for min().  |
| [`sym_not`](https://docs.pytorch.org/docs/stable/generated/torch.sym_not.html#torch.sym_not "torch.sym_not")  | SymInt-aware utility for logical negation.  |
| [`sym_ite`](https://docs.pytorch.org/docs/stable/generated/torch.sym_ite.html#torch.sym_ite "torch.sym_ite")  | SymInt-aware utility for ternary operator (`t if b else f`.)  |
| [`sym_sum`](https://docs.pytorch.org/docs/stable/generated/torch.sym_sum.html#torch.sym_sum "torch.sym_sum")  | N-ary add which is faster to compute for long lists than iterated binary addition.  |
## Export Path[#](https://docs.pytorch.org/docs/stable/torch.html#export-path "Link to this heading")
Warning
This feature is a prototype and may have compatibility breaking changes in the future.
export generated/exportdb/index
## Control Flow[#](https://docs.pytorch.org/docs/stable/torch.html#control-flow "Link to this heading")
Warning
This feature is a prototype and may have compatibility breaking changes in the future.
| [`cond`](https://docs.pytorch.org/docs/stable/generated/torch.cond.html#torch.cond "torch.cond")  | Conditionally applies true_fn or false_fn.  |
| --- | --- |
## Optimizations[#](https://docs.pytorch.org/docs/stable/torch.html#optimizations "Link to this heading")
| [`compile`](https://docs.pytorch.org/docs/stable/generated/torch.compile.html#torch.compile "torch.compile")  | Optimizes given model/function using TorchDynamo and specified backend.  |
| --- | --- |
[torch.compile documentation](https://docs.pytorch.org/docs/main/user_guide/torch_compiler/torch.compiler.html)
## Operator Tags[#](https://docs.pytorch.org/docs/stable/torch.html#operator-tags "Link to this heading")

_class_ torch.Tag[#](https://docs.pytorch.org/docs/stable/torch.html#torch.Tag "Link to this definition")

Members:
core
cudagraph_unsafe
data_dependent_output
dynamic_output_shape
flexible_layout
generated
inplace_view
maybe_aliasing_or_mutating
needs_contiguous_strides
needs_exact_strides
needs_fixed_stride_order
nondeterministic_bitwise
nondeterministic_seeded
out_variant
pointwise
pt2_compliant_tag
reduction
view_copy

_property_ name[#](https://docs.pytorch.org/docs/stable/torch.html#torch.Tag.name "Link to this definition")

Rate this Page
★ ★ ★ ★ ★
Send Feedback
[ previous Reference API ](https://docs.pytorch.org/docs/stable/pytorch-api.html "previous page") [ next torch.is_tensor ](https://docs.pytorch.org/docs/stable/generated/torch.is_tensor.html "next page")
Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.15.4.
[ previous Reference API ](https://docs.pytorch.org/docs/stable/pytorch-api.html "previous page") [ next torch.is_tensor ](https://docs.pytorch.org/docs/stable/generated/torch.is_tensor.html "next page")
On this page
  * [Tensors](https://docs.pytorch.org/docs/stable/torch.html#tensors)
    * [Creation Ops](https://docs.pytorch.org/docs/stable/torch.html#creation-ops)
    * [Indexing, Slicing, Joining, Mutating Ops](https://docs.pytorch.org/docs/stable/torch.html#indexing-slicing-joining-mutating-ops)
  * [Accelerators](https://docs.pytorch.org/docs/stable/torch.html#accelerators)
  * [Generators](https://docs.pytorch.org/docs/stable/torch.html#generators)
  * [Random sampling](https://docs.pytorch.org/docs/stable/torch.html#random-sampling)
    * [`torch.default_generator`](https://docs.pytorch.org/docs/stable/torch.html#torch.torch.default_generator)
    * [In-place random sampling](https://docs.pytorch.org/docs/stable/torch.html#in-place-random-sampling)
    * [Quasi-random sampling](https://docs.pytorch.org/docs/stable/torch.html#quasi-random-sampling)
  * [Serialization](https://docs.pytorch.org/docs/stable/torch.html#serialization)
  * [Parallelism](https://docs.pytorch.org/docs/stable/torch.html#parallelism)
  * [Locally disabling gradient computation](https://docs.pytorch.org/docs/stable/torch.html#locally-disabling-gradient-computation)
  * [Math operations](https://docs.pytorch.org/docs/stable/torch.html#math-operations)
    * [Constants](https://docs.pytorch.org/docs/stable/torch.html#constants)
    * [Pointwise Ops](https://docs.pytorch.org/docs/stable/torch.html#pointwise-ops)
    * [Reduction Ops](https://docs.pytorch.org/docs/stable/torch.html#reduction-ops)
    * [Comparison Ops](https://docs.pytorch.org/docs/stable/torch.html#comparison-ops)
    * [Spectral Ops](https://docs.pytorch.org/docs/stable/torch.html#spectral-ops)
    * [Other Operations](https://docs.pytorch.org/docs/stable/torch.html#other-operations)
    * [BLAS and LAPACK Operations](https://docs.pytorch.org/docs/stable/torch.html#blas-and-lapack-operations)
    * [Foreach Operations](https://docs.pytorch.org/docs/stable/torch.html#foreach-operations)
  * [Utilities](https://docs.pytorch.org/docs/stable/torch.html#utilities)
  * [Symbolic Numbers](https://docs.pytorch.org/docs/stable/torch.html#symbolic-numbers)
    * [`SymInt`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymInt)
      * [`SymInt.as_integer_ratio()`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymInt.as_integer_ratio)
    * [`SymFloat`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat)
      * [`SymFloat.as_integer_ratio()`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.as_integer_ratio)
      * [`SymFloat.conjugate()`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.conjugate)
      * [`SymFloat.hex()`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.hex)
      * [`SymFloat.is_integer()`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymFloat.is_integer)
    * [`SymBool`](https://docs.pytorch.org/docs/stable/torch.html#torch.SymBool)
  * [Export Path](https://docs.pytorch.org/docs/stable/torch.html#export-path)
  * [Control Flow](https://docs.pytorch.org/docs/stable/torch.html#control-flow)
  * [Optimizations](https://docs.pytorch.org/docs/stable/torch.html#optimizations)
  * [Operator Tags](https://docs.pytorch.org/docs/stable/torch.html#operator-tags)
    * [`Tag`](https://docs.pytorch.org/docs/stable/torch.html#torch.Tag)
      * [`Tag.name`](https://docs.pytorch.org/docs/stable/torch.html#torch.Tag.name)


[ Edit on GitHub ](https://github.com/pytorch/pytorch/edit/main/docs/source/torch.rst)
[ Show Source ](https://docs.pytorch.org/docs/stable/_sources/torch.rst.txt)
PyTorch Libraries
  * [ExecuTorch](https://docs.pytorch.org/executorch)
  * [Helion](https://docs.pytorch.org/helion)
  * [torchao](https://docs.pytorch.org/ao)
  * [kineto](https://github.com/pytorch/kineto)
  * [torchtitan](https://github.com/pytorch/torchtitan)
  * [TorchRL](https://docs.pytorch.org/rl)
  * [torchvision](https://docs.pytorch.org/vision)
  * [torchaudio](https://docs.pytorch.org/audio)
  * [tensordict](https://docs.pytorch.org/tensordict)
  * [PyTorch on XLA Devices](https://docs.pytorch.org/xla)


## Docs
Access comprehensive developer documentation for PyTorch
[View Docs](https://docs.pytorch.org/docs/stable/index.html)
## Tutorials
Get in-depth tutorials for beginners and advanced developers
[View Tutorials](https://docs.pytorch.org/tutorials)
## Resources
Find development resources and get your questions answered
[View Resources](https://pytorch.org/resources)
**Stay in touch** for updates, event info, and the latest news
Select Country* Afghanistan Åland Islands Albania Algeria American Samoa Andorra Angola Anguilla Antarctica Antigua and Barbuda Argentina Armenia Aruba Asia/Pacific Region Australia Austria Azerbaijan Bahamas Bahrain Bangladesh Barbados Belarus Belgium Belize Benin Bermuda Bhutan Bolivia Bosnia and Herzegovina Botswana Bouvet Island Brazil British Indian Ocean Territory British Virgin Islands Brunei Bulgaria Burkina Faso Burundi Cambodia Cameroon Canada Canary Islands Cape Verde Caribbean Netherlands Cayman Islands Central African Republic Chad Chile China Christmas Island Cocos (Keeling) Islands Colombia Comoros Congo Cook Islands Costa Rica Cote d'Ivoire Croatia Cuba Curaçao Cyprus Czech Republic Democratic Republic of the Congo Denmark Djibouti Dominica Dominican Republic East Timor Ecuador Egypt El Salvador Equatorial Guinea Eritrea Estonia Ethiopia Europe Falkland Islands Faroe Islands Fiji Finland France French Guiana French Polynesia French Southern and Antarctic Lands Gabon Gambia Georgia Germany Ghana Gibraltar Greece Greenland Grenada Guadeloupe Guam Guatemala Guernsey Guinea Guinea-Bissau Guyana Haiti Heard Island and McDonald Islands Honduras Hong Kong Hungary Iceland India Indonesia Iran Iraq Ireland Isle of Man Israel Italy Jamaica Japan Jersey Jordan Kazakhstan Kenya Kiribati Kosovo Kuwait Kyrgyzstan Laos Latvia Lebanon Lesotho Liberia Libya Liechtenstein Lithuania Luxembourg Macau Macedonia (FYROM) Madagascar Malawi Malaysia Maldives Mali Malta Marshall Islands Martinique Mauritania Mauritius Mayotte Mexico Micronesia Moldova Monaco Mongolia Montenegro Montserrat Morocco Mozambique Myanmar (Burma) Namibia Nauru Nepal Netherlands Netherlands Antilles New Caledonia New Zealand Nicaragua Niger Nigeria Niue Norfolk Island North Korea Northern Mariana Islands Norway Oman Pakistan Palau Palestine Panama Papua New Guinea Paraguay Peru Philippines Pitcairn Islands Poland Portugal Puerto Rico Qatar Réunion Romania Russia Rwanda Saint Barthélemy Saint Helena Saint Kitts and Nevis Saint Lucia Saint Martin Saint Pierre and Miquelon Saint Vincent and the Grenadines Samoa San Marino Sao Tome and Principe Saudi Arabia Senegal Serbia Seychelles Sierra Leone Singapore Sint Maarten Slovakia Slovenia Solomon Islands Somalia South Africa South Georgia and the South Sandwich Islands South Korea South Sudan Spain Sri Lanka Sudan Suriname Svalbard and Jan Mayen Swaziland Sweden Switzerland Syria Taiwan Tajikistan Tanzania Thailand Togo Tokelau Tonga Trinidad and Tobago Tunisia Türkiye Turkmenistan Turks and Caicos Islands Tuvalu U.S. Virgin Islands Uganda Ukraine United Arab Emirates United Kingdom United States United States Minor Outlying Islands Uruguay Uzbekistan Vanuatu Vatican City Venezuela Vietnam Wallis and Futuna Western Sahara Yemen Zambia Zimbabwe
By submitting this form, I consent to receive marketing emails from the LF and its projects regarding their events, training, research, developments, and related announcements. I understand that I can unsubscribe at any time using the links in the footers of the emails I receive. [Privacy Policy](https://www.linuxfoundation.org/legal/privacy-policy)
By submitting this form, I consent to receive marketing emails from the LF and its projects regarding their events, training, research, developments, and related announcements. I understand that I can unsubscribe at any time using the links in the footers of the emails I receive. [Privacy Policy](https://www.linuxfoundation.org/privacy/).
  * [ ](https://www.facebook.com/pytorch "PyTorch on Facebook")
  * [ ](https://twitter.com/pytorch "PyTorch on X")
  * [ ](https://www.youtube.com/pytorch "PyTorch on YouTube")
  * [ ](https://www.linkedin.com/company/pytorch "PyTorch on LinkedIn")
  * [ ](https://pytorch.slack.com "PyTorch Slack")
  * [ ](https://pytorch.org/wechat "PyTorch on WeChat")


© PyTorch. Copyright © The Linux Foundation®. All rights reserved. The Linux Foundation has registered trademarks and uses trademarks. For more information, including terms of use, privacy policy, and trademark usage, please see our [Policies](https://www.linuxfoundation.org/legal/policies) page. [Trademark Usage](https://www.linuxfoundation.org/trademark-usage). [Privacy Policy](http://www.linuxfoundation.org/privacy).
To analyze traffic and optimize your experience, we serve cookies on this site. By clicking or navigating, you agree to allow our usage of cookies. As the current maintainers of this site, Facebook’s Cookies Policy applies. Learn more, including about available controls: [Cookies Policy](https://opensource.fb.com/legal/cookie-policy).
![](https://docs.pytorch.org/docs/stable/_static/img/pytorch-x.svg)
© Copyright PyTorch Contributors.

Created using [Sphinx](https://www.sphinx-doc.org/) 7.2.6.

Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.15.4.
