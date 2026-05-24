

--- DOCUMENT: https://docs.pytorch.org/docs/stable/distributed.html#basics/ ---
# Distributed communication package - torch.distributed[#](https://docs.pytorch.org/docs/stable/distributed.html#distributed-communication-package-torch-distributed "Link to this heading")
Created On: Jul 12, 2017 | Last Updated On: Feb 14, 2026
Note
Please refer to [PyTorch Distributed Overview](https://pytorch.org/tutorials/beginner/dist_overview.html) for a brief introduction to all features related to distributed training.
## Backends[#](https://docs.pytorch.org/docs/stable/distributed.html#backends "Link to this heading")
`torch.distributed` supports four built-in backends, each with different capabilities. The table below shows which functions are available for use with a CPU or GPU for each backend. For NCCL, GPU refers to CUDA GPU while for XCCL to XPU GPU.
MPI supports CUDA only if the implementation used to build PyTorch supports it.
| Backend  | `gloo`  | `mpi`  | `nccl`  | `xccl`  |
| --- | --- | --- | --- | --- |
| Device  | CPU  | GPU  | CPU  | GPU  | CPU  | GPU  | CPU  | GPU  |
| send  | ✓  | ✘  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| recv  | ✓  | ✘  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| broadcast  | ✓  | ✓  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| all_reduce  | ✓  | ✓  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| reduce  | ✓  | ✓  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| all_gather  | ✓  | ✓  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| gather  | ✓  | ✓  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| scatter  | ✓  | ✓  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| reduce_scatter  | ✓  | ✓  | ✘  | ✘  | ✘  | ✓  | ✘  | ✓  |
| all_to_all  | ✘  | ✘  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
| barrier  | ✓  | ✘  | ✓  | ?  | ✘  | ✓  | ✘  | ✓  |
### Backends that come with PyTorch[#](https://docs.pytorch.org/docs/stable/distributed.html#backends-that-come-with-pytorch "Link to this heading")
PyTorch distributed package supports Linux (stable), macOS (stable), and Windows (prototype). By default for Linux, the Gloo and NCCL backends are built and included in PyTorch distributed (NCCL only when building with CUDA). MPI is an optional backend that can only be included if you build PyTorch from source. (e.g. building PyTorch on a host that has MPI installed.)
Note
As of PyTorch v1.8, Windows supports all collective communications backends but NCCL, If the `init_method` argument of [`init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") points to a file it must adhere to the following schema:
  * Local file system, `init_method="file:///d:/tmp/some_file"`
  * Shared file system, `init_method="file://////{machine_name}/{share_folder_name}/some_file"`


Same as on Linux platform, you can enable TcpStore by setting environment variables, MASTER_ADDR and MASTER_PORT.
### Which backend to use?[#](https://docs.pytorch.org/docs/stable/distributed.html#which-backend-to-use "Link to this heading")
In the past, we were often asked: “which backend should I use?”.
  * Rule of thumb
    * Use the NCCL backend for distributed training with CUDA **GPU**.
    * Use the XCCL backend for distributed training with XPU **GPU**.
    * Use the Gloo backend for distributed training with **CPU**.
  * GPU hosts with InfiniBand interconnect
    * Use NCCL, since it’s the only backend that currently supports InfiniBand and GPUDirect.
  * GPU hosts with Ethernet interconnect
    * Use NCCL, since it currently provides the best distributed GPU training performance, especially for multiprocess single-node or multi-node distributed training. If you encounter any problem with NCCL, use Gloo as the fallback option. (Note that Gloo currently runs slower than NCCL for GPUs.)
  * CPU hosts with InfiniBand interconnect
    * If your InfiniBand has enabled IP over IB, use Gloo, otherwise, use MPI instead. We are planning on adding InfiniBand support for Gloo in the upcoming releases.
  * CPU hosts with Ethernet interconnect
    * Use Gloo, unless you have specific reasons to use MPI.


### Common environment variables[#](https://docs.pytorch.org/docs/stable/distributed.html#common-environment-variables "Link to this heading")
#### Choosing the network interface to use[#](https://docs.pytorch.org/docs/stable/distributed.html#choosing-the-network-interface-to-use "Link to this heading")
By default, both the NCCL and Gloo backends will try to find the right network interface to use. If the automatically detected interface is not correct, you can override it using the following environment variables (applicable to the respective backend):
  * **NCCL_SOCKET_IFNAME** , for example `export NCCL_SOCKET_IFNAME=eth0`
  * **GLOO_SOCKET_IFNAME** , for example `export GLOO_SOCKET_IFNAME=eth0`


If you’re using the Gloo backend, you can specify multiple interfaces by separating them by a comma, like this: `export GLOO_SOCKET_IFNAME=eth0,eth1,eth2,eth3`. The backend will dispatch operations in a round-robin fashion across these interfaces. It is imperative that all processes specify the same number of interfaces in this variable.
#### Other NCCL environment variables[#](https://docs.pytorch.org/docs/stable/distributed.html#other-nccl-environment-variables "Link to this heading")
**Debugging** - in case of NCCL failure, you can set `NCCL_DEBUG=INFO` to print an explicit warning message as well as basic NCCL initialization information.
You may also use `NCCL_DEBUG_SUBSYS` to get more details about a specific aspect of NCCL. For example, `NCCL_DEBUG_SUBSYS=COLL` would print logs of collective calls, which may be helpful when debugging hangs, especially those caused by collective type or message size mismatch. In case of topology detection failure, it would be helpful to set `NCCL_DEBUG_SUBSYS=GRAPH` to inspect the detailed detection result and save as reference if further help from NCCL team is needed.
**Performance tuning** - NCCL performs automatic tuning based on its topology detection to save users’ tuning effort. On some socket-based systems, users may still try tuning `NCCL_SOCKET_NTHREADS` and `NCCL_NSOCKS_PERTHREAD` to increase socket network bandwidth. These two environment variables have been pre-tuned by NCCL for some cloud providers, such as AWS or GCP.
For a full list of NCCL environment variables, please refer to [NVIDIA NCCL’s official documentation](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html)
You can tune NCCL communicators even further using `torch.distributed.ProcessGroupNCCL.NCCLConfig` and `torch.distributed.ProcessGroupNCCL.Options`. Learn more about them using `help` (e.g. `help(torch.distributed.ProcessGroupNCCL.NCCLConfig)`) in the interpreter.
## Basics[#](https://docs.pytorch.org/docs/stable/distributed.html#basics "Link to this heading")
The `torch.distributed` package provides PyTorch support and communication primitives for multiprocess parallelism across several computation nodes running on one or more machines. The class [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") builds on this functionality to provide synchronous distributed training as a wrapper around any PyTorch model. This differs from the kinds of parallelism provided by [Multiprocessing package - torch.multiprocessing](https://docs.pytorch.org/docs/stable/multiprocessing.html) and [`torch.nn.DataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.DataParallel.html#torch.nn.DataParallel "torch.nn.DataParallel") in that it supports multiple network-connected machines and in that the user must explicitly launch a separate copy of the main training script for each process.
In the single-machine synchronous case, `torch.distributed` or the [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") wrapper may still have advantages over other approaches to data-parallelism, including [`torch.nn.DataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.DataParallel.html#torch.nn.DataParallel "torch.nn.DataParallel"):
  * Each process maintains its own optimizer and performs a complete optimization step with each iteration. While this may appear redundant, since the gradients have already been gathered together and averaged across processes and are thus the same for every process, this means that no parameter broadcast step is needed, reducing time spent transferring tensors between nodes.
  * Each process contains an independent Python interpreter, eliminating the extra interpreter overhead and “GIL-thrashing” that comes from driving several execution threads, model replicas, or GPUs from a single Python process. This is especially important for models that make heavy use of the Python runtime, including models with recurrent layers or many small components.


## Initialization[#](https://docs.pytorch.org/docs/stable/distributed.html#initialization "Link to this heading")
The package needs to be initialized using the [`torch.distributed.init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") or [`torch.distributed.device_mesh.init_device_mesh()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.init_device_mesh "torch.distributed.device_mesh.init_device_mesh") function before calling any other methods. Both block until all processes have joined.
Warning
Initialization is not thread-safe. Process group creation should be performed from a single thread, to prevent inconsistent ‘UUID’ assignment across ranks, and to prevent races during initialization that can lead to hangs.

torch.distributed.is_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/__init__.py#L17)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_available "Link to this definition")

Return `True` if the distributed package is available.
Otherwise, `torch.distributed` does not expose any other APIs. Currently, `torch.distributed` is available on Linux, MacOS and Windows. Set `USE_DISTRIBUTED=1` to enable it when building PyTorch from source. Currently, the default value is `USE_DISTRIBUTED=1` for Linux and Windows, `USE_DISTRIBUTED=0` for MacOS.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.init_process_group(_backend =None_, _init_method =None_, _timeout =None_, _world_size =-1_, _rank =-1_, _store =None_, _group_name =''_, _pg_options =None_, _device_id =None_, __ranks =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1603)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "Link to this definition")

Initialize the default distributed process group.
This will also initialize the distributed package.

There are 2 main ways to initialize a process group:

  1. Specify `store`, `rank`, and `world_size` explicitly.
  2. Specify `init_method` (a URL string) which indicates where/how to discover peers. Optionally specify `rank` and `world_size`, or encode all required parameters in the URL and omit them.


If neither is specified, `init_method` is assumed to be “env://”.

Parameters:

  * **backend** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _or_[ _Backend_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend "torch.distributed.Backend") _,__optional_) – The backend to use. Depending on build-time configurations, valid values include `mpi`, `gloo`, `nccl`, `ucc`, `xccl` or one that is registered by a third-party plugin. Since 2.6, if `backend` is not provided, c10d will use a backend registered for the device type indicated by the device_id kwarg (if provided). The known default registrations today are: `nccl` for `cuda`, `gloo` for `cpu`, `xccl` for `xpu`. If neither `backend` nor `device_id` is provided, c10d will detect the accelerator on the run-time machine and use a backend registered for that detected accelerator (or `cpu`). This field can be given as a lowercase string (e.g., `"gloo"`), which can also be accessed via [`Backend`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend "torch.distributed.Backend") attributes (e.g., `Backend.GLOO`). If using multiple processes per machine with `nccl` backend, each process must have exclusive access to every GPU it uses, as sharing GPUs between processes can result in deadlock or NCCL invalid usage. `ucc` backend is experimental. Default backend for the device can be queried with [`get_default_backend_for_device()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_default_backend_for_device "torch.distributed.get_default_backend_for_device").
  * **init_method** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__optional_) – URL specifying how to initialize the process group. Default is “env://” if no `init_method` or `store` is specified. Mutually exclusive with `store`.
  * **world_size** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Number of processes participating in the job. Required if `store` is specified.
  * **rank** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Rank of the current process (it should be a number between 0 and `world_size`-1). Required if `store` is specified.
  * **store** ([_Store_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store "torch.distributed.Store") _,__optional_) – Key/value store accessible to all workers, used to exchange connection/address information. Mutually exclusive with `init_method`.
  * **timeout** (_timedelta_ _,__optional_) – Timeout for operations executed against the process group. Default value is 10 minutes for NCCL and 30 minutes for other backends. This is the duration after which collectives will be aborted asynchronously and the process will crash. This is done since CUDA execution is async and it is no longer safe to continue executing user code since failed async NCCL operations might result in subsequent CUDA operations running on corrupted data. When TORCH_NCCL_BLOCKING_WAIT is set, the process will block and wait for this timeout.
  * **group_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__optional_ _,__deprecated_) – Group name. This argument is ignored
  * **pg_options** (_ProcessGroupOptions_ _,__optional_) – process group options specifying what additional options need to be passed in during the construction of specific process groups. As of now, the only options we support is `ProcessGroupNCCL.Options` for the `nccl` backend, `is_high_priority_stream` can be specified so that the nccl backend can pick up high priority cuda streams when there’re compute kernels waiting. For other available options to config nccl, See <https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-t>
  * **device_id** ([_torch.device_](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.device "torch.device") _|_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – a single, specific device this process will work on, allowing for backend-specific optimizations. Currently this has two effects, only under NCCL: the communicator is immediately formed (calling `ncclCommInit*` immediately rather than the normal lazy call) and sub-groups will use `ncclCommSplit` when possible to avoid unnecessary overhead of group creation. If you want to know NCCL initialization error early, you can also use this field. If an int is provided, the API assumes that the accelerator type at compile time will be used.
  * **_ranks** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _]__|__None_) – The ranks in the process group. If provided, the process group name will be the hash of all the ranks in the group.


Note
To enable `backend == Backend.MPI`, PyTorch needs to be built from source on a system that supports MPI.
Note
Support for multiple backends is experimental. Currently when no backend is specified, both `gloo` and `nccl` backends will be created. The `gloo` backend will be used for collectives with CPU tensors and the `nccl` backend will be used for collectives with CUDA tensors. A custom backend can be specified by passing in a string with format “<device_type>:<backend_name>,<device_type>:<backend_name>”, e.g. “cpu:gloo,cuda:custom_backend”.

torch.distributed.device_mesh.init_device_mesh(_device_type_ , _mesh_shape_ , _*_ , _mesh_dim_names =None_, _backend_override =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L1460)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.init_device_mesh "Link to this definition")

Initializes a DeviceMesh based on device_type, mesh_shape, and mesh_dim_names parameters.
This creates a DeviceMesh with an n-dimensional array layout, where n is the length of mesh_shape. If mesh_dim_names is provided, each dimension is labeled as mesh_dim_names[i].
Note
init_device_mesh follows SPMD programming model, meaning the same PyTorch Python program runs on all processes/ranks in the cluster. Ensure mesh_shape (the dimensions of the nD array describing device layout) is identical across all ranks. Inconsistent mesh_shape may lead to hanging.
Note
If no process group is found, init_device_mesh will initialize distributed process group/groups required for distributed communications behind the scene.

Parameters:

  * **device_type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The device type of the mesh. Currently supports: “cpu”, “cuda/cuda-like”, “xpu”. Passing in a device type with a GPU index, such as “cuda:0”, is not allowed.
  * **mesh_shape** (_Tuple_ _[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _]_) – A tuple defining the dimensions of the multi-dimensional array describing the layout of devices.
  * **mesh_dim_names** ([_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)") _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__...__]__,__optional_) – A tuple of mesh dimension names to assign to each dimension of the multi-dimensional array describing the layout of devices. Its length must match the length of mesh_shape. Each string in mesh_dim_names must be unique.
  * **backend_override** (_Dict_ _[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _|_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,_[_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)") _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__Options_ _]__|_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _|__Options_ _]__,__optional_) – Overrides for some or all of the ProcessGroups that will be created for each mesh dimension. Each key can be either the index of a dimension or its name (if mesh_dim_names is provided). Each value can be a tuple containing the name of the backend and its options, or just one of these two components (in which case the other will be set to its default value).


Returns:

A [`DeviceMesh`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh") object representing the device layout.

Return type:

[DeviceMesh](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh")
Example:

```
>>> from torch.distributed.device_mesh import init_device_mesh
>>>
>>> mesh_1d = init_device_mesh("cuda", mesh_shape=(8,))
>>> mesh_2d = init_device_mesh("cuda", mesh_shape=(2, 8), mesh_dim_names=("dp", "tp"))

```
Copy to clipboard

torch.distributed.is_initialized()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1333)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_initialized "Link to this definition")

Check if the default process group has been initialized.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.is_mpi_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1271)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_mpi_available "Link to this definition")

Check if the MPI backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.is_nccl_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1276)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_nccl_available "Link to this definition")

Check if the NCCL backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.is_gloo_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1281)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_gloo_available "Link to this definition")

Check if the Gloo backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.is_xccl_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1291)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_xccl_available "Link to this definition")

Check if the XCCL backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.batch_isend_irecv(_p2p_op_list_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2847)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.batch_isend_irecv "Link to this definition")

Send or Receive a batch of tensors asynchronously and return a list of requests.
Process each of the operations in `p2p_op_list` and return the corresponding requests. NCCL, Gloo, and UCC backend are currently supported.

Parameters:

**p2p_op_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_P2POp_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.P2POp "torch.distributed.distributed_c10d.P2POp") _]_) – A list of point-to-point operations(type of each operator is `torch.distributed.P2POp`). The order of the isend/irecv in the list matters and it needs to match with corresponding isend/irecv on the remote end.

Returns:

A list of distributed request objects returned by calling the corresponding op in the op_list.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[_Work_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work "torch.distributed.distributed_c10d.Work")]
Examples

```
>>> send_tensor = torch.arange(2, dtype=torch.float32) + 2 * rank
>>> recv_tensor = torch.randn(2, dtype=torch.float32)
>>> send_op = dist.P2POp(dist.isend, send_tensor, (rank + 1) % world_size)
>>> recv_op = dist.P2POp(
...     dist.irecv, recv_tensor, (rank - 1 + world_size) % world_size
... )
>>> reqs = batch_isend_irecv([send_op, recv_op])
>>> for req in reqs:
>>>     req.wait()
>>> recv_tensor
tensor([2, 3])     # Rank 0
tensor([0, 1])     # Rank 1

```
Copy to clipboard
Note
Note that when this API is used with the NCCL PG backend, users must set the current GPU device with torch.cuda.set_device, otherwise it will lead to unexpected hang issues.
In addition, if this API is the first collective call in the `group` passed to `dist.P2POp`, all ranks of the `group` must participate in this API call; otherwise, the behavior is undefined. If this API call is not the first collective call in the `group`, batched P2P operations involving only a subset of ranks of the `group` are allowed.

torch.distributed.distributed_c10d.destroy_process_group(_group =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2273)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.destroy_process_group "Link to this definition")

Destroy a given process group, and deinitialize the distributed package.

Parameters:

**group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _,__optional_) – The process group to be destroyed, if group.WORLD is given, all process groups including the default one will be destroyed.

torch.distributed.distributed_c10d.is_backend_available(_backend_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1308)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_backend_available "Link to this definition")

Check backend availability.
Checks if the given backend is available and supports the built-in backends or third-party backends through function `Backend.register_backend`.

Parameters:

**backend** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – Backend name.

Returns:

Returns true if the backend is available otherwise false.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.irecv(_tensor_ , _src =None_, _group =None_, _tag =0_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2555)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.irecv "Link to this definition")

Receives a tensor asynchronously.
Warning
`tag` is not supported with the NCCL backend.
Unlike recv, which is blocking, irecv allows src == dst rank, i.e. recv from self.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to fill with received data.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Source rank on global process group (regardless of `group` argument). Will receive from any process if unspecified.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **tag** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Tag to match recv with remote send
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `src` and `group_src`.


Returns:

A distributed request object. None, if not part of the group

Return type:

[_Work_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work "torch.distributed.distributed_c10d.Work") | None

torch.distributed.distributed_c10d.is_gloo_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1281)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_gloo_available "Link to this definition")

Check if the Gloo backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.is_initialized()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1333)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_initialized "Link to this definition")

Check if the default process group has been initialized.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.is_mpi_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1271)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_mpi_available "Link to this definition")

Check if the MPI backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.is_nccl_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1276)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_nccl_available "Link to this definition")

Check if the NCCL backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.is_torchelastic_launched()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1338)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_torchelastic_launched "Link to this definition")

Check whether this process was launched with `torch.distributed.elastic` (aka torchelastic).
The existence of `TORCHELASTIC_RUN_ID` environment variable is used as a proxy to determine whether the current process was launched with torchelastic. This is a reasonable proxy since `TORCHELASTIC_RUN_ID` maps to the rendezvous id which is always a non-null value indicating the job id for peer discovery purposes..

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.distributed_c10d.is_ucc_available()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1286)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_ucc_available "Link to this definition")

Check if the UCC backend is available.

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.is_torchelastic_launched()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1338)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_torchelastic_launched "Link to this definition")

Check whether this process was launched with `torch.distributed.elastic` (aka torchelastic).
The existence of `TORCHELASTIC_RUN_ID` environment variable is used as a proxy to determine whether the current process was launched with torchelastic. This is a reasonable proxy since `TORCHELASTIC_RUN_ID` maps to the rendezvous id which is always a non-null value indicating the job id for peer discovery purposes..

Return type:

[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")

torch.distributed.get_default_backend_for_device(_device_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1436)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_default_backend_for_device "Link to this definition")

Return the default backend for the given device.

Parameters:

**device** (_Union_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,_[_torch.device_](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.device "torch.device") _]_) – The device to get the default backend for.

Returns:

The default backend for the given device as a lower case string.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")
* * *
Currently three initialization methods are supported:
### TCP initialization[#](https://docs.pytorch.org/docs/stable/distributed.html#tcp-initialization "Link to this heading")
There are two ways to initialize using TCP, both requiring a network address reachable from all processes and a desired `world_size`. The first way requires specifying an address that belongs to the rank 0 process. This initialization method requires that all processes have manually specified ranks.
Note that multicast address is not supported anymore in the latest distributed package. `group_name` is deprecated as well.

```
import torch.distributed as dist

# Use address of one of the machines
dist.init_process_group(backend, init_method='tcp://10.1.1.20:23456',
                        rank=args.rank, world_size=4)

```
Copy to clipboard
### Shared file-system initialization[#](https://docs.pytorch.org/docs/stable/distributed.html#shared-file-system-initialization "Link to this heading")
Another initialization method makes use of a file system that is shared and visible from all machines in a group, along with a desired `world_size`. The URL should start with `file://` and contain a path to a non-existent file (in an existing directory) on a shared file system. File-system initialization will automatically create that file if it doesn’t exist, but will not delete the file. Therefore, it is your responsibility to make sure that the file is cleaned up before the next [`init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") call on the same file path/name.
Note that automatic rank assignment is not supported anymore in the latest distributed package and `group_name` is deprecated as well.
Warning
This method assumes that the file system supports locking using `fcntl` - most local systems and NFS support it.
Warning
This method will always create the file and try its best to clean up and remove the file at the end of the program. In other words, each initialization with the file init method will need a brand new empty file in order for the initialization to succeed. If the same file used by the previous initialization (which happens not to get cleaned up) is used again, this is unexpected behavior and can often cause deadlocks and failures. Therefore, even though this method will try its best to clean up the file, if the auto-delete happens to be unsuccessful, it is your responsibility to ensure that the file is removed at the end of the training to prevent the same file to be reused again during the next time. This is especially important if you plan to call [`init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") multiple times on the same file name. In other words, if the file is not removed/cleaned up and you call [`init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") again on that file, failures are expected. The rule of thumb here is that, make sure that the file is non-existent or empty every time [`init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") is called.

```
import torch.distributed as dist

# rank should always be specified
dist.init_process_group(backend, init_method='file:///mnt/nfs/sharedfile',
                        world_size=4, rank=args.rank)

```
Copy to clipboard
### Environment variable initialization[#](https://docs.pytorch.org/docs/stable/distributed.html#environment-variable-initialization "Link to this heading")
This method will read the configuration from environment variables, allowing one to fully customize how the information is obtained. The variables to be set are:
  * `MASTER_PORT` - required; has to be a free port on machine with rank 0
  * `MASTER_ADDR` - required (except for rank 0); address of rank 0 node
  * `WORLD_SIZE` - required; can be set either here, or in a call to init function
  * `RANK` - required; can be set either here, or in a call to init function


The machine with rank 0 will be used to set up all connections.
This is the default method, meaning that `init_method` does not have to be specified (or can be `env://`).
### Improving initialization time[#](https://docs.pytorch.org/docs/stable/distributed.html#improving-initialization-time "Link to this heading")
  * `TORCH_GLOO_LAZY_INIT` - establishes connections on demand rather than using a full mesh which can greatly improve initialization time for non all2all operations.


## Post-Initialization[#](https://docs.pytorch.org/docs/stable/distributed.html#post-initialization "Link to this heading")
Once [`torch.distributed.init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") was run, the following functions can be used. To check whether the process group has already been initialized use [`torch.distributed.is_initialized()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_initialized "torch.distributed.is_initialized").

_class_ torch.distributed.Backend(_name_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L257)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend "Link to this definition")

An enum-like class for backends.
Available backends: GLOO, NCCL, UCC, MPI, XCCL, FAKE, and other registered backends.
The values of this class are lowercase strings, e.g., `"gloo"`. They can be accessed as attributes, e.g., `Backend.NCCL`.
This class can be directly called to parse the string, e.g., `Backend(backend_str)` will check if `backend_str` is valid, and return the parsed lowercase string if so. It also accepts uppercase strings, e.g., `Backend("GLOO")` returns `"gloo"`.
Note
The entry `Backend.UNDEFINED` is present but only used as initial value of some fields. Users should neither use it directly nor assume its existence.

_classmethod_ register_backend(_name_ , _func_ , _extended_api =False_, _devices =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L327)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend.register_backend "Link to this definition")

Register a new backend with the given name and instantiating function.
This class method is used by 3rd party `ProcessGroup` extension to register new backends.

Parameters:

  * **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – Backend name of the `ProcessGroup` extension. It should match the one in `init_process_group()`.
  * **func** (_function_) – Function handler that instantiates the backend. The function should be implemented in the backend extension and takes four arguments, including `store`, `rank`, `world_size`, and `timeout`.
  * **extended_api** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether the backend supports extended argument structure. Default: `False`. If set to `True`, the backend will get an instance of `c10d::DistributedBackendOptions`, and a process group options object as defined by the backend implementation.
  * **device** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _or_[ _list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _of_[ _str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__optional_) – device type this backend supports, e.g. “cpu”, “cuda”, etc. If None, assuming both “cpu” and “cuda”


Note
This support of 3rd party backend is experimental and subject to change.

torch.distributed.get_backend(_group =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1410)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_backend "Link to this definition")

Return the backend of the given process group.

Parameters:

**group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. The default is the general main process group. If another specific group is specified, the calling process must be part of `group`.

Returns:

The backend of the given process group as a lower case string.

Return type:

[_Backend_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend "torch.distributed.distributed_c10d.Backend")

torch.distributed.get_rank(_group =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2464)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_rank "Link to this definition")

Return the rank of the current process in the provided `group`, default otherwise.
Rank is a unique identifier assigned to each process within a distributed process group. They are always consecutive integers ranging from 0 to `world_size`.

Parameters:

**group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.

Returns:

The rank of the process group -1, if not part of the group

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")

torch.distributed.get_world_size(_group =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2491)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_world_size "Link to this definition")

Return the number of processes in the current process group.

Parameters:

**group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.

Returns:

The world size of the process group -1, if not part of the group

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")
## Shutdown[#](https://docs.pytorch.org/docs/stable/distributed.html#shutdown "Link to this heading")
It is important to clean up resources on exit by calling `destroy_process_group()`.
The simplest pattern to follow is to destroy every process group and backend by calling `destroy_process_group()` with the default value of None for the `group` argument, at a point in the training script where communications are no longer needed, usually near the end of main(). The call should be made once per trainer-process, not at the outer process-launcher level.
if `destroy_process_group()` is not called by all ranks in a pg within the timeout duration, especially when there are multiple process-groups in the application e.g. for N-D parallelism, hangs on exit are possible. This is because the destructor for ProcessGroupNCCL calls ncclCommAbort, which must be called collectively, but the order of calling ProcessGroupNCCL’s destructor if called by python’s GC is not deterministic. Calling `destroy_process_group()` helps by ensuring ncclCommAbort is called in a consistent order across ranks, and avoids calling ncclCommAbort during ProcessGroupNCCL’s destructor.
### Reinitialization[#](https://docs.pytorch.org/docs/stable/distributed.html#reinitialization "Link to this heading")
`destroy_process_group` can also be used to destroy individual process groups. One use case could be fault tolerant training, where a process group may be destroyed and then a new one initialized during runtime. In this case, it’s critical to synchronize the trainer processes using some means other than torch.distributed primitives _after_ calling destroy and before subsequently initializing. This behavior is currently unsupported/untested, due to the difficulty of achieving this synchronization, and is considered a known issue. Please file a github issue or RFC if this is a use case that’s blocking you.
* * *
## Groups[#](https://docs.pytorch.org/docs/stable/distributed.html#groups "Link to this heading")
By default collectives operate on the default group (also called the world) and require all processes to enter the distributed function call. However, some workloads can benefit from more fine-grained communication. This is where distributed groups come into play. [`new_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.new_group "torch.distributed.new_group") function can be used to create new groups, with arbitrary subsets of all processes. It returns an opaque group handle that can be given as a `group` argument to all collectives (collectives are distributed functions to exchange information in certain well-known programming patterns).

torch.distributed.new_group(_ranks =None_, _timeout =None_, _backend =None_, _pg_options =None_, _use_local_synchronization =False_, _group_desc =None_, _device_id =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L5364)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.new_group "Link to this definition")

Create a new distributed group.
This function requires that all processes in the main group (i.e. all processes that are part of the distributed job) enter this function, even if they are not going to be members of the group. Additionally, groups should be created in the same order in all processes.
Warning
Safe concurrent usage: When using multiple process groups with the `NCCL` backend, the user must ensure a globally consistent execution order of collectives across ranks.
If multiple threads within a process issue collectives, explicit synchronization is necessary to ensure consistent ordering.
When using async variants of torch.distributed communication APIs, a work object is returned and the communication kernel is enqueued on a separate CUDA stream, allowing overlap of communication and computation. Once one or more async ops have been issued on one process group, they must be synchronized with other cuda streams by calling work.wait() before using another process group.
See Using multiple NCCL communicators concurrently <https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html#using-multiple-nccl-communicators-concurrently> for more details.

Parameters:

  * **ranks** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _]_) – List of ranks of group members. If `None`, will be set to all ranks. Default is `None`.
  * **timeout** (_timedelta_ _,__optional_) – see init_process_group for details and default value.
  * **backend** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _or_[ _Backend_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend "torch.distributed.Backend") _,__optional_) – The backend to use. Depending on build-time configurations, valid values are `gloo` and `nccl`. By default uses the same backend as the global group. This field should be given as a lowercase string (e.g., `"gloo"`), which can also be accessed via [`Backend`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend "torch.distributed.Backend") attributes (e.g., `Backend.GLOO`). If `None` is passed in, the backend corresponding to the default process group will be used. Default is `None`.
  * **pg_options** (_ProcessGroupOptions_ _,__optional_) – process group options specifying what additional options need to be passed in during the construction of specific process groups. i.e. for the `nccl` backend, `is_high_priority_stream` can be specified so that process group can pick up high priority cuda streams. For other available options to config nccl, See <https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/types.html#ncclconfig-tuse_local_synchronization> (bool, optional): perform a group-local barrier at the end of the process group creation. This is different in that non-member ranks don’t need to call into API and don’t join the barrier.
  * **group_desc** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__optional_) – a string to describe the process group.
  * **device_id** ([_torch.device_](https://docs.pytorch.org/docs/stable/tensor_attributes.html#torch.device "torch.device") _,__optional_) – a single, specific device to “bind” this process to, The new_group call will try to initialize a communication backend immediately for the device if this field is given.


Returns:

A handle of distributed group that can be given to collective calls or GroupMember.NON_GROUP_MEMBER if the rank is not part of `ranks`.
N.B. use_local_synchronization doesn’t work with MPI.
N.B. While use_local_synchronization=True can be significantly faster with larger clusters and small process groups, care must be taken since it changes cluster behavior as non-member ranks don’t join the group barrier().
N.B. use_local_synchronization=True can lead to deadlocks when each rank creates multiple overlapping process groups. To avoid that, make sure all ranks follow the same global creation order.

torch.distributed.distributed_c10d.shrink_group(_ranks_to_exclude_ , _group =None_, _shrink_flags =0_, _pg_options =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L5844)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.shrink_group "Link to this definition")

Shrinks a process group by excluding specified ranks.
Creates and returns a new, smaller process group comprising only the ranks from the original group that were not in the `ranks_to_exclude` list.

Parameters:

  * **ranks_to_exclude** (_List_ _[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _]_) – A list of ranks from the original `group` to exclude from the new group.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _,__optional_) – The process group to shrink. If `None`, the default process group is used. Defaults to `None`.
  * **shrink_flags** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Flags to control the shrinking behavior. Can be `SHRINK_DEFAULT` (default) or `SHRINK_ABORT`. `SHRINK_ABORT` will attempt to terminate ongoing operations in the parent communicator before shrinking. Defaults to `SHRINK_DEFAULT`.
  * **pg_options** (_ProcessGroupOptions_ _,__optional_) – Backend-specific options to apply to the shrunken process group. If provided, the backend will use these options when creating the new group. If omitted, the new group inherits defaults from the parent.


Returns:

a new group comprised of the remaining ranks. If the default group was shrunk, the returned group becomes the new default group.

Return type:

[ProcessGroup](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup")

Raises:

  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError "\(in Python v3.14\)") – if the group’s backend does not support shrinking.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "\(in Python v3.14\)") – if `ranks_to_exclude` is invalid (empty, out of bounds,
  * **duplicates****, or****excludes all ranks****)****.** –
  * [**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError "\(in Python v3.14\)") – if an excluded rank calls this function or the backend
  * **fails the operation.** –


Notes
  * Only non-excluded ranks should call this function; excluded ranks must not participate in the shrink operation.
  * Shrinking the default group destroys all other process groups since rank reassignment makes them inconsistent.


torch.distributed.get_group_rank(_group_ , _global_rank_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1052)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_group_rank "Link to this definition")

Translate a global rank into a group rank.
`global_rank` must be part of `group` otherwise this raises RuntimeError.

Parameters:

  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup")) – ProcessGroup to find the relative rank.
  * **global_rank** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Global rank to query.


Returns:

Group rank of `global_rank` relative to `group`

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")
N.B. calling this function on the default process group returns identity

torch.distributed.get_global_rank(_group_ , _group_rank_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1080)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_global_rank "Link to this definition")

Translate a group rank into a global rank.
`group_rank` must be part of group otherwise this raises RuntimeError.

Parameters:

  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup")) – ProcessGroup to find the global rank from.
  * **group_rank** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Group rank to query.


Returns:

Global rank of `group_rank` relative to `group`

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")
N.B. calling this function on the default process group returns identity

torch.distributed.get_process_group_ranks(_group_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L1118)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_process_group_ranks "Link to this definition")

Get all ranks associated with `group`.

Parameters:

**group** (_Optional_ _[_[_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _]_) – ProcessGroup to get all ranks from. If None, the default process group will be used.

Returns:

List of global ranks ordered by group rank.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")]
## DeviceMesh[#](https://docs.pytorch.org/docs/stable/distributed.html#devicemesh "Link to this heading")
DeviceMesh is a higher level abstraction that manages process groups (or NCCL communicators). It allows user to easily create inter node and intra node process groups without worrying about how to set up the ranks correctly for different sub process groups, and it helps manage those distributed process group easily. [`init_device_mesh()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.init_device_mesh "torch.distributed.device_mesh.init_device_mesh") function can be used to create new DeviceMesh, with a mesh shape describing the device topology.

_class_ torch.distributed.device_mesh.DeviceMesh(_device_type_ , _mesh =None_, _*_ , _mesh_dim_names =None_, _backend_override =None_, __init_backend =True_, __rank =None_, __layout =None_, __rank_map =None_, __root_mesh =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L151)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "Link to this definition")

DeviceMesh represents a mesh of devices, where layout of devices could be represented as a n-d dimension array, and each value of the n-d dimensional array is the global id of the default process group ranks.
DeviceMesh could be used to setup the N dimensional device connections across the cluster, and manage the ProcessGroups for N dimensional parallelisms. Communications could happen on each dimension of the DeviceMesh separately. DeviceMesh respects the device that user selects already (i.e. if user call torch.cuda.set_device before the DeviceMesh initialization), and will select/set the device for the current process if user does not set the device beforehand. Note that manual device selection should happen BEFORE the DeviceMesh initialization.
DeviceMesh can also be used as a context manager when using together with DTensor APIs.
Note
DeviceMesh follows SPMD programming model, which means the same PyTorch Python program is running on all processes/ranks in the cluster. Therefore, users need to make sure the mesh array (which describes the layout of devices) should be identical across all ranks. Inconsistent mesh will lead to silent hang.

Parameters:

  * **device_type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The device type of the mesh. Currently supports: “cpu”, “cuda/cuda-like”.
  * **mesh** (_ndarray_) – A multi-dimensional array or an integer tensor describing the layout of devices, where the IDs are global IDs of the default process group.
  * **_rank** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – (experimental/internal) The global rank of the current process. If not provided, it will be inferred from the default process group.


Returns:

A [`DeviceMesh`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh") object representing the device layout.

Return type:

[DeviceMesh](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh")
The following program runs on each process/rank in an SPMD manner. In this example, we have 2 hosts with 4 GPUs each. A reduction over the first dimension of mesh will reduce across columns (0, 4), .. and (3, 7), a reduction over the second dimension of mesh reduces across rows (0, 1, 2, 3) and (4, 5, 6, 7).
Example:

```
>>> from torch.distributed.device_mesh import DeviceMesh
>>>
>>> # Initialize device mesh as (2, 4) to represent the topology
>>> # of cross-host(dim 0), and within-host (dim 1).
>>> mesh = DeviceMesh(device_type="cuda", mesh=[[0, 1, 2, 3],[4, 5, 6, 7]])

```
Copy to clipboard

_property_ device_type _:[ str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.device_type "Link to this definition")

Returns the device type of the mesh.

_static_ from_group(_group_ , _device_type_ , _mesh =None_, _*_ , _mesh_dim_names =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L1026)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.from_group "Link to this definition")

Constructs a [`DeviceMesh`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh") with `device_type` from an existing `ProcessGroup` or a list of existing `ProcessGroup`.
The constructed device mesh has number of dimensions equal to the number of groups passed. For example, if a single process group is passed in, the resulted DeviceMesh is a 1D mesh. If a list of 2 process groups is passed in, the resulted DeviceMesh is a 2D mesh.
If more than one group is passed, then the `mesh` and `mesh_dim_names` arguments are required. The order of the process groups passed in determines the topology of the mesh. For example, the first process group will be the 0th dimension of the DeviceMesh. The mesh tensor passed in must have the same number of dimensions as the number of process groups passed in, and the order of the dimensions in the mesh tensor must match the order in the process groups passed in.

Parameters:

  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _or_[ _list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _]_) – the existing ProcessGroup or a list of existing ProcessGroups.
  * **device_type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The device type of the mesh. Currently supports: “cpu”, “cuda/cuda-like”. Passing in a device type with a GPU index, such as “cuda:0”, is not allowed.
  * **mesh** ([_torch.Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _or_ _ArrayLike_ _,__optional_) – A multi-dimensional array or an integer tensor describing the layout of devices, where the IDs are global IDs of the default process group. Default is None.
  * **mesh_dim_names** ([_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)") _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _,__...__]__,__optional_) – A tuple of mesh dimension names to assign to each dimension of the multi-dimensional array describing the layout of devices. Its length must match the length of mesh_shape. Each string in mesh_dim_names must be unique. Default is None.


Returns:

A [`DeviceMesh`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh") object representing the device layout.

Return type:

[DeviceMesh](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh "torch.distributed.device_mesh.DeviceMesh")

get_all_groups()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L785)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_all_groups "Link to this definition")

Returns a list of ProcessGroups for all mesh dimensions.

Returns:

A list of `ProcessGroup` object.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup")]

get_coordinate()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L1206)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_coordinate "Link to this definition")

Return the relative indices of this rank relative to all dimensions of the mesh. If this rank is not part of the mesh, return None.

Return type:

[tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)"), …] | None

get_group(_mesh_dim =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L736)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_group "Link to this definition")

Returns the single ProcessGroup specified by mesh_dim, or, if mesh_dim is not specified and the DeviceMesh is 1-dimensional, returns the only ProcessGroup in the mesh.

Parameters:

  * **mesh_dim** (_str/python:int_ _,__optional_) – it can be the name of the mesh dimension or the index
  * **None.** (_of the mesh dimension. Default is_) –


Returns:

A `ProcessGroup` object.

Return type:

[_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup")

get_local_rank(_mesh_dim =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L1143)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_local_rank "Link to this definition")

Returns the local rank of the given mesh_dim of the DeviceMesh.

Parameters:

  * **mesh_dim** (_str/python:int_ _,__optional_) – it can be the name of the mesh dimension or the index
  * **None.** (_of the mesh dimension. Default is_) –


Returns:

An integer denotes the local rank.

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")
The following program runs on each process/rank in an SPMD manner. In this example, we have 2 hosts with 4 GPUs each. Calling mesh_2d.get_local_rank(mesh_dim=0) on rank 0, 1, 2, 3 would return 0. Calling mesh_2d.get_local_rank(mesh_dim=0) on rank 4, 5, 6, 7 would return 1. Calling mesh_2d.get_local_rank(mesh_dim=1) on rank 0, 4 would return 0. Calling mesh_2d.get_local_rank(mesh_dim=1) on rank 1, 5 would return 1. Calling mesh_2d.get_local_rank(mesh_dim=1) on rank 2, 6 would return 2. Calling mesh_2d.get_local_rank(mesh_dim=1) on rank 3, 7 would return 3.
Example:

```
>>> from torch.distributed.device_mesh import DeviceMesh
>>>
>>> # Initialize device mesh as (2, 4) to represent the topology
>>> # of cross-host(dim 0), and within-host (dim 1).
>>> mesh = DeviceMesh(device_type="cuda", mesh=[[0, 1, 2, 3],[4, 5, 6, 7]])

```
Copy to clipboard

get_rank()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/device_mesh.py#L1137)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_rank "Link to this definition")

Returns the current global rank.

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")

_property_ mesh _:[ Tensor](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")_[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.mesh "Link to this definition")

Returns the tensor representing the layout of devices.

_property_ mesh_dim_names _:[ tuple](https://docs.python.org/3/library/stdtypes.html#tuple "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)"),...]|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")_[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.mesh_dim_names "Link to this definition")

Returns the names of mesh dimensions.
## Point-to-point communication[#](https://docs.pytorch.org/docs/stable/distributed.html#point-to-point-communication "Link to this heading")

torch.distributed.send(_tensor_ , _dst =None_, _group =None_, _tag =0_, _group_dst =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2600)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send "Link to this definition")

Send a tensor synchronously.
Warning
`tag` is not supported with the NCCL backend.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to send.
  * **dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Destination rank on global process group (regardless of `group` argument). Destination rank should not be the same as the rank of the current process.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **tag** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Tag to match send with remote recv
  * **group_dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `dst` and `group_dst`.


torch.distributed.recv(_tensor_ , _src =None_, _group =None_, _tag =0_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2632)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv "Link to this definition")

Receives a tensor synchronously.
Warning
`tag` is not supported with the NCCL backend.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to fill with received data.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Source rank on global process group (regardless of `group` argument). Will receive from any process if unspecified.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **tag** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Tag to match recv with remote send
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `src` and `group_src`.


Returns:

Sender rank -1, if not part of the group

Return type:

[int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")
[`isend()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.isend "torch.distributed.isend") and [`irecv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.irecv "torch.distributed.irecv") return distributed request objects when used. In general, the type of this object is unspecified as they should never be created manually, but they are guaranteed to support two methods:
  * `is_completed()` - returns True if the operation has finished
  * `wait()` - will block the process until the operation is finished. `is_completed()` is guaranteed to return True once it returns.


torch.distributed.isend(_tensor_ , _dst =None_, _group =None_, _tag =0_, _group_dst =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2510)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.isend "Link to this definition")

Send a tensor asynchronously.
Warning
Modifying `tensor` before the request completes causes undefined behavior.
Warning
`tag` is not supported with the NCCL backend.
Unlike send, which is blocking, isend allows src == dst rank, i.e. send to self.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to send.
  * **dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Destination rank on global process group (regardless of `group` argument)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **tag** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Tag to match send with remote recv
  * **group_dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `dst` and `group_dst`


Returns:

A distributed request object. None, if not part of the group

Return type:

[_Work_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work "torch.distributed.distributed_c10d.Work") | None

torch.distributed.irecv(_tensor_ , _src =None_, _group =None_, _tag =0_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2555)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.irecv "Link to this definition")

Receives a tensor asynchronously.
Warning
`tag` is not supported with the NCCL backend.
Unlike recv, which is blocking, irecv allows src == dst rank, i.e. recv from self.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to fill with received data.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Source rank on global process group (regardless of `group` argument). Will receive from any process if unspecified.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **tag** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Tag to match recv with remote send
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `src` and `group_src`.


Returns:

A distributed request object. None, if not part of the group

Return type:

[_Work_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work "torch.distributed.distributed_c10d.Work") | None

torch.distributed.send_object_list(_object_list_ , _dst =None_, _group =None_, _device =None_, _group_dst =None_, _use_batch =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3463)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send_object_list "Link to this definition")

Sends picklable objects in `object_list` synchronously.
Similar to [`send()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send "torch.distributed.send"), but Python objects can be passed in. Note that all objects in `object_list` must be picklable in order to be sent.

Parameters:

  * **object_list** (_List_ _[__Any_ _]_) – List of input objects to sent. Each object must be picklable. Receiver must provide lists of equal sizes.
  * **dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Destination rank to send `object_list` to. Destination rank is based on global process group (regardless of `group` argument)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _|__None_) – (ProcessGroup, optional): The process group to work on. If None, the default process group will be used. Default is `None`.
  * **device** (`torch.device`, optional) – If not None, the objects are serialized and converted to tensors which are moved to the `device` before sending. Default is `None`.
  * **group_dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Must specify one of `dst` and `group_dst` but not both
  * **use_batch** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – If True, use batch p2p operations instead of regular send operations. This avoids initializing 2-rank communicators and uses existing entire group communicators. See batch_isend_irecv for usage and assumptions. Default is `False`.


Returns:

`None`.
Note
For NCCL-based process groups, internal tensor representations of objects must be moved to the GPU device before communication takes place. In this case, the device used is given by `torch.cuda.current_device()` and it is the user’s responsibility to ensure that this is set so that each rank has an individual GPU, via `torch.cuda.set_device()`.
Warning
Object collectives have a number of serious performance and scalability limitations. See [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives) for details.
Warning
[`send_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send_object_list "torch.distributed.send_object_list") uses `pickle` module implicitly, which is known to be insecure. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling. Only call this function with data you trust.
Warning
Calling [`send_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send_object_list "torch.distributed.send_object_list") with GPU tensors is not well supported and inefficient as it incurs GPU -> CPU transfer since tensors would be pickled. Please consider using [`send()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send "torch.distributed.send") instead.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> # Assumes backend is not NCCL
>>> device = torch.device("cpu")
>>> if dist.get_rank() == 0:
>>>     # Assumes world_size of 2.
>>>     objects = ["foo", 12, {1: 2}] # any picklable object
>>>     dist.send_object_list(objects, dst=1, device=device)
>>> else:
>>>     objects = [None, None, None]
>>>     dist.recv_object_list(objects, src=0, device=device)
>>> objects
['foo', 12, {1: 2}]

```
Copy to clipboard

torch.distributed.recv_object_list(_object_list_ , _src =None_, _group =None_, _device =None_, _group_src =None_, _use_batch =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3581)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv_object_list "Link to this definition")

Receives picklable objects in `object_list` synchronously.
Similar to [`recv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv "torch.distributed.recv"), but can receive Python objects.

Parameters:

  * **object_list** (_List_ _[__Any_ _]_) – List of objects to receive into. Must provide a list of sizes equal to the size of the list being sent.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Source rank from which to recv `object_list`. Source rank is based on global process group (regardless of `group` argument) Will receive from any rank if set to None. Default is `None`.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _|__None_) – (ProcessGroup, optional): The process group to work on. If None, the default process group will be used. Default is `None`.
  * **device** (`torch.device`, optional) – If not None, receives on this device. Default is `None`.
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `src` and `group_src`.
  * **use_batch** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – If True, use batch p2p operations instead of regular send operations. This avoids initializing 2-rank communicators and uses existing entire group communicators. See batch_isend_irecv for usage and assumptions. Default is `False`.


Returns:

Sender rank. -1 if rank is not part of the group. If rank is part of the group, `object_list` will contain the sent objects from `src` rank.
Note
For NCCL-based process groups, internal tensor representations of objects must be moved to the GPU device before communication takes place. In this case, the device used is given by `torch.cuda.current_device()` and it is the user’s responsibility to ensure that this is set so that each rank has an individual GPU, via `torch.cuda.set_device()`.
Warning
Object collectives have a number of serious performance and scalability limitations. See [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives) for details.
Warning
[`recv_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv_object_list "torch.distributed.recv_object_list") uses `pickle` module implicitly, which is known to be insecure. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling. Only call this function with data you trust.
Warning
Calling [`recv_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv_object_list "torch.distributed.recv_object_list") with GPU tensors is not well supported and inefficient as it incurs GPU -> CPU transfer since tensors would be pickled. Please consider using [`recv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv "torch.distributed.recv") instead.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> # Assumes backend is not NCCL
>>> device = torch.device("cpu")
>>> if dist.get_rank() == 0:
>>>     # Assumes world_size of 2.
>>>     objects = ["foo", 12, {1: 2}] # any picklable object
>>>     dist.send_object_list(objects, dst=1, device=device)
>>> else:
>>>     objects = [None, None, None]
>>>     dist.recv_object_list(objects, src=0, device=device)
>>> objects
['foo', 12, {1: 2}]

```
Copy to clipboard

torch.distributed.batch_isend_irecv(_p2p_op_list_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2847)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.batch_isend_irecv "Link to this definition")

Send or Receive a batch of tensors asynchronously and return a list of requests.
Process each of the operations in `p2p_op_list` and return the corresponding requests. NCCL, Gloo, and UCC backend are currently supported.

Parameters:

**p2p_op_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_P2POp_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.P2POp "torch.distributed.distributed_c10d.P2POp") _]_) – A list of point-to-point operations(type of each operator is `torch.distributed.P2POp`). The order of the isend/irecv in the list matters and it needs to match with corresponding isend/irecv on the remote end.

Returns:

A list of distributed request objects returned by calling the corresponding op in the op_list.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[_Work_](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work "torch.distributed.distributed_c10d.Work")]
Examples

```
>>> send_tensor = torch.arange(2, dtype=torch.float32) + 2 * rank
>>> recv_tensor = torch.randn(2, dtype=torch.float32)
>>> send_op = dist.P2POp(dist.isend, send_tensor, (rank + 1) % world_size)
>>> recv_op = dist.P2POp(
...     dist.irecv, recv_tensor, (rank - 1 + world_size) % world_size
... )
>>> reqs = batch_isend_irecv([send_op, recv_op])
>>> for req in reqs:
>>>     req.wait()
>>> recv_tensor
tensor([2, 3])     # Rank 0
tensor([0, 1])     # Rank 1

```
Copy to clipboard
Note
Note that when this API is used with the NCCL PG backend, users must set the current GPU device with torch.cuda.set_device, otherwise it will lead to unexpected hang issues.
In addition, if this API is the first collective call in the `group` passed to `dist.P2POp`, all ranks of the `group` must participate in this API call; otherwise, the behavior is undefined. If this API call is not the first collective call in the `group`, batched P2P operations involving only a subset of ranks of the `group` are allowed.

_class_ torch.distributed.P2POp(_op_ , _tensor_ , _peer =None_, _group =None_, _tag =0_, _group_peer =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L504)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.P2POp "Link to this definition")

A class to build point-to-point operations for `batch_isend_irecv`.
This class builds the type of P2P operation, communication buffer, peer rank, Process Group, and tag. Instances of this class will be passed to `batch_isend_irecv` for point-to-point communications.

Parameters:

  * **op** (_Callable_) – A function to send data to or receive data from a peer process. The type of `op` is either `torch.distributed.isend` or `torch.distributed.irecv`.
  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to send or receive.
  * **peer** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination or source rank.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **tag** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Tag to match send with recv.
  * **group_peer** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination or source rank.


## Synchronous and asynchronous collective operations[#](https://docs.pytorch.org/docs/stable/distributed.html#synchronous-and-asynchronous-collective-operations "Link to this heading")
Every collective operation function supports the following two kinds of operations, depending on the setting of the `async_op` flag passed into the collective:
**Synchronous operation** - the default mode, when `async_op` is set to `False`. When the function returns, it is guaranteed that the collective operation is performed. In the case of CUDA operations, it is not guaranteed that the CUDA operation is completed, since CUDA operations are asynchronous. For CPU collectives, any further function calls utilizing the output of the collective call will behave as expected. For CUDA collectives, function calls utilizing the output on the same CUDA stream will behave as expected. Users must take care of synchronization under the scenario of running under different streams. For details on CUDA semantics such as stream synchronization, see [CUDA Semantics](https://pytorch.org/docs/stable/notes/cuda.html). See the below script to see examples of differences in these semantics for CPU and CUDA operations.
**Asynchronous operation** - when `async_op` is set to True. The collective operation function returns a distributed request object. In general, you don’t need to create it manually and it is guaranteed to support two methods:
  * `is_completed()` - in the case of CPU collectives, returns `True` if completed. In the case of CUDA operations, returns `True` if the operation has been successfully enqueued onto a CUDA stream and the output can be utilized on the default stream without further synchronization.
  * `wait()` - in the case of CPU collectives, will block the process until the operation is completed. In the case of CUDA collectives, will block the currently active CUDA stream until the operation is completed (but will not block the CPU).
  * `get_future()` - returns `torch._C.Future` object. Supported for NCCL, also supported for most operations on GLOO and MPI, except for peer to peer operations. Note: as we continue adopting Futures and merging APIs, `get_future()` call might become redundant.


**Example**
The following code can serve as a reference regarding semantics for CUDA operations when using distributed collectives. It shows the explicit need to synchronize when using collective outputs on different CUDA streams:

```
# Code runs on each rank.
dist.init_process_group("nccl", rank=rank, world_size=2)
output = torch.tensor([rank]).cuda(rank)
s = torch.cuda.Stream()
handle = dist.all_reduce(output, async_op=True)
# Wait ensures the operation is enqueued, but not necessarily complete.
handle.wait()
# Using result on non-default stream.
with torch.cuda.stream(s):
    s.wait_stream(torch.cuda.default_stream())
    output.add_(100)
if rank == 0:
    # if the explicit call to wait_stream was omitted, the output below will be
    # non-deterministically 1 or 101, depending on whether the allreduce overwrote
    # the value after the add completed.
    print(output)

```
Copy to clipboard
## Collective functions[#](https://docs.pytorch.org/docs/stable/distributed.html#collective-functions "Link to this heading")

torch.distributed.broadcast(_tensor_ , _src =None_, _group =None_, _async_op =False_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2926)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast "Link to this definition")

Broadcasts the tensor to the whole group.
`tensor` must have the same number of elements in all processes participating in the collective.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Data to be sent if `src` is the rank of current process, and tensor to be used to save received data otherwise.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Source rank on global process group (regardless of `group` argument).
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Source rank on `group`. Must specify one of `group_src` and `src` but not both.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group

torch.distributed.broadcast_object_list(_object_list_ , _src =None_, _group =None_, _device =None_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3723)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast_object_list "Link to this definition")

Broadcasts picklable objects in `object_list` to the whole group.
Similar to [`broadcast()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast "torch.distributed.broadcast"), but Python objects can be passed in. Note that all objects in `object_list` must be picklable in order to be broadcasted.

Parameters:

  * **object_list** (_List_ _[__Any_ _]_) – List of input objects to broadcast. Each object must be picklable. Only objects on the `src` rank will be broadcast, but each rank must provide lists of equal sizes.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Source rank from which to broadcast `object_list`. Source rank is based on global process group (regardless of `group` argument)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _|__None_) – (ProcessGroup, optional): The process group to work on. If None, the default process group will be used. Default is `None`.
  * **device** (`torch.device`, optional) – If not None, the objects are serialized and converted to tensors which are moved to the `device` before broadcasting. Default is `None`.
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Source rank on `group`. Must not specify one of `group_src` and `src` but not both.


Returns:

`None`. If rank is part of the group, `object_list` will contain the broadcasted objects from `src` rank.
Note
For NCCL-based process groups, internal tensor representations of objects must be moved to the GPU device before communication takes place. In this case, the device used is given by `torch.cuda.current_device()` and it is the user’s responsibility to ensure that this is set so that each rank has an individual GPU, via `torch.cuda.set_device()`.
Note
Note that this API differs slightly from the [`broadcast()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast "torch.distributed.broadcast") collective since it does not provide an `async_op` handle and thus will be a blocking call.
Warning
Object collectives have a number of serious performance and scalability limitations. See [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives) for details.
Warning
[`broadcast_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast_object_list "torch.distributed.broadcast_object_list") uses `pickle` module implicitly, which is known to be insecure. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling. Only call this function with data you trust.
Warning
Calling [`broadcast_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast_object_list "torch.distributed.broadcast_object_list") with GPU tensors is not well supported and inefficient as it incurs GPU -> CPU transfer since tensors would be pickled. Please consider using [`broadcast()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast "torch.distributed.broadcast") instead.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> if dist.get_rank() == 0:
>>>     # Assumes world_size of 3.
>>>     objects = ["foo", 12, {1: 2}] # any picklable object
>>> else:
>>>     objects = [None, None, None]
>>> # Assumes backend is not NCCL
>>> device = torch.device("cpu")
>>> dist.broadcast_object_list(objects, src=0, device=device)
>>> objects
['foo', 12, {1: 2}]

```
Copy to clipboard

torch.distributed.all_reduce(_tensor_ , _op= <RedOpType.SUM: 0>_, _group=None_ , _async_op=False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L2978)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_reduce "Link to this definition")

Reduces the tensor data across all machines in a way that all get the final result.
After the call `tensor` is going to be bitwise identical in all processes.
Complex tensors are supported.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Input and output of the collective. The function operates in-place.
  * **op** (_optional_) – One of the values from `torch.distributed.ReduceOp` enum. Specifies an operation used for element-wise reductions.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group
Examples

```
>>> # All tensors below are of torch.int64 type.
>>> # We have 2 process groups, 2 ranks.
>>> device = torch.device(f"cuda:{rank}")
>>> tensor = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank
>>> tensor
tensor([1, 2], device='cuda:0') # Rank 0
tensor([3, 4], device='cuda:1') # Rank 1
>>> dist.all_reduce(tensor, op=ReduceOp.SUM)
>>> tensor
tensor([4, 6], device='cuda:0') # Rank 0
tensor([4, 6], device='cuda:1') # Rank 1

```
Copy to clipboard

```
>>> # All tensors below are of torch.cfloat type.
>>> # We have 2 process groups, 2 ranks.
>>> tensor = torch.tensor(
...     [1 + 1j, 2 + 2j], dtype=torch.cfloat, device=device
... ) + 2 * rank * (1 + 1j)
>>> tensor
tensor([1.+1.j, 2.+2.j], device='cuda:0') # Rank 0
tensor([3.+3.j, 4.+4.j], device='cuda:1') # Rank 1
>>> dist.all_reduce(tensor, op=ReduceOp.SUM)
>>> tensor
tensor([4.+4.j, 6.+6.j], device='cuda:0') # Rank 0
tensor([4.+4.j, 6.+6.j], device='cuda:1') # Rank 1

```
Copy to clipboard

torch.distributed.reduce(_tensor_ , _dst=None_ , _op= <RedOpType.SUM: 0>_, _group=None_ , _async_op=False_ , _group_dst=None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3148)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce "Link to this definition")

Reduces the tensor data across all machines.
Only the process with rank `dst` is going to receive the final result.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Input and output of the collective. The function operates in-place.
  * **dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Destination rank on global process group (regardless of `group` argument)
  * **op** (_optional_) – One of the values from `torch.distributed.ReduceOp` enum. Specifies an operation used for element-wise reductions.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op
  * **group_dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Destination rank on `group`. Must specify one of `group_dst` and `dst` but not both.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group

torch.distributed.all_gather(_tensor_list_ , _tensor_ , _group =None_, _async_op =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3990)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather "Link to this definition")

Gathers tensors from the whole group in a list.
Complex and uneven sized tensors are supported.

Parameters:

  * **tensor_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _]_) – Output list. It should contain correctly-sized tensors to be used for output of the collective. Uneven sized tensors are supported.
  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to be broadcast from current process.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group
Examples

```
>>> # All tensors below are of torch.int64 dtype.
>>> # We have 2 process groups, 2 ranks.
>>> device = torch.device(f"cuda:{rank}")
>>> tensor_list = [
...     torch.zeros(2, dtype=torch.int64, device=device) for _ in range(2)
... ]
>>> tensor_list
[tensor([0, 0], device='cuda:0'), tensor([0, 0], device='cuda:0')] # Rank 0
[tensor([0, 0], device='cuda:1'), tensor([0, 0], device='cuda:1')] # Rank 1
>>> tensor = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank
>>> tensor
tensor([1, 2], device='cuda:0') # Rank 0
tensor([3, 4], device='cuda:1') # Rank 1
>>> dist.all_gather(tensor_list, tensor)
>>> tensor_list
[tensor([1, 2], device='cuda:0'), tensor([3, 4], device='cuda:0')] # Rank 0
[tensor([1, 2], device='cuda:1'), tensor([3, 4], device='cuda:1')] # Rank 1

```
Copy to clipboard

```
>>> # All tensors below are of torch.cfloat dtype.
>>> # We have 2 process groups, 2 ranks.
>>> tensor_list = [
...     torch.zeros(2, dtype=torch.cfloat, device=device) for _ in range(2)
... ]
>>> tensor_list
[tensor([0.+0.j, 0.+0.j], device='cuda:0'), tensor([0.+0.j, 0.+0.j], device='cuda:0')] # Rank 0
[tensor([0.+0.j, 0.+0.j], device='cuda:1'), tensor([0.+0.j, 0.+0.j], device='cuda:1')] # Rank 1
>>> tensor = torch.tensor(
...     [1 + 1j, 2 + 2j], dtype=torch.cfloat, device=device
... ) + 2 * rank * (1 + 1j)
>>> tensor
tensor([1.+1.j, 2.+2.j], device='cuda:0') # Rank 0
tensor([3.+3.j, 4.+4.j], device='cuda:1') # Rank 1
>>> dist.all_gather(tensor_list, tensor)
>>> tensor_list
[tensor([1.+1.j, 2.+2.j], device='cuda:0'), tensor([3.+3.j, 4.+4.j], device='cuda:0')] # Rank 0
[tensor([1.+1.j, 2.+2.j], device='cuda:1'), tensor([3.+3.j, 4.+4.j], device='cuda:1')] # Rank 1

```
Copy to clipboard

torch.distributed.all_gather_into_tensor(_output_tensor_ , _input_tensor_ , _group =None_, _async_op =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4090)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather_into_tensor "Link to this definition")

Gather tensors from all ranks and put them in a single output tensor.
This function requires all tensors to be the same size on each process.

Parameters:

  * **output_tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Output tensor to accommodate tensor elements from all ranks. It must be correctly sized to have one of the following forms: (i) a concatenation of all the input tensors along the primary dimension; for definition of “concatenation”, see `torch.cat()`; (ii) a stack of all the input tensors along the primary dimension; for definition of “stack”, see `torch.stack()`. Examples below may better explain the supported output forms.
  * **input_tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Tensor to be gathered from current rank. Different from the `all_gather` API, the input tensors in this API must have the same size across all ranks.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group
Examples

```
>>> # All tensors below are of torch.int64 dtype and on CUDA devices.
>>> # We have two ranks.
>>> device = torch.device(f"cuda:{rank}")
>>> tensor_in = torch.arange(2, dtype=torch.int64, device=device) + 1 + 2 * rank
>>> tensor_in
tensor([1, 2], device='cuda:0') # Rank 0
tensor([3, 4], device='cuda:1') # Rank 1
>>> # Output in concatenation form
>>> tensor_out = torch.zeros(world_size * 2, dtype=torch.int64, device=device)
>>> dist.all_gather_into_tensor(tensor_out, tensor_in)
>>> tensor_out
tensor([1, 2, 3, 4], device='cuda:0') # Rank 0
tensor([1, 2, 3, 4], device='cuda:1') # Rank 1
>>> # Output in stack form
>>> tensor_out2 = torch.zeros(world_size, 2, dtype=torch.int64, device=device)
>>> dist.all_gather_into_tensor(tensor_out2, tensor_in)
>>> tensor_out2
tensor([[1, 2],
        [3, 4]], device='cuda:0') # Rank 0
tensor([[1, 2],
        [3, 4]], device='cuda:1') # Rank 1

```
Copy to clipboard

torch.distributed.all_gather_object(_object_list_ , _obj_ , _group =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3237)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather_object "Link to this definition")

Gathers picklable objects from the whole group into a list.
Similar to [`all_gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather "torch.distributed.all_gather"), but Python objects can be passed in. Note that the object must be picklable in order to be gathered.

Parameters:

  * **object_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[__Any_ _]_) – Output list. It should be correctly sized as the size of the group for this collective and will contain the output.
  * **obj** (_Any_) – Pickable Python object to be broadcast from current process.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used. Default is `None`.


Returns:

None. If the calling rank is part of this group, the output of the collective will be populated into the input `object_list`. If the calling rank is not part of the group, the passed in `object_list` will be unmodified.
Note
Note that this API differs slightly from the [`all_gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather "torch.distributed.all_gather") collective since it does not provide an `async_op` handle and thus will be a blocking call.
Note
For NCCL-based processed groups, internal tensor representations of objects must be moved to the GPU device before communication takes place. In this case, the device used is given by `torch.cuda.current_device()` and it is the user’s responsibility to ensure that this is set so that each rank has an individual GPU, via `torch.cuda.set_device()`.
Warning
Object collectives have a number of serious performance and scalability limitations. See [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives) for details.
Warning
[`all_gather_object()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather_object "torch.distributed.all_gather_object") uses `pickle` module implicitly, which is known to be insecure. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling. Only call this function with data you trust.
Warning
Calling [`all_gather_object()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather_object "torch.distributed.all_gather_object") with GPU tensors is not well supported and inefficient as it incurs GPU -> CPU transfer since tensors would be pickled. Please consider using [`all_gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather "torch.distributed.all_gather") instead.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> # Assumes world_size of 3.
>>> gather_objects = ["foo", 12, {1: 2}] # any picklable object
>>> output = [None for _ in gather_objects]
>>> dist.all_gather_object(output, gather_objects[dist.get_rank()])
>>> output
['foo', 12, {1: 2}]

```
Copy to clipboard

torch.distributed.gather(_tensor_ , _gather_list =None_, _dst =None_, _group =None_, _async_op =False_, _group_dst =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4329)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather "Link to this definition")

Gathers a list of tensors in a single process.
This function requires all tensors to be the same size on each process.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Input tensor.
  * **gather_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _]__,__optional_) – List of appropriately, same-sized tensors to use for gathered data (default is None, must be specified on the destination rank)
  * **dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on global process group (regardless of `group` argument). (If both `dst` and `group_dst` are None, default is global rank 0)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op
  * **group_dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `dst` and `group_dst`


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group
Note
Note that all Tensors in gather_list must have the same size.

Example::


```
>>> # We have 2 process groups, 2 ranks.
>>> tensor_size = 2
>>> device = torch.device(f'cuda:{rank}')
>>> tensor = torch.ones(tensor_size, device=device) + rank
>>> if dist.get_rank() == 0:
>>>     gather_list = [torch.zeros_like(tensor, device=device) for i in range(2)]
>>> else:
>>>     gather_list = None
>>> dist.gather(tensor, gather_list, dst=0)
>>> # Rank 0 gets gathered data.
>>> gather_list
[tensor([1., 1.], device='cuda:0'), tensor([2., 2.], device='cuda:0')] # Rank 0
None                                                                   # Rank 1

```
Copy to clipboard

torch.distributed.gather_object(_obj_ , _object_gather_list =None_, _dst =None_, _group =None_, _group_dst =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3332)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather_object "Link to this definition")

Gathers picklable objects from the whole group in a single process.
Similar to [`gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather "torch.distributed.gather"), but Python objects can be passed in. Note that the object must be picklable in order to be gathered.

Parameters:

  * **obj** (_Any_) – Input object. Must be picklable.
  * **object_gather_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[__Any_ _]_) – Output list. On the `dst` rank, it should be correctly sized as the size of the group for this collective and will contain the output. Must be `None` on non-dst ranks. (default is `None`)
  * **dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on global process group (regardless of `group` argument). (If both `dst` and `group_dst` are None, default is global rank 0)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _|__None_) – (ProcessGroup, optional): The process group to work on. If None, the default process group will be used. Default is `None`.
  * **group_dst** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Destination rank on `group`. Invalid to specify both `dst` and `group_dst`


Returns:

None. On the `dst` rank, `object_gather_list` will contain the output of the collective.
Note
Note that this API differs slightly from the gather collective since it does not provide an async_op handle and thus will be a blocking call.
Note
For NCCL-based processed groups, internal tensor representations of objects must be moved to the GPU device before communication takes place. In this case, the device used is given by `torch.cuda.current_device()` and it is the user’s responsibility to ensure that this is set so that each rank has an individual GPU, via `torch.cuda.set_device()`.
Warning
Object collectives have a number of serious performance and scalability limitations. See [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives) for details.
Warning
[`gather_object()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather_object "torch.distributed.gather_object") uses `pickle` module implicitly, which is known to be insecure. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling. Only call this function with data you trust.
Warning
Calling [`gather_object()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather_object "torch.distributed.gather_object") with GPU tensors is not well supported and inefficient as it incurs GPU -> CPU transfer since tensors would be pickled. Please consider using [`gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather "torch.distributed.gather") instead.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> # Assumes world_size of 3.
>>> gather_objects = ["foo", 12, {1: 2}] # any picklable object
>>> output = [None for _ in gather_objects]
>>> dist.gather_object(
...     gather_objects[dist.get_rank()],
...     output if dist.get_rank() == 0 else None,
...     dst=0
... )
>>> # On rank 0
>>> output
['foo', 12, {1: 2}]

```
Copy to clipboard

torch.distributed.scatter(_tensor_ , _scatter_list =None_, _src =None_, _group =None_, _async_op =False_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4412)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter "Link to this definition")

Scatters a list of tensors to all processes in a group.
Each process will receive exactly one tensor and store its data in the `tensor` argument.
Complex tensors are supported.

Parameters:

  * **tensor** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Output tensor.
  * **scatter_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _]_) – List of tensors to scatter (default is None, must be specified on the source rank)
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Source rank on global process group (regardless of `group` argument). (If both `src` and `group_src` are None, default is global rank 0)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Source rank on `group`. Invalid to specify both `src` and `group_src`


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group
Note
Note that all Tensors in scatter_list must have the same size.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> tensor_size = 2
>>> device = torch.device(f'cuda:{rank}')
>>> output_tensor = torch.zeros(tensor_size, device=device)
>>> if dist.get_rank() == 0:
>>>     # Assumes world_size of 2.
>>>     # Only tensors, all of which must be the same size.
>>>     t_ones = torch.ones(tensor_size, device=device)
>>>     t_fives = torch.ones(tensor_size, device=device) * 5
>>>     scatter_list = [t_ones, t_fives]
>>> else:
>>>     scatter_list = None
>>> dist.scatter(output_tensor, scatter_list, src=0)
>>> # Rank i gets scatter_list[i].
>>> output_tensor
tensor([1., 1.], device='cuda:0') # Rank 0
tensor([5., 5.], device='cuda:1') # Rank 1

```
Copy to clipboard

torch.distributed.scatter_object_list(_scatter_object_output_list_ , _scatter_object_input_list =None_, _src =None_, _group =None_, _group_src =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L3855)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter_object_list "Link to this definition")

Scatters picklable objects in `scatter_object_input_list` to the whole group.
Similar to [`scatter()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter "torch.distributed.scatter"), but Python objects can be passed in. On each rank, the scattered object will be stored as the first element of `scatter_object_output_list`. Note that all objects in `scatter_object_input_list` must be picklable in order to be scattered.

Parameters:

  * **scatter_object_output_list** (_List_ _[__Any_ _]_) – Non-empty list whose first element will store the object scattered to this rank.
  * **scatter_object_input_list** (_List_ _[__Any_ _]__,__optional_) – List of input objects to scatter. Each object must be picklable. Only objects on the `src` rank will be scattered, and the argument can be `None` for non-src ranks.
  * **src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Source rank from which to scatter `scatter_object_input_list`. Source rank is based on global process group (regardless of `group` argument). (If both `src` and `group_src` are None, default is global rank 0)
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed.distributed_c10d.ProcessGroup") _|__None_) – (ProcessGroup, optional): The process group to work on. If None, the default process group will be used. Default is `None`.
  * **group_src** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – Source rank on `group`. Invalid to specify both `src` and `group_src`


Returns:

`None`. If rank is part of the group, `scatter_object_output_list` will have its first element set to the scattered object for this rank.
Note
Note that this API differs slightly from the scatter collective since it does not provide an `async_op` handle and thus will be a blocking call.
Warning
Object collectives have a number of serious performance and scalability limitations. See [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives) for details.
Warning
[`scatter_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter_object_list "torch.distributed.scatter_object_list") uses `pickle` module implicitly, which is known to be insecure. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling. Only call this function with data you trust.
Warning
Calling [`scatter_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter_object_list "torch.distributed.scatter_object_list") with GPU tensors is not well supported and inefficient as it incurs GPU -> CPU transfer since tensors would be pickled. Please consider using [`scatter()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter "torch.distributed.scatter") instead.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> if dist.get_rank() == 0:
>>>     # Assumes world_size of 3.
>>>     objects = ["foo", 12, {1: 2}] # any picklable object
>>> else:
>>>     # Can be any list on non-src ranks, elements are not used.
>>>     objects = [None, None, None]
>>> output_list = [None]
>>> dist.scatter_object_list(output_list, objects, src=0)
>>> # Rank i gets objects[i]. For example, on rank 2:
>>> output_list
[{1: 2}]

```
Copy to clipboard

torch.distributed.reduce_scatter(_output_ , _input_list_ , _op= <RedOpType.SUM: 0>_, _group=None_ , _async_op=False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4517)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce_scatter "Link to this definition")

Reduces, then scatters a list of tensors to all processes in a group.

Parameters:

  * **output** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Output tensor.
  * **input_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _]_) – List of tensors to reduce and scatter.
  * **op** (_optional_) – One of the values from `torch.distributed.ReduceOp` enum. Specifies an operation used for element-wise reductions.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group.

torch.distributed.reduce_scatter_tensor(_output_ , _input_ , _op= <RedOpType.SUM: 0>_, _group=None_ , _async_op=False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4562)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce_scatter_tensor "Link to this definition")

Reduces, then scatters a tensor to all ranks in a group.

Parameters:

  * **output** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Output tensor. It should have the same size across all ranks.
  * **input** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Input tensor to be reduced and scattered. Its size should be output tensor size times the world size. The input tensor can have one of the following shapes: (i) a concatenation of the output tensors along the primary dimension, or (ii) a stack of the output tensors along the primary dimension. For definition of “concatenation”, see `torch.cat()`. For definition of “stack”, see `torch.stack()`.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group.
Examples

```
>>> # All tensors below are of torch.int64 dtype and on CUDA devices.
>>> # We have two ranks.
>>> device = torch.device(f"cuda:{rank}")
>>> tensor_out = torch.zeros(2, dtype=torch.int64, device=device)
>>> # Input in concatenation form
>>> tensor_in = torch.arange(world_size * 2, dtype=torch.int64, device=device)
>>> tensor_in
tensor([0, 1, 2, 3], device='cuda:0') # Rank 0
tensor([0, 1, 2, 3], device='cuda:1') # Rank 1
>>> dist.reduce_scatter_tensor(tensor_out, tensor_in)
>>> tensor_out
tensor([0, 2], device='cuda:0') # Rank 0
tensor([4, 6], device='cuda:1') # Rank 1
>>> # Input in stack form
>>> tensor_in = torch.reshape(tensor_in, (world_size, 2))
>>> tensor_in
tensor([[0, 1],
        [2, 3]], device='cuda:0') # Rank 0
tensor([[0, 1],
        [2, 3]], device='cuda:1') # Rank 1
>>> dist.reduce_scatter_tensor(tensor_out, tensor_in)
>>> tensor_out
tensor([0, 2], device='cuda:0') # Rank 0
tensor([4, 6], device='cuda:1') # Rank 1

```
Copy to clipboard

torch.distributed.all_to_all_single(_output_ , _input_ , _output_split_sizes =None_, _input_split_sizes =None_, _group =None_, _async_op =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4693)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_to_all_single "Link to this definition")

Split input tensor and then scatter the split list to all processes in a group.
Later the received tensors are concatenated from all the processes in the group and returned as a single output tensor.
Complex tensors are supported.

Parameters:

  * **output** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Gathered concatenated output tensor.
  * **input** ([_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")) – Input tensor to scatter.
  * **output_split_sizes** – (list[Int], optional): Output split sizes for dim 0 if specified None or empty, dim 0 of `output` tensor must divide equally by `world_size`.
  * **input_split_sizes** – (list[Int], optional): Input split sizes for dim 0 if specified None or empty, dim 0 of `input` tensor must divide equally by `world_size`.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group.
Warning
all_to_all_single is experimental and subject to change.
Examples

```
>>> input = torch.arange(4) + rank * 4
>>> input
tensor([0, 1, 2, 3])     # Rank 0
tensor([4, 5, 6, 7])     # Rank 1
tensor([8, 9, 10, 11])   # Rank 2
tensor([12, 13, 14, 15]) # Rank 3
>>> output = torch.empty([4], dtype=torch.int64)
>>> dist.all_to_all_single(output, input)
>>> output
tensor([0, 4, 8, 12])    # Rank 0
tensor([1, 5, 9, 13])    # Rank 1
tensor([2, 6, 10, 14])   # Rank 2
tensor([3, 7, 11, 15])   # Rank 3

```
Copy to clipboard

```
>>> # Essentially, it is similar to following operation:
>>> scatter_list = list(input.chunk(world_size))
>>> gather_list = list(output.chunk(world_size))
>>> for i in range(world_size):
>>>     dist.scatter(gather_list[i], scatter_list if i == rank else [], src = i)

```
Copy to clipboard

```
>>> # Another example with uneven split
>>> input
tensor([0, 1, 2, 3, 4, 5])                                       # Rank 0
tensor([10, 11, 12, 13, 14, 15, 16, 17, 18])                     # Rank 1
tensor([20, 21, 22, 23, 24])                                     # Rank 2
tensor([30, 31, 32, 33, 34, 35, 36])                             # Rank 3
>>> input_splits
[2, 2, 1, 1]                                                     # Rank 0
[3, 2, 2, 2]                                                     # Rank 1
[2, 1, 1, 1]                                                     # Rank 2
[2, 2, 2, 1]                                                     # Rank 3
>>> output_splits
[2, 3, 2, 2]                                                     # Rank 0
[2, 2, 1, 2]                                                     # Rank 1
[1, 2, 1, 2]                                                     # Rank 2
[1, 2, 1, 1]                                                     # Rank 3
>>> output = ...
>>> dist.all_to_all_single(output, input, output_splits, input_splits)
>>> output
tensor([ 0,  1, 10, 11, 12, 20, 21, 30, 31])                     # Rank 0
tensor([ 2,  3, 13, 14, 22, 32, 33])                             # Rank 1
tensor([ 4, 15, 16, 23, 34, 35])                                 # Rank 2
tensor([ 5, 17, 18, 24, 36])                                     # Rank 3

```
Copy to clipboard

```
>>> # Another example with tensors of torch.cfloat type.
>>> input = torch.tensor(
...     [1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j], dtype=torch.cfloat
... ) + 4 * rank * (1 + 1j)
>>> input
tensor([1+1j, 2+2j, 3+3j, 4+4j])                                # Rank 0
tensor([5+5j, 6+6j, 7+7j, 8+8j])                                # Rank 1
tensor([9+9j, 10+10j, 11+11j, 12+12j])                          # Rank 2
tensor([13+13j, 14+14j, 15+15j, 16+16j])                        # Rank 3
>>> output = torch.empty([4], dtype=torch.int64)
>>> dist.all_to_all_single(output, input)
>>> output
tensor([1+1j, 5+5j, 9+9j, 13+13j])                              # Rank 0
tensor([2+2j, 6+6j, 10+10j, 14+14j])                            # Rank 1
tensor([3+3j, 7+7j, 11+11j, 15+15j])                            # Rank 2
tensor([4+4j, 8+8j, 12+12j, 16+16j])                            # Rank 3

```
Copy to clipboard

torch.distributed.all_to_all(_output_tensor_list_ , _input_tensor_list_ , _group =None_, _async_op =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4842)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_to_all "Link to this definition")

Scatters list of input tensors to all processes in a group and return gathered list of tensors in output list.
Complex tensors are supported.

Parameters:

  * **output_tensor_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _]_) – List of tensors to be gathered one per rank.
  * **input_tensor_list** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_Tensor_](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor") _]_) – List of tensors to scatter one per rank.
  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group.
Warning
all_to_all is experimental and subject to change.
Examples

```
>>> input = torch.arange(4) + rank * 4
>>> input = list(input.chunk(4))
>>> input
[tensor([0]), tensor([1]), tensor([2]), tensor([3])]     # Rank 0
[tensor([4]), tensor([5]), tensor([6]), tensor([7])]     # Rank 1
[tensor([8]), tensor([9]), tensor([10]), tensor([11])]   # Rank 2
[tensor([12]), tensor([13]), tensor([14]), tensor([15])] # Rank 3
>>> output = list(torch.empty([4], dtype=torch.int64).chunk(4))
>>> dist.all_to_all(output, input)
>>> output
[tensor([0]), tensor([4]), tensor([8]), tensor([12])]    # Rank 0
[tensor([1]), tensor([5]), tensor([9]), tensor([13])]    # Rank 1
[tensor([2]), tensor([6]), tensor([10]), tensor([14])]   # Rank 2
[tensor([3]), tensor([7]), tensor([11]), tensor([15])]   # Rank 3

```
Copy to clipboard

```
>>> # Essentially, it is similar to following operation:
>>> scatter_list = input
>>> gather_list = output
>>> for i in range(world_size):
>>>     dist.scatter(gather_list[i], scatter_list if i == rank else [], src=i)

```
Copy to clipboard

```
>>> input
tensor([0, 1, 2, 3, 4, 5])                                       # Rank 0
tensor([10, 11, 12, 13, 14, 15, 16, 17, 18])                     # Rank 1
tensor([20, 21, 22, 23, 24])                                     # Rank 2
tensor([30, 31, 32, 33, 34, 35, 36])                             # Rank 3
>>> input_splits
[2, 2, 1, 1]                                                     # Rank 0
[3, 2, 2, 2]                                                     # Rank 1
[2, 1, 1, 1]                                                     # Rank 2
[2, 2, 2, 1]                                                     # Rank 3
>>> output_splits
[2, 3, 2, 2]                                                     # Rank 0
[2, 2, 1, 2]                                                     # Rank 1
[1, 2, 1, 2]                                                     # Rank 2
[1, 2, 1, 1]                                                     # Rank 3
>>> input = list(input.split(input_splits))
>>> input
[tensor([0, 1]), tensor([2, 3]), tensor([4]), tensor([5])]                   # Rank 0
[tensor([10, 11, 12]), tensor([13, 14]), tensor([15, 16]), tensor([17, 18])] # Rank 1
[tensor([20, 21]), tensor([22]), tensor([23]), tensor([24])]                 # Rank 2
[tensor([30, 31]), tensor([32, 33]), tensor([34, 35]), tensor([36])]         # Rank 3
>>> output = ...
>>> dist.all_to_all(output, input)
>>> output
[tensor([0, 1]), tensor([10, 11, 12]), tensor([20, 21]), tensor([30, 31])]   # Rank 0
[tensor([2, 3]), tensor([13, 14]), tensor([22]), tensor([32, 33])]           # Rank 1
[tensor([4]), tensor([15, 16]), tensor([23]), tensor([34, 35])]              # Rank 2
[tensor([5]), tensor([17, 18]), tensor([24]), tensor([36])]                  # Rank 3

```
Copy to clipboard

```
>>> # Another example with tensors of torch.cfloat type.
>>> input = torch.tensor(
...     [1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j], dtype=torch.cfloat
... ) + 4 * rank * (1 + 1j)
>>> input = list(input.chunk(4))
>>> input
[tensor([1+1j]), tensor([2+2j]), tensor([3+3j]), tensor([4+4j])]            # Rank 0
[tensor([5+5j]), tensor([6+6j]), tensor([7+7j]), tensor([8+8j])]            # Rank 1
[tensor([9+9j]), tensor([10+10j]), tensor([11+11j]), tensor([12+12j])]      # Rank 2
[tensor([13+13j]), tensor([14+14j]), tensor([15+15j]), tensor([16+16j])]    # Rank 3
>>> output = list(torch.empty([4], dtype=torch.int64).chunk(4))
>>> dist.all_to_all(output, input)
>>> output
[tensor([1+1j]), tensor([5+5j]), tensor([9+9j]), tensor([13+13j])]          # Rank 0
[tensor([2+2j]), tensor([6+6j]), tensor([10+10j]), tensor([14+14j])]        # Rank 1
[tensor([3+3j]), tensor([7+7j]), tensor([11+11j]), tensor([15+15j])]        # Rank 2
[tensor([4+4j]), tensor([8+8j]), tensor([12+12j]), tensor([16+16j])]        # Rank 3

```
Copy to clipboard

torch.distributed.barrier(_group =None_, _async_op =False_, _device_ids =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L4966)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.barrier "Link to this definition")

Synchronize all processes.
This collective blocks processes until the whole group enters this function, if async_op is False, or if async work handle is called on wait().

Parameters:

  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If None, the default process group will be used.
  * **async_op** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether this op should be an async op
  * **device_ids** (_[_[_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _]__,__optional_) – List of device/GPU ids. Only one id is expected.


Returns:

Async work handle, if async_op is set to True. None, if not async_op or if not part of the group
Note
ProcessGroupNCCL now blocks the cpu thread till the completion of the barrier collective.
Note
ProcessGroupNCCL implements barrier as an all_reduce of a 1-element tensor. A device must be chosen for allocating this tensor. The device choice is made by checking in this order (1) the first device passed to device_ids arg of barrier if not None, (2) the device passed to init_process_group if not None, (3) the device that was first used with this process group, if another collective with tensor inputs has been performed, (4) the device index indicated by the global rank mod local device count.

torch.distributed.monitored_barrier(_group =None_, _timeout =None_, _wait_all_ranks =False_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/distributed_c10d.py#L5041)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "Link to this definition")

Synchronize processes similar to `torch.distributed.barrier`, but consider a configurable timeout.
It is able to report ranks that did not pass this barrier within the provided timeout. Specifically, for non-zero ranks, will block until a send/recv is processed from rank 0. Rank 0 will block until all send /recv from other ranks are processed, and will report failures for ranks that failed to respond in time. Note that if one rank does not reach the monitored_barrier (for example due to a hang), all other ranks would fail in monitored_barrier.
This collective will block all processes/ranks in the group, until the whole group exits the function successfully, making it useful for debugging and synchronizing. However, it can have a performance impact and should only be used for debugging or scenarios that require full synchronization points on the host-side. For debugging purposes, this barrier can be inserted before the application’s collective calls to check if any ranks are desynchronized.
Note
Note that this collective is only supported with the GLOO backend.

Parameters:

  * **group** ([_ProcessGroup_](https://docs.pytorch.org/docs/stable/distributed._dist2.html#torch.distributed._dist2.ProcessGroup "torch.distributed._dist2.ProcessGroup") _,__optional_) – The process group to work on. If `None`, the default process group will be used.
  * **timeout** ([_datetime.timedelta_](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)") _,__optional_) – Timeout for monitored_barrier. If `None`, the default process group timeout will be used.
  * **wait_all_ranks** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether to collect all failed ranks or not. By default, this is `False` and `monitored_barrier` on rank 0 will throw on the first failed rank it encounters in order to fail fast. By setting `wait_all_ranks=True` `monitored_barrier` will collect all failed ranks and throw an error containing information about all failed ranks.


Returns:

`None`.

Example::


```
>>> # Note: Process group initialization omitted on each rank.
>>> import torch.distributed as dist
>>> if dist.get_rank() != 1:
>>>     dist.monitored_barrier() # Raises exception indicating that
>>> # rank 1 did not call into monitored_barrier.
>>> # Example with wait_all_ranks=True
>>> if dist.get_rank() == 0:
>>>     dist.monitored_barrier(wait_all_ranks=True) # Raises exception
>>> # indicating that ranks 1, 2, ... world_size - 1 did not call into
>>> # monitored_barrier.

```
Copy to clipboard

_class_ torch.distributed.Work[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work "Link to this definition")

A Work object represents the handle to a pending asynchronous operation in PyTorch’s distributed package. It is returned by non-blocking collective operations, such as dist.all_reduce(tensor, async_op=True).

block_current_stream(_self :torch._C._distributed_c10d.Work_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.block_current_stream "Link to this definition")

Blocks the currently active GPU stream on the operation to complete. For GPU based collectives this is equivalent to synchronize. For CPU initiated collectives such as with Gloo this will block the CUDA stream until the operation is complete.
This returns immediately in all cases.
To check whether an operation was successful you should check the Work object result asynchronously.

boxed(_self :torch._C._distributed_c10d.Work_) → [object](https://docs.python.org/3/library/functions.html#object "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.boxed "Link to this definition")


exception(_self :torch._C._distributed_c10d.Work_) → std::__exception_ptr::exception_ptr[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.exception "Link to this definition")


get_future(_self :torch._C._distributed_c10d.Work_) → torch.Future[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.get_future "Link to this definition")


Returns:

A `torch.futures.Future` object which is associated with the completion of the `Work`. As an example, a future object can be retrieved by `fut = process_group.allreduce(tensors).get_future()`.

Example::

Below is an example of a simple allreduce DDP communication hook that uses `get_future` API to retrieve a Future associated with the completion of `allreduce`.

```
>>> def allreduce(process_group: dist.ProcessGroup, bucket: dist.GradBucket): -> torch.futures.Future
>>>     group_to_use = process_group if process_group is not None else torch.distributed.group.WORLD
>>>     tensor = bucket.buffer().div_(group_to_use.size())
>>>     return torch.distributed.all_reduce(tensor, group=group_to_use, async_op=True).get_future()
>>> ddp_model.register_comm_hook(state=None, hook=allreduce)

```
Copy to clipboard
Warning
`get_future` API supports NCCL, and partially GLOO and MPI backends (no support for peer-to-peer operations like send/recv) and will return a `torch.futures.Future`.
In the example above, `allreduce` work will be done on GPU using NCCL backend, `fut.wait()` will return after synchronizing the appropriate NCCL streams with PyTorch’s current device streams to ensure we can have asynchronous CUDA execution and it does not wait for the entire operation to complete on GPU. Note that `CUDAFuture` does not support `TORCH_NCCL_BLOCKING_WAIT` flag or NCCL’s `barrier()`. In addition, if a callback function was added by `fut.then()`, it will wait until `WorkNCCL`’s NCCL streams synchronize with `ProcessGroupNCCL`’s dedicated callback stream and invoke the callback inline after running the callback on the callback stream. `fut.then()` will return another `CUDAFuture` that holds the return value of the callback and a `CUDAEvent` that recorded the callback stream.
>   1. For CPU work, `fut.done()` returns true when work has been completed and value() tensors are ready.
>   2. For GPU work, `fut.done()` returns true only whether the operation has been enqueued.
>   3. For mixed CPU-GPU work (e.g. sending GPU tensors with GLOO), `fut.done()` returns true when tensors have arrived on respective nodes, but not yet necessarily synched on respective GPUs (similarly to GPU work).
>


get_future_result(_self :torch._C._distributed_c10d.Work_) → torch.Future[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.get_future_result "Link to this definition")


Returns:

A `torch.futures.Future` object of int type which maps to the enum type of WorkResult As an example, a future object can be retrieved by `fut = process_group.allreduce(tensor).get_future_result()`.

Example::

users can use `fut.wait()` to blocking wait for the completion of the work and get the WorkResult by `fut.value()`. Also, users can use `fut.then(call_back_func)` to register a callback function to be called when the work is completed, without blocking the current thread.
Warning
`get_future_result` API supports NCCL

is_completed(_self :torch._C._distributed_c10d.Work_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.is_completed "Link to this definition")


is_success(_self :torch._C._distributed_c10d.Work_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.is_success "Link to this definition")


result(_self :torch._C._distributed_c10d.Work_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[torch.Tensor](https://docs.pytorch.org/docs/stable/tensors.html#torch.Tensor "torch.Tensor")][#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.result "Link to this definition")


source_rank(_self :torch._C._distributed_c10d.Work_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.source_rank "Link to this definition")


synchronize(_self :torch._C._distributed_c10d.Work_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.synchronize "Link to this definition")


_static_ unbox(_arg0 :[object](https://docs.python.org/3/library/functions.html#object "\(in Python v3.14\)")_) → torch._C._distributed_c10d.Work[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.unbox "Link to this definition")


wait(_self :torch._C._distributed_c10d.Work_, _timeout :[datetime.timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)")=datetime.timedelta(0)_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.wait "Link to this definition")


Returns:

true/false.

Example::


try:

work.wait(timeout)

except:

# some handling
Warning
In normal cases, users do not need to set the timeout. calling wait() is the same as calling synchronize(): Letting the current stream block on the completion of the NCCL work. However, if timeout is set, it will block the CPU thread until the NCCL work is completed or timed out. If timeout, exception will be thrown.

_class_ torch.distributed.ReduceOp[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.ReduceOp "Link to this definition")

An enum-like class for available reduction operations: `SUM`, `PRODUCT`, `MIN`, `MAX`, `BAND`, `BOR`, `BXOR`, and `PREMUL_SUM`.
`BAND`, `BOR`, and `BXOR` reductions are not available when using the `NCCL` backend.
`AVG` divides values by the world size before summing across ranks. `AVG` is only available with the `NCCL` backend, and only for NCCL versions 2.10 or later.
`PREMUL_SUM` multiplies inputs by a given scalar locally before reduction. `PREMUL_SUM` is only available with the `NCCL` backend, and only available for NCCL versions 2.11 or later. Users are supposed to use `torch.distributed._make_nccl_premul_sum`.
Additionally, `MAX`, `MIN` and `PRODUCT` are not supported for complex tensors.
The values of this class can be accessed as attributes, e.g., `ReduceOp.SUM`. They are used in specifying strategies for reduction collectives, e.g., [`reduce()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce "torch.distributed.reduce").
This class does not support `__members__` property.

_class_ torch.distributed.reduce_op[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce_op "Link to this definition")

Deprecated enum-like class for reduction operations: `SUM`, `PRODUCT`, `MIN`, and `MAX`.
[`ReduceOp`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.ReduceOp "torch.distributed.ReduceOp") is recommended to use instead.
## Distributed Key-Value Store[#](https://docs.pytorch.org/docs/stable/distributed.html#distributed-key-value-store "Link to this heading")
The distributed package comes with a distributed key-value store, which can be used to share information between processes in the group as well as to initialize the distributed package in [`torch.distributed.init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") (by explicitly creating the store as an alternative to specifying `init_method`.) There are 3 choices for Key-Value Stores: [`TCPStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "torch.distributed.TCPStore"), [`FileStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore "torch.distributed.FileStore"), and [`HashStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore "torch.distributed.HashStore").

_class_ torch.distributed.Store[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store "Link to this definition")

Base class for all store implementations, such as the 3 provided by PyTorch distributed: ([`TCPStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "torch.distributed.TCPStore"), [`FileStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore "torch.distributed.FileStore"), and [`HashStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore "torch.distributed.HashStore")).

__init__(_self :torch._C._distributed_c10d.Store_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.__init__ "Link to this definition")


add(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arg1 :[SupportsInt](https://docs.python.org/3/library/typing.html#typing.SupportsInt "\(in Python v3.14\)")_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.add "Link to this definition")

The first call to add for a given `key` creates a counter associated with `key` in the store, initialized to `amount`. Subsequent calls to add with the same `key` increment the counter by the specified `amount`. Calling `add()` with a key that has already been set in the store by `set()` will result in an exception.

Parameters:

  * **key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key in the store whose counter will be incremented.
  * **amount** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – The quantity by which the counter will be incremented.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, other store types can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.add("first_key", 1)
>>> store.add("first_key", 6)
>>> # Should return 7
>>> store.get("first_key")

```
Copy to clipboard

append(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arg1 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.append "Link to this definition")

Append the key-value pair into the store based on the supplied `key` and `value`. If `key` does not exists in the store, it will be created.

Parameters:

  * **key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key to be appended to the store.
  * **value** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The value associated with `key` to be added to the store.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.append("first_key", "po")
>>> store.append("first_key", "tato")
>>> # Should return "potato"
>>> store.get("first_key")

```
Copy to clipboard

check(_self :torch._C._distributed_c10d.Store_, _arg0 :[collections.abc.Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.check "Link to this definition")

The call to check whether a given list of `keys` have value stored in the store. This call immediately returns in normal cases but still suffers from some edge deadlock cases, e.g, calling check after TCPStore has been destroyed. Calling `check()` with a list of keys that one wants to check whether stored in the store or not.

Parameters:

**keys** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]_) – The keys to query whether stored in the store.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, other store types can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.add("first_key", 1)
>>> # Should return 7
>>> store.check(["first_key"])

```
Copy to clipboard

clone(_self :torch._C._distributed_c10d.Store_) → torch._C._distributed_c10d.Store[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.clone "Link to this definition")

Clones the store and returns a new object that points to the same underlying store. The returned store can be used concurrently with the original object. This is intended to provide a safe way to use a store from multiple threads by cloning one store per thread.

compare_set(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arg1 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arg2 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.compare_set "Link to this definition")

Inserts the key-value pair into the store based on the supplied `key` and performs comparison between `expected_value` and `desired_value` before inserting. `desired_value` will only be set if `expected_value` for the `key` already exists in the store or if `expected_value` is an empty string.

Parameters:

  * **key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key to be checked in the store.
  * **expected_value** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The value associated with `key` to be checked before insertion.
  * **desired_value** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The value associated with `key` to be added to the store.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set("key", "first_value")
>>> store.compare_set("key", "first_value", "second_value")
>>> # Should return "second_value"
>>> store.get("key")

```
Copy to clipboard

delete_key(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.delete_key "Link to this definition")

Deletes the key-value pair associated with `key` from the store. Returns true if the key was successfully deleted, and false if it was not.
Warning
The `delete_key` API is only supported by the [`TCPStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "torch.distributed.TCPStore") and [`HashStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore "torch.distributed.HashStore"). Using this API with the [`FileStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore "torch.distributed.FileStore") will result in an exception.

Parameters:

**key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key to be deleted from the store

Returns:

True if `key` was deleted, otherwise False.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, HashStore can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set("first_key")
>>> # This should return true
>>> store.delete_key("first_key")
>>> # This should return false
>>> store.delete_key("bad_key")

```
Copy to clipboard

get(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.get "Link to this definition")

Retrieves the value associated with the given `key` in the store. If `key` is not present in the store, the function will wait for `timeout`, which is defined when initializing the store, before throwing an exception.

Parameters:

**key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The function will return the value associated with this key.

Returns:

Value associated with `key` if `key` is in the store.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set("first_key", "first_value")
>>> # Should return "first_value"
>>> store.get("first_key")

```
Copy to clipboard

has_extended_api(_self :torch._C._distributed_c10d.Store_) → [bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.has_extended_api "Link to this definition")

Returns true if the store supports extended operations.

list_keys(_self :torch._C._distributed_c10d.Store_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")][#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.list_keys "Link to this definition")

Returns a list of all keys in the store.

multi_get(_self :torch._C._distributed_c10d.Store_, _arg0 :[collections.abc.Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) → [list](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")][#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.multi_get "Link to this definition")

Retrieve all values in `keys`. If any key in `keys` is not present in the store, the function will wait for `timeout`

Parameters:

**keys** (_List_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]_) – The keys to be retrieved from the store.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set("first_key", "po")
>>> store.set("second_key", "tato")
>>> # Should return [b"po", b"tato"]
>>> store.multi_get(["first_key", "second_key"])

```
Copy to clipboard

multi_set(_self :torch._C._distributed_c10d.Store_, _arg0 :[collections.abc.Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_, _arg1 :[collections.abc.Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "\(in Python v3.14\)")[[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")]_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.multi_set "Link to this definition")

Inserts a list key-value pair into the store based on the supplied `keys` and `values`

Parameters:

  * **keys** (_List_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]_) – The keys to insert.
  * **values** (_List_ _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]_) – The values to insert.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.multi_set(["first_key", "second_key"], ["po", "tato"])
>>> # Should return b"po"
>>> store.get("first_key")

```
Copy to clipboard

num_keys(_self :torch._C._distributed_c10d.Store_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.num_keys "Link to this definition")

Returns the number of keys set in the store. Note that this number will typically be one greater than the number of keys added by `set()` and `add()` since one key is used to coordinate all the workers using the store.
Warning
When used with the [`TCPStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "torch.distributed.TCPStore"), `num_keys` returns the number of keys written to the underlying file. If the store is destructed and another store is created with the same file, the original keys will be retained.

Returns:

The number of keys present in the store.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, other store types can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set("first_key", "first_value")
>>> # This should return 2
>>> store.num_keys()

```
Copy to clipboard

queue_len(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [int](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.queue_len "Link to this definition")

Returns the length of the specified queue.
If the queue doesn’t exist it returns 0.
See queue_push for more details.

Parameters:

**key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key of the queue to get the length.

queue_pop(_self :torch._C._distributed_c10d.Store_, _key :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _block :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=True_) → [bytes](https://docs.python.org/3/library/stdtypes.html#bytes "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.queue_pop "Link to this definition")

Pops a value from the specified queue or waits until timeout if the queue is empty.
See queue_push for more details.
If block is False, a dist.QueueEmptyError will be raised if the queue is empty.

Parameters:

  * **key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key of the queue to pop from.
  * **block** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")) – Whether to block waiting for the key or immediately return.


queue_push(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arg1 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.queue_push "Link to this definition")

Pushes a value into the specified queue.
Using the same key for queues and set/get operations may result in unexpected behavior.
wait/check operations are supported for queues.
wait with queues will only wake one waiting worker rather than all.

Parameters:

  * **key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key of the queue to push to.
  * **value** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The value to push into the queue.


set(_self :torch._C._distributed_c10d.Store_, _arg0 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _arg1 :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.set "Link to this definition")

Inserts the key-value pair into the store based on the supplied `key` and `value`. If `key` already exists in the store, it will overwrite the old value with the new supplied `value`.

Parameters:

  * **key** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The key to be added to the store.
  * **value** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The value associated with `key` to be added to the store.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set("first_key", "first_value")
>>> # Should return "first_value"
>>> store.get("first_key")

```
Copy to clipboard

set_timeout(_self :torch._C._distributed_c10d.Store_, _arg0 :[datetime.timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.set_timeout "Link to this definition")

Sets the store’s default timeout. This timeout is used during initialization and in `wait()` and `get()`.

Parameters:

**timeout** (_timedelta_) – timeout to be set in the store.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, other store types can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> store.set_timeout(timedelta(seconds=10))
>>> # This will throw an exception after 10 seconds
>>> store.wait(["bad_key"])

```
Copy to clipboard

_property_ timeout[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.timeout "Link to this definition")

Gets the timeout of the store.

wait(_* args_, _** kwargs_)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.wait "Link to this definition")

Overloaded function.
  1. wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str]) -> None


Waits for each key in `keys` to be added to the store. If not all keys are set before the `timeout` (set during store initialization), then `wait` will throw an exception.

Parameters:

**keys** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")) – List of keys on which to wait until they are set in the store.

Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, other store types can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> # This will throw an exception after 30 seconds
>>> store.wait(["bad_key"])

```
Copy to clipboard
  1. wait(self: torch._C._distributed_c10d.Store, arg0: collections.abc.Sequence[str], arg1: datetime.timedelta) -> None


Waits for each key in `keys` to be added to the store, and throws an exception if the keys have not been set by the supplied `timeout`.

Parameters:

  * **keys** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)")) – List of keys on which to wait until they are set in the store.
  * **timeout** (_timedelta_) – Time to wait for the keys to be added before throwing an exception.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Using TCPStore as an example, other store types can also be used
>>> store = dist.TCPStore("127.0.0.1", 0, 1, True, timedelta(seconds=30))
>>> # This will throw an exception after 10 seconds
>>> store.wait(["bad_key"], timedelta(seconds=10))

```
Copy to clipboard

_class_ torch.distributed.TCPStore[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "Link to this definition")

A TCP-based distributed key-value store implementation. The server store holds the data, while the client stores can connect to the server store over TCP and perform actions such as `set()` to insert a key-value pair, `get()` to retrieve a key-value pair, etc. There should always be one server store initialized because the client store(s) will wait for the server to establish a connection.

Parameters:

  * **host_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The hostname or IP Address the server store should run on.
  * **port** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – The port on which the server store should listen for incoming requests.
  * **world_size** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – The total number of store users (number of clients + 1 for the server). Default is None (None indicates a non-fixed number of store users).
  * **is_master** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – True when initializing the server store and False for client stores. Default is False.
  * **timeout** (_timedelta_ _,__optional_) – Timeout used by the store during initialization and for methods such as `get()` and `wait()`. Default is timedelta(seconds=300)
  * **wait_for_workers** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – Whether to wait for all the workers to connect with the server store. This is only applicable when world_size is a fixed value. Default is True.
  * **multi_tenant** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – If True, all `TCPStore` instances in the current process with the same host/port will use the same underlying `TCPServer`. Default is False.
  * **master_listen_fd** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – If specified, the underlying `TCPServer` will listen on this file descriptor, which must be a socket already bound to `port`. To bind an ephemeral port we recommend setting the port to 0 and reading `.port`. Default is None (meaning the server creates a new socket and attempts to bind it to `port`).
  * **use_libuv** ([_bool_](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)") _,__optional_) – If True, use libuv for `TCPServer` backend. Default is True.


Example::


```
>>> import torch.distributed as dist
>>> from datetime import timedelta
>>> # Run on process 1 (server)
>>> server_store = dist.TCPStore("127.0.0.1", 1234, 2, True, timedelta(seconds=30))
>>> # Run on process 2 (client)
>>> client_store = dist.TCPStore("127.0.0.1", 1234, 2, False)
>>> # Use any of the store methods from either the client or server after initialization
>>> server_store.set("first_key", "first_value")
>>> client_store.get("first_key")

```
Copy to clipboard

__init__(_self :[torch._C._distributed_c10d.TCPStore](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "torch._C._distributed_c10d.TCPStore")_, _host_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _port :[SupportsInt](https://docs.python.org/3/library/typing.html#typing.SupportsInt "\(in Python v3.14\)")_, _world_size :[SupportsInt](https://docs.python.org/3/library/typing.html#typing.SupportsInt "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _is_master :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_, _timeout :[datetime.timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta "\(in Python v3.14\)")=datetime.timedelta(seconds=300)_, _wait_for_workers :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=True_, _multi_tenant :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=False_, _master_listen_fd :[SupportsInt](https://docs.python.org/3/library/typing.html#typing.SupportsInt "\(in Python v3.14\)")|[None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")=None_, _use_libuv :[bool](https://docs.python.org/3/library/functions.html#bool "\(in Python v3.14\)")=True_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.__init__ "Link to this definition")

Creates a new TCPStore.

_property_ host[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.host "Link to this definition")

Gets the hostname on which the store listens for requests.

_property_ libuvBackend[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.libuvBackend "Link to this definition")

Returns True if it’s using the libuv backend.

_property_ port[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.port "Link to this definition")

Gets the port number on which the store listens for requests.

_class_ torch.distributed.HashStore[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore "Link to this definition")

A thread-safe store implementation based on an underlying hashmap. This store can be used within the same process (for example, by other threads), but cannot be used across processes.

Example::


```
>>> import torch.distributed as dist
>>> store = dist.HashStore()
>>> # store can be used from other threads
>>> # Use any of the store methods after initialization
>>> store.set("first_key", "first_value")

```
Copy to clipboard

__init__(_self :[torch._C._distributed_c10d.HashStore](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore "torch._C._distributed_c10d.HashStore")_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore.__init__ "Link to this definition")

Creates a new HashStore.

_class_ torch.distributed.FileStore[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore "Link to this definition")

A store implementation that uses a file to store the underlying key-value pairs.

Parameters:

  * **file_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – path of the file in which to store the key-value pairs
  * **world_size** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)") _,__optional_) – The total number of processes using the store. Default is -1 (a negative value indicates a non-fixed number of store users).


Example::


```
>>> import torch.distributed as dist
>>> store1 = dist.FileStore("/tmp/filestore", 2)
>>> store2 = dist.FileStore("/tmp/filestore", 2)
>>> # Use any of the store methods from either the client or server after initialization
>>> store1.set("first_key", "first_value")
>>> store2.get("first_key")

```
Copy to clipboard

__init__(_self :[torch._C._distributed_c10d.FileStore](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore "torch._C._distributed_c10d.FileStore")_, _file_name :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _world_size :[SupportsInt](https://docs.python.org/3/library/typing.html#typing.SupportsInt "\(in Python v3.14\)")=-1_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore.__init__ "Link to this definition")

Creates a new FileStore.

_property_ path[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore.path "Link to this definition")

Gets the path of the file used by FileStore to store key-value pairs.

_class_ torch.distributed.PrefixStore[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.PrefixStore "Link to this definition")

A wrapper around any of the 3 key-value stores ([`TCPStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore "torch.distributed.TCPStore"), [`FileStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore "torch.distributed.FileStore"), and [`HashStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore "torch.distributed.HashStore")) that adds a prefix to each key inserted to the store.

Parameters:

  * **prefix** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")) – The prefix string that is prepended to each key before being inserted into the store.
  * **store** (_torch.distributed.store_) – A store object that forms the underlying key-value store.


__init__(_self :torch._C._distributed_c10d.PrefixStore_, _prefix :[str](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)")_, _store :torch._C._distributed_c10d.Store_) → [None](https://docs.python.org/3/library/constants.html#None "\(in Python v3.14\)")[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.PrefixStore.__init__ "Link to this definition")

Creates a new PrefixStore.

_property_ underlying_store[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.PrefixStore.underlying_store "Link to this definition")

Gets the underlying store object that PrefixStore wraps around.
## Profiling Collective Communication[#](https://docs.pytorch.org/docs/stable/distributed.html#profiling-collective-communication "Link to this heading")
Note that you can use `torch.profiler` (recommended, only available after 1.8.1) or `torch.autograd.profiler` to profile collective communication and point-to-point communication APIs mentioned here. All out-of-the-box backends (`gloo`, `nccl`, `mpi`) are supported and collective communication usage will be rendered as expected in profiling output/traces. Profiling your code is the same as any regular torch operator:

```
import torch
import torch.distributed as dist
with torch.profiler():
    tensor = torch.randn(20, 10)
    dist.all_reduce(tensor)

```
Copy to clipboard
Please refer to the [profiler documentation](https://pytorch.org/docs/main/profiler.html) for a full overview of profiler features.
## Optimization with Symmetric Memory[#](https://docs.pytorch.org/docs/stable/distributed.html#optimization-with-symmetric-memory "Link to this heading")
### Copy Engine Collectives[#](https://docs.pytorch.org/docs/stable/distributed.html#copy-engine-collectives "Link to this heading")
When NCCL collective operations are performed on symmetric memory tensors with the zero-CTA policy, data movement is offloaded to the GPU’s copy engines (DMA engines) instead of using CUDA streaming multiprocessors (SMs). This frees up SMs for compute work, enabling better overlap of communication and computation.
For setup instructions, requirements, and examples, see [Copy Engine Collectives](https://docs.pytorch.org/docs/stable/symmetric_memory.html#copy-engine-collectives) in the Symmetric Memory documentation.
### Higher-Precision Reduction[#](https://docs.pytorch.org/docs/stable/distributed.html#higher-precision-reduction "Link to this heading")
When NCCL collectives such as `reduce_scatter` and `all_reduce` operate on symmetric memory tensors, NCCL’s symmetric kernel implementation automatically performs internal reduction with higher precision (e.g., BF16/FP16 in → FP32 accumulate → BF16/FP16 out). This improves numerical accuracy without any code changes to the collective call.
For details on scope, supported domains, and version requirements, see [Higher-Precision Reduction](https://docs.pytorch.org/docs/stable/symmetric_memory.html#higher-precision-reduction) in the Symmetric Memory documentation.
## Multi-GPU collective functions[#](https://docs.pytorch.org/docs/stable/distributed.html#multi-gpu-collective-functions "Link to this heading")
Warning
The multi-GPU functions (which stand for multiple GPUs per CPU thread) are deprecated. As of today, PyTorch Distributed’s preferred programming model is one device per thread, as exemplified by the APIs in this document. If you are a backend developer and want to support multiple devices per thread, please contact PyTorch Distributed’s maintainers.
## Object collectives[#](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives "Link to this heading")
Warning
Object collectives have a number of serious limitations. Read further to determine if they are safe to use for your use case.
Object collectives are a set of collective-like operations that work on arbitrary Python objects, as long as they can be pickled. There are various collective patterns implemented (e.g. broadcast, all_gather, …) but they each roughly follow this pattern:
  1. convert the input object into a pickle (raw bytes), then shove it into a byte tensor
  2. communicate the size of this byte tensor to peers (first collective operation)
  3. allocate appropriately sized tensor to perform the real collective
  4. communicate the object data (second collective operation)
  5. convert raw data back into Python (unpickle)


Object collectives sometimes have surprising performance or memory characteristics that lead to long runtimes or OOMs, and thus they should be used with caution. Here are some common issues.
**Asymmetric pickle/unpickle time** - Pickling objects can be slow, depending on the number, type and size of the objects. When the collective has a fan-in (e.g. gather_object), the receiving rank(s) must unpickle N times more objects than the sending rank(s) had to pickle, which can cause other ranks to time out on their next collective.
**Inefficient tensor communication** - Tensors should be sent via regular collective APIs, not object collective APIs. It is possible to send Tensors via object collective APIs, but they will be serialized and deserialized (including a CPU-sync and device-to-host copy in the case of non-CPU tensors), and in almost every case other than debugging or troubleshooting code, it would be worth the trouble to refactor the code to use non-object collectives instead.
**Unexpected tensor devices** - If you still want to send tensors via object collectives, there is another aspect specific to cuda (and possibly other accelerators) tensors. If you pickle a tensor that is currently on `cuda:3`, and then unpickle it, you will get another tensor on `cuda:3` _regardless of which process you are on, or which CUDA device is the ‘default’ device for that process_. With regular tensor collective APIs, ‘output tensors’ will always be on the same, local device, which is generally what you’d expect.
Unpickling a tensor will implicitly activate a CUDA context if it is the first time a GPU is used by the process, which can waste significant amounts of GPU memory. This issue can be avoided by moving tensors to CPU before passing them as inputs to an object collective.
## Third-party backends[#](https://docs.pytorch.org/docs/stable/distributed.html#third-party-backends "Link to this heading")
Besides the builtin GLOO/MPI/NCCL backends, PyTorch distributed supports third-party backends through a run-time register mechanism. For references on how to develop a third-party backend through C++ Extension, please refer to [Tutorials - Custom C++ and CUDA Extensions](https://pytorch.org/tutorials/advanced/cpp_extension.html) and `test/cpp_extensions/cpp_c10d_extension.cpp`. The capability of third-party backends are decided by their own implementations.
The new backend derives from `c10d::ProcessGroup` and registers the backend name and the instantiating interface through [`torch.distributed.Backend.register_backend()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend.register_backend "torch.distributed.Backend.register_backend") when imported.
When manually importing this backend and invoking [`torch.distributed.init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") with the corresponding backend name, the `torch.distributed` package runs on the new backend.
Warning
The support of third-party backend is experimental and subject to change.
## Launch utility[#](https://docs.pytorch.org/docs/stable/distributed.html#launch-utility "Link to this heading")
The `torch.distributed` package also provides a launch utility in `torch.distributed.launch`. This helper utility can be used to launch multiple processes per node for distributed training.
Module `torch.distributed.launch`.
`torch.distributed.launch` is a module that spawns up multiple distributed training processes on each of the training nodes.
Warning
This module is going to be deprecated in favor of [torchrun](https://docs.pytorch.org/docs/stable/elastic/run.html#launcher-api).
The utility can be used for single-node distributed training, in which one or more processes per node will be spawned. The utility can be used for either CPU training or GPU training. If the utility is used for GPU training, each distributed process will be operating on a single GPU. This can achieve well-improved single-node training performance. It can also be used in multi-node distributed training, by spawning up multiple processes on each node for well-improved multi-node distributed training performance as well. This will especially be beneficial for systems with multiple Infiniband interfaces that have direct-GPU support, since all of them can be utilized for aggregated communication bandwidth.
In both cases of single-node distributed training or multi-node distributed training, this utility will launch the given number of processes per node (`--nproc-per-node`). If used for GPU training, this number needs to be less or equal to the number of GPUs on the current system (`nproc_per_node`), and each process will be operating on a single GPU from _GPU 0 to GPU (nproc_per_node - 1)_.
**How to use this module:**
  1. Single-Node multi-process distributed training


```
python -m torch.distributed.launch --nproc-per-node=NUM_GPUS_YOU_HAVE
           YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3 and all other
           arguments of your training script)

```
Copy to clipboard
  1. Multi-Node multi-process distributed training: (e.g. two nodes)


Node 1: _(IP: 192.168.1.1, and has a free port: 1234)_

```
python -m torch.distributed.launch --nproc-per-node=NUM_GPUS_YOU_HAVE
           --nnodes=2 --node-rank=0 --master-addr="192.168.1.1"
           --master-port=1234 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3
           and all other arguments of your training script)

```
Copy to clipboard
Node 2:

```
python -m torch.distributed.launch --nproc-per-node=NUM_GPUS_YOU_HAVE
           --nnodes=2 --node-rank=1 --master-addr="192.168.1.1"
           --master-port=1234 YOUR_TRAINING_SCRIPT.py (--arg1 --arg2 --arg3
           and all other arguments of your training script)

```
Copy to clipboard
  1. To look up what optional arguments this module offers:


```
python -m torch.distributed.launch --help

```
Copy to clipboard
**Important Notices:**
1. This utility and multi-process distributed (single-node or multi-node) GPU training currently only achieves the best performance using the NCCL distributed backend. Thus NCCL backend is the recommended backend to use for GPU training.
2. In your training program, you must parse the command-line argument: `--local-rank=LOCAL_PROCESS_RANK`, which will be provided by this module. If your training program uses GPUs, you should ensure that your code only runs on the GPU device of LOCAL_PROCESS_RANK. This can be done by:
Parsing the local_rank argument

```
>>> import argparse
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument("--local-rank", "--local_rank", type=int)
>>> args = parser.parse_args()

```
Copy to clipboard
Set your device to local rank using either

```
>>> torch.cuda.set_device(args.local_rank)  # before your code runs

```
Copy to clipboard
or

```
>>> with torch.cuda.device(args.local_rank):
>>>    # your code to run
>>>    ...

```
Copy to clipboard
Changed in version 2.0.0: The launcher will passes the `--local-rank=<rank>` argument to your script. From PyTorch 2.0.0 onwards, the dashed `--local-rank` is preferred over the previously used underscored `--local_rank`.
For backward compatibility, it may be necessary for users to handle both cases in their argument parsing code. This means including both `"--local-rank"` and `"--local_rank"` in the argument parser. If only `"--local_rank"` is provided, the launcher will trigger an error: “error: unrecognized arguments: –local-rank=<rank>”. For training code that only supports PyTorch 2.0.0+, including `"--local-rank"` should be sufficient.
3. In your training program, you are supposed to call the following function at the beginning to start the distributed backend. It is strongly recommended that `init_method=env://`. Other init methods (e.g. `tcp://`) may work, but `env://` is the one that is officially supported by this module.

```
>>> torch.distributed.init_process_group(backend='YOUR BACKEND',
>>>                                      init_method='env://')

```
Copy to clipboard
4. In your training program, you can either use regular distributed functions or use [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") module. If your training program uses GPUs for training and you would like to use [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") module, here is how to configure it.

```
>>> model = torch.nn.parallel.DistributedDataParallel(model,
>>>                                                   device_ids=[args.local_rank],
>>>                                                   output_device=args.local_rank)

```
Copy to clipboard
Please ensure that `device_ids` argument is set to be the only GPU device id that your code will be operating on. This is generally the local rank of the process. In other words, the `device_ids` needs to be `[args.local_rank]`, and `output_device` needs to be `args.local_rank` in order to use this utility
5. Another way to pass `local_rank` to the subprocesses via environment variable `LOCAL_RANK`. This behavior is enabled when you launch the script with `--use-env=True`. You must adjust the subprocess example above to replace `args.local_rank` with `os.environ['LOCAL_RANK']`; the launcher will not pass `--local-rank` when you specify this flag.
Warning
`local_rank` is NOT globally unique: it is only unique per process on a machine. Thus, don’t use it to decide if you should, e.g., write to a networked filesystem. See [pytorch/pytorch#12042](https://github.com/pytorch/pytorch/issues/12042) for an example of how things can go wrong if you don’t do this correctly.
## Spawn utility[#](https://docs.pytorch.org/docs/stable/distributed.html#spawn-utility "Link to this heading")
The [Multiprocessing package - torch.multiprocessing](https://docs.pytorch.org/docs/stable/multiprocessing.html#multiprocessing-doc) package also provides a `spawn` function in [`torch.multiprocessing.spawn()`](https://docs.pytorch.org/docs/stable/multiprocessing.html#module-torch.multiprocessing.spawn "torch.multiprocessing.spawn"). This helper function can be used to spawn multiple processes. It works by passing in the function that you want to run and spawns N processes to run it. This can be used for multiprocess distributed training as well.
For references on how to use it, please refer to [PyTorch example - ImageNet implementation](https://github.com/pytorch/examples/tree/master/imagenet)
Note that this function requires Python 3.4 or higher.
## Debugging `torch.distributed` applications[#](https://docs.pytorch.org/docs/stable/distributed.html#debugging-torch-distributed-applications "Link to this heading")
Debugging distributed applications can be challenging due to hard to understand hangs, crashes, or inconsistent behavior across ranks. `torch.distributed` provides a suite of tools to help debug training applications in a self-serve fashion:
### Python Breakpoint[#](https://docs.pytorch.org/docs/stable/distributed.html#python-breakpoint "Link to this heading")
It is extremely convenient to use python’s debugger in a distributed environment, but because it does not work out of the box many people do not use it at all. PyTorch offers a customized wrapper around pdb that streamlines the process.
`torch.distributed.breakpoint` makes this process easy. Internally, it customizes `pdb`’s breakpoint behavior in two ways but otherwise behaves as normal `pdb`.
  1. Attaches the debugger only on one rank (specified by the user).
  2. Ensures all other ranks stop, by using a `torch.distributed.barrier()` that will release once the debugged rank issues a `continue`
  3. Reroutes stdin from the child process such that it connects to your terminal.


To use it, simply issue `torch.distributed.breakpoint(rank)` on all ranks, using the same value for `rank` in each case.
### Monitored Barrier[#](https://docs.pytorch.org/docs/stable/distributed.html#monitored-barrier "Link to this heading")
As of v1.10, [`torch.distributed.monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "torch.distributed.monitored_barrier") exists as an alternative to [`torch.distributed.barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.barrier "torch.distributed.barrier") which fails with helpful information about which rank may be faulty when crashing, i.e. not all ranks calling into [`torch.distributed.monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "torch.distributed.monitored_barrier") within the provided timeout. [`torch.distributed.monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "torch.distributed.monitored_barrier") implements a host-side barrier using `send`/`recv` communication primitives in a process similar to acknowledgements, allowing rank 0 to report which rank(s) failed to acknowledge the barrier in time. As an example, consider the following function where rank 1 fails to call into [`torch.distributed.monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "torch.distributed.monitored_barrier") (in practice this could be due to an application bug or hang in a previous collective):

```
import os
from datetime import timedelta

import torch
import torch.distributed as dist
import torch.multiprocessing as mp


def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    # monitored barrier requires gloo process group to perform host-side sync.
    group_gloo = dist.new_group(backend="gloo")
    if rank not in [1]:
        dist.monitored_barrier(group=group_gloo, timeout=timedelta(seconds=2))


if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    mp.spawn(worker, nprocs=2, args=())

```
Copy to clipboard
The following error message is produced on rank 0, allowing the user to determine which rank(s) may be faulty and investigate further:

```
RuntimeError: Rank 1 failed to pass monitoredBarrier in 2000 ms
 Original exception:
[gloo/transport/tcp/pair.cc:598] Connection closed by peer [2401:db00:eef0:1100:3560:0:1c05:25d]:8594

```
Copy to clipboard
###  `TORCH_DISTRIBUTED_DEBUG`[#](https://docs.pytorch.org/docs/stable/distributed.html#torch-distributed-debug "Link to this heading")
With `TORCH_CPP_LOG_LEVEL=INFO`, the environment variable `TORCH_DISTRIBUTED_DEBUG` can be used to trigger additional useful logging and collective synchronization checks to ensure all ranks are synchronized appropriately. `TORCH_DISTRIBUTED_DEBUG` can be set to either `OFF` (default), `INFO`, or `DETAIL` depending on the debugging level required. Please note that the most verbose option, `DETAIL` may impact the application performance and thus should only be used when debugging issues.
Setting `TORCH_DISTRIBUTED_DEBUG=INFO` will result in additional debug logging when models trained with [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") are initialized, and `TORCH_DISTRIBUTED_DEBUG=DETAIL` will additionally log runtime performance statistics a select number of iterations. These runtime statistics include data such as forward time, backward time, gradient communication time, etc. As an example, given the following application:

```
import os

import torch
import torch.distributed as dist
import torch.multiprocessing as mp


class TwoLinLayerNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.a = torch.nn.Linear(10, 10, bias=False)
        self.b = torch.nn.Linear(10, 1, bias=False)

    def forward(self, x):
        a = self.a(x)
        b = self.b(x)
        return (a, b)


def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    torch.cuda.set_device(rank)
    print("init model")
    model = TwoLinLayerNet().cuda()
    print("init ddp")
    ddp_model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank])

    inp = torch.randn(10, 10).cuda()
    print("train")

    for _ in range(20):
        output = ddp_model(inp)
        loss = output[0] + output[1]
        loss.sum().backward()


if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    os.environ["TORCH_CPP_LOG_LEVEL"]="INFO"
    os.environ[
        "TORCH_DISTRIBUTED_DEBUG"
    ] = "DETAIL"  # set to DETAIL for runtime logging.
    mp.spawn(worker, nprocs=2, args=())

```
Copy to clipboard
The following logs are rendered at initialization time:

```
I0607 16:10:35.739390 515217 logger.cpp:173] [Rank 0]: DDP Initialized with:
broadcast_buffers: 1
bucket_cap_bytes: 26214400
find_unused_parameters: 0
gradient_as_bucket_view: 0
is_multi_device_module: 0
iteration: 0
num_parameter_tensors: 2
output_device: 0
rank: 0
total_parameter_size_bytes: 440
world_size: 2
backend_name: nccl
bucket_sizes: 440
cuda_visible_devices: N/A
device_ids: 0
dtypes: float
master_addr: localhost
master_port: 29501
module_name: TwoLinLayerNet
nccl_async_error_handling: N/A
nccl_blocking_wait: N/A
nccl_debug: WARN
nccl_ib_timeout: N/A
nccl_nthreads: N/A
nccl_socket_ifname: N/A
torch_distributed_debug: INFO

```
Copy to clipboard
The following logs are rendered during runtime (when `TORCH_DISTRIBUTED_DEBUG=DETAIL` is set):

```
I0607 16:18:58.085681 544067 logger.cpp:344] [Rank 1 / 2] Training TwoLinLayerNet unused_parameter_size=0
 Avg forward compute time: 40838608
 Avg backward compute time: 5983335
Avg backward comm. time: 4326421
 Avg backward comm/comp overlap time: 4207652
I0607 16:18:58.085693 544066 logger.cpp:344] [Rank 0 / 2] Training TwoLinLayerNet unused_parameter_size=0
 Avg forward compute time: 42850427
 Avg backward compute time: 3885553
Avg backward comm. time: 2357981
 Avg backward comm/comp overlap time: 2234674

```
Copy to clipboard
In addition, `TORCH_DISTRIBUTED_DEBUG=INFO` enhances crash logging in [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") due to unused parameters in the model. Currently, `find_unused_parameters=True` must be passed into [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") initialization if there are parameters that may be unused in the forward pass, and as of v1.10, all model outputs are required to be used in loss computation as [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") does not support unused parameters in the backwards pass. These constraints are challenging especially for larger models, thus when crashing with an error, [`torch.nn.parallel.DistributedDataParallel()`](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel "torch.nn.parallel.DistributedDataParallel") will log the fully qualified name of all parameters that went unused. For example, in the above application, if we modify `loss` to be instead computed as `loss = output[1]`, then `TwoLinLayerNet.a` does not receive a gradient in the backwards pass, and thus results in `DDP` failing. On a crash, the user is passed information about parameters which went unused, which may be challenging to manually find for large models:

```
RuntimeError: Expected to have finished reduction in the prior iteration before starting a new one. This error indicates that your module has parameters that were not used in producing loss. You can enable unused parameter detection by passing
 the keyword argument `find_unused_parameters=True` to `torch.nn.parallel.DistributedDataParallel`, and by
making sure all `forward` function outputs participate in calculating loss.
If you already have done the above, then the distributed data parallel module wasn't able to locate the output tensors in the return value of your module's `forward` function. Please include the loss function and the structure of the return va
lue of `forward` of your module when reporting this issue (e.g. list, dict, iterable).
Parameters which did not receive grad for rank 0: a.weight
Parameter indices which did not receive grad for rank 0: 0

```
Copy to clipboard
Setting `TORCH_DISTRIBUTED_DEBUG=DETAIL` will trigger additional consistency and synchronization checks on every collective call issued by the user either directly or indirectly (such as DDP `allreduce`). This is done by creating a wrapper process group that wraps all process groups returned by [`torch.distributed.init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") and [`torch.distributed.new_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.new_group "torch.distributed.new_group") APIs. As a result, these APIs will return a wrapper process group that can be used exactly like a regular process group, but performs consistency checks before dispatching the collective to an underlying process group. Currently, these checks include a [`torch.distributed.monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "torch.distributed.monitored_barrier"), which ensures all ranks complete their outstanding collective calls and reports ranks which are stuck. Next, the collective itself is checked for consistency by ensuring all collective functions match and are called with consistent tensor shapes. If this is not the case, a detailed error report is included when the application crashes, rather than a hang or uninformative error message. As an example, consider the following function which has mismatched input shapes into [`torch.distributed.all_reduce()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_reduce "torch.distributed.all_reduce"):

```
import torch
import torch.distributed as dist
import torch.multiprocessing as mp


def worker(rank):
    dist.init_process_group("nccl", rank=rank, world_size=2)
    torch.cuda.set_device(rank)
    tensor = torch.randn(10 if rank == 0 else 20).cuda()
    dist.all_reduce(tensor)
    torch.cuda.synchronize(device=rank)


if __name__ == "__main__":
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29501"
    os.environ["TORCH_CPP_LOG_LEVEL"]="INFO"
    os.environ["TORCH_DISTRIBUTED_DEBUG"] = "DETAIL"
    mp.spawn(worker, nprocs=2, args=())

```
Copy to clipboard
With the `NCCL` backend, such an application would likely result in a hang which can be challenging to root-cause in nontrivial scenarios. If the user enables `TORCH_DISTRIBUTED_DEBUG=DETAIL` and reruns the application, the following error message reveals the root cause:

```
work = default_pg.allreduce([tensor], opts)
RuntimeError: Error when verifying shape tensors for collective ALLREDUCE on rank 0. This likely indicates that input shapes into the collective are mismatched across ranks. Got shapes:  10
[ torch.LongTensor{1} ]

```
Copy to clipboard
Note
For fine-grained control of the debug level during runtime the functions `torch.distributed.set_debug_level()`, `torch.distributed.set_debug_level_from_env()`, and `torch.distributed.get_debug_level()` can also be used.
In addition, `TORCH_DISTRIBUTED_DEBUG=DETAIL` can be used in conjunction with `TORCH_SHOW_CPP_STACKTRACES=1` to log the entire callstack when a collective desynchronization is detected. These collective desynchronization checks will work for all applications that use `c10d` collective calls backed by process groups created with the [`torch.distributed.init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group "torch.distributed.init_process_group") and [`torch.distributed.new_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.new_group "torch.distributed.new_group") APIs.
### torch.distributed.debug HTTP Server[#](https://docs.pytorch.org/docs/stable/distributed.html#torch-distributed-debug-http-server "Link to this heading")
The `torch.distributed.debug` module provides a HTTP server that can be used to debug distributed applications. The server can be started by calling [`torch.distributed.debug.start_debug_server()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.debug.start_debug_server "torch.distributed.debug.start_debug_server"). This allows users to collect data across all workers at runtime.

torch.distributed.debug.start_debug_server(_port =25999_, _worker_port =0_, _start_method =None_, _dump_dir =None_, _dump_interval =60.0_, _enabled_dumps =None_, _handlers =None_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/debug/__init__.py#L27)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.debug.start_debug_server "Link to this definition")

Start the debug server stack on all workers. The frontend debug server is only started on rank0 while the per rank worker servers are started on all ranks.
This server provides an HTTP frontend that allows for debugging slow and deadlocked distributed jobs across all ranks simultaneously. This collects data such as stack traces, FlightRecorder events, and performance profiles.
This depends on dependencies which are not installed by default.
Dependencies: - Jinja2 - aiohttp
WARNING: This is intended to only be used in trusted network environments. The debug server is not designed to be secure and should not be exposed to the public internet. See SECURITY.md for more details.
WARNING: This is an experimental feature and may change at any time.

Parameters:

  * **port** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – The port to start the frontend debug server on.
  * **worker_port** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – The port to start the worker server on. Defaults to 0, which will cause the worker server to bind to an ephemeral port.
  * **start_method** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _|__None_) – The multiprocessing start method to use for the frontend server process. One of “fork”, “spawn”, or “forkserver”. If None, uses the default start method. Using “spawn” is recommended when using CUDA or when fork safety is a concern.
  * **dump_dir** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _|__None_) – Directory to write periodic debug dumps to. If None, periodic dumping is disabled.
  * **dump_interval** ([_float_](https://docs.python.org/3/library/functions.html#float "\(in Python v3.14\)")) – Seconds between periodic dumps. Defaults to 60.
  * **enabled_dumps** ([_set_](https://docs.python.org/3/library/stdtypes.html#set "\(in Python v3.14\)") _[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "\(in Python v3.14\)") _]__|__None_) – Set of handler dump filenames to enable (e.g. {“stacks”, “fr_trace”, “tcpstore”}). If None, all handlers that implement dump() are enabled.
  * **handlers** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "\(in Python v3.14\)") _[__DebugHandler_ _]__|__None_) – List of debug handlers to use. If None, uses the default handlers. See torch.distributed.debug._handlers for the default handlers.


torch.distributed.debug.stop_debug_server()[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/debug/__init__.py#L122)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.debug.stop_debug_server "Link to this definition")

Shutdown the debug server and stop the frontend debug server process.
## Logging[#](https://docs.pytorch.org/docs/stable/distributed.html#logging "Link to this heading")
In addition to explicit debugging support via [`torch.distributed.monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier "torch.distributed.monitored_barrier") and `TORCH_DISTRIBUTED_DEBUG`, the underlying C++ library of `torch.distributed` also outputs log messages at various levels. These messages can be helpful to understand the execution state of a distributed training job and to troubleshoot problems such as network connection failures. The following matrix shows how the log level can be adjusted via the combination of `TORCH_CPP_LOG_LEVEL` and `TORCH_DISTRIBUTED_DEBUG` environment variables.
| `TORCH_CPP_LOG_LEVEL`  | `TORCH_DISTRIBUTED_DEBUG`  | Effective Log Level  |
| --- | --- | --- |
| `ERROR`  | ignored  | Error  |
| `WARNING`  | ignored  | Warning  |
| `INFO`  | ignored  | Info  |
| `INFO`  | `INFO`  | Debug  |
| `INFO`  | `DETAIL`  | Trace (a.k.a. All)  |
Distributed components raise custom Exception types derived from `RuntimeError`:
  * `torch.distributed.DistError`: This is the base type of all distributed exceptions.
  * `torch.distributed.DistBackendError`: This exception is thrown when a backend-specific error occurs. For example, if the `NCCL` backend is used and the user attempts to use a GPU that is not available to the `NCCL` library.
  * `torch.distributed.DistNetworkError`: This exception is thrown when networking libraries encounter errors (ex: Connection reset by peer)
  * `torch.distributed.DistStoreError`: This exception is thrown when the Store encounters an error (ex: TCPStore timeout)


_class_ torch.distributed.DistError[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistError "Link to this definition")

Exception raised when an error occurs in the distributed library

_class_ torch.distributed.DistBackendError[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistBackendError "Link to this definition")

Exception raised when a backend error occurs in distributed

_class_ torch.distributed.DistNetworkError[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistNetworkError "Link to this definition")

Exception raised when a network error occurs in distributed

_class_ torch.distributed.DistStoreError[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistStoreError "Link to this definition")

Exception raised when an error occurs in the distributed store
If you are running single node training, it may be convenient to interactively breakpoint your script. We offer a way to conveniently breakpoint a single rank:

torch.distributed.breakpoint(_rank =0_, _skip =0_, _timeout_s =3600_)[[source]](https://github.com/pytorch/pytorch/blob/v2.11.0/torch/distributed/__init__.py#L94)[#](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.breakpoint "Link to this definition")

Set a breakpoint, but only on a single rank. All other ranks will wait for you to be done with the breakpoint before continuing.

Parameters:

  * **rank** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Which rank to break on. Default: `0`
  * **skip** ([_int_](https://docs.python.org/3/library/functions.html#int "\(in Python v3.14\)")) – Skip the first `skip` calls to this breakpoint. Default: `0`.


Rate this Page
★ ★ ★ ★ ★
Send Feedback
[ previous torch.backends ](https://docs.pytorch.org/docs/stable/backends.html "previous page") [ next Experimental Object Oriented Distributed API ](https://docs.pytorch.org/docs/stable/distributed._dist2.html "next page")
Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.15.4.
[ previous torch.backends ](https://docs.pytorch.org/docs/stable/backends.html "previous page") [ next Experimental Object Oriented Distributed API ](https://docs.pytorch.org/docs/stable/distributed._dist2.html "next page")
On this page
  * [Backends](https://docs.pytorch.org/docs/stable/distributed.html#backends)
    * [Backends that come with PyTorch](https://docs.pytorch.org/docs/stable/distributed.html#backends-that-come-with-pytorch)
    * [Which backend to use?](https://docs.pytorch.org/docs/stable/distributed.html#which-backend-to-use)
    * [Common environment variables](https://docs.pytorch.org/docs/stable/distributed.html#common-environment-variables)
      * [Choosing the network interface to use](https://docs.pytorch.org/docs/stable/distributed.html#choosing-the-network-interface-to-use)
      * [Other NCCL environment variables](https://docs.pytorch.org/docs/stable/distributed.html#other-nccl-environment-variables)
  * [Basics](https://docs.pytorch.org/docs/stable/distributed.html#basics)
  * [Initialization](https://docs.pytorch.org/docs/stable/distributed.html#initialization)
    * [`is_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_available)
    * [`init_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.init_process_group)
    * [`init_device_mesh()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.init_device_mesh)
    * [`is_initialized()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_initialized)
    * [`is_mpi_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_mpi_available)
    * [`is_nccl_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_nccl_available)
    * [`is_gloo_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_gloo_available)
    * [`is_xccl_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_xccl_available)
    * [`batch_isend_irecv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.batch_isend_irecv)
    * [`destroy_process_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.destroy_process_group)
    * [`is_backend_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_backend_available)
    * [`irecv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.irecv)
    * [`is_gloo_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_gloo_available)
    * [`is_initialized()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_initialized)
    * [`is_mpi_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_mpi_available)
    * [`is_nccl_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_nccl_available)
    * [`is_torchelastic_launched()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_torchelastic_launched)
    * [`is_ucc_available()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.is_ucc_available)
    * [`is_torchelastic_launched()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.is_torchelastic_launched)
    * [`get_default_backend_for_device()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_default_backend_for_device)
    * [TCP initialization](https://docs.pytorch.org/docs/stable/distributed.html#tcp-initialization)
    * [Shared file-system initialization](https://docs.pytorch.org/docs/stable/distributed.html#shared-file-system-initialization)
    * [Environment variable initialization](https://docs.pytorch.org/docs/stable/distributed.html#environment-variable-initialization)
    * [Improving initialization time](https://docs.pytorch.org/docs/stable/distributed.html#improving-initialization-time)
  * [Post-Initialization](https://docs.pytorch.org/docs/stable/distributed.html#post-initialization)
    * [`Backend`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend)
      * [`Backend.register_backend()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Backend.register_backend)
    * [`get_backend()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_backend)
    * [`get_rank()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_rank)
    * [`get_world_size()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_world_size)
  * [Shutdown](https://docs.pytorch.org/docs/stable/distributed.html#shutdown)
    * [Reinitialization](https://docs.pytorch.org/docs/stable/distributed.html#reinitialization)
  * [Groups](https://docs.pytorch.org/docs/stable/distributed.html#groups)
    * [`new_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.new_group)
    * [`shrink_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.distributed_c10d.shrink_group)
    * [`get_group_rank()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_group_rank)
    * [`get_global_rank()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_global_rank)
    * [`get_process_group_ranks()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.get_process_group_ranks)
  * [DeviceMesh](https://docs.pytorch.org/docs/stable/distributed.html#devicemesh)
    * [`DeviceMesh`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh)
      * [`DeviceMesh.device_type`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.device_type)
      * [`DeviceMesh.from_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.from_group)
      * [`DeviceMesh.get_all_groups()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_all_groups)
      * [`DeviceMesh.get_coordinate()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_coordinate)
      * [`DeviceMesh.get_group()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_group)
      * [`DeviceMesh.get_local_rank()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_local_rank)
      * [`DeviceMesh.get_rank()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.get_rank)
      * [`DeviceMesh.mesh`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.mesh)
      * [`DeviceMesh.mesh_dim_names`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.device_mesh.DeviceMesh.mesh_dim_names)
  * [Point-to-point communication](https://docs.pytorch.org/docs/stable/distributed.html#point-to-point-communication)
    * [`send()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send)
    * [`recv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv)
    * [`isend()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.isend)
    * [`irecv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.irecv)
    * [`send_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.send_object_list)
    * [`recv_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.recv_object_list)
    * [`batch_isend_irecv()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.batch_isend_irecv)
    * [`P2POp`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.P2POp)
  * [Synchronous and asynchronous collective operations](https://docs.pytorch.org/docs/stable/distributed.html#synchronous-and-asynchronous-collective-operations)
  * [Collective functions](https://docs.pytorch.org/docs/stable/distributed.html#collective-functions)
    * [`broadcast()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast)
    * [`broadcast_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.broadcast_object_list)
    * [`all_reduce()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_reduce)
    * [`reduce()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce)
    * [`all_gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather)
    * [`all_gather_into_tensor()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather_into_tensor)
    * [`all_gather_object()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_gather_object)
    * [`gather()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather)
    * [`gather_object()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.gather_object)
    * [`scatter()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter)
    * [`scatter_object_list()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.scatter_object_list)
    * [`reduce_scatter()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce_scatter)
    * [`reduce_scatter_tensor()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce_scatter_tensor)
    * [`all_to_all_single()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_to_all_single)
    * [`all_to_all()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.all_to_all)
    * [`barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.barrier)
    * [`monitored_barrier()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.monitored_barrier)
    * [`Work`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work)
      * [`Work.block_current_stream()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.block_current_stream)
      * [`Work.boxed()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.boxed)
      * [`Work.exception()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.exception)
      * [`Work.get_future()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.get_future)
      * [`Work.get_future_result()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.get_future_result)
      * [`Work.is_completed()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.is_completed)
      * [`Work.is_success()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.is_success)
      * [`Work.result()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.result)
      * [`Work.source_rank()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.source_rank)
      * [`Work.synchronize()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.synchronize)
      * [`Work.unbox()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.unbox)
      * [`Work.wait()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Work.wait)
    * [`ReduceOp`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.ReduceOp)
    * [`reduce_op`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.reduce_op)
  * [Distributed Key-Value Store](https://docs.pytorch.org/docs/stable/distributed.html#distributed-key-value-store)
    * [`Store`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store)
      * [`Store.__init__()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.__init__)
      * [`Store.add()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.add)
      * [`Store.append()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.append)
      * [`Store.check()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.check)
      * [`Store.clone()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.clone)
      * [`Store.compare_set()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.compare_set)
      * [`Store.delete_key()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.delete_key)
      * [`Store.get()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.get)
      * [`Store.has_extended_api()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.has_extended_api)
      * [`Store.list_keys()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.list_keys)
      * [`Store.multi_get()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.multi_get)
      * [`Store.multi_set()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.multi_set)
      * [`Store.num_keys()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.num_keys)
      * [`Store.queue_len()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.queue_len)
      * [`Store.queue_pop()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.queue_pop)
      * [`Store.queue_push()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.queue_push)
      * [`Store.set()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.set)
      * [`Store.set_timeout()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.set_timeout)
      * [`Store.timeout`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.timeout)
      * [`Store.wait()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.Store.wait)
    * [`TCPStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore)
      * [`TCPStore.__init__()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.__init__)
      * [`TCPStore.host`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.host)
      * [`TCPStore.libuvBackend`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.libuvBackend)
      * [`TCPStore.port`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.TCPStore.port)
    * [`HashStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore)
      * [`HashStore.__init__()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.HashStore.__init__)
    * [`FileStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore)
      * [`FileStore.__init__()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore.__init__)
      * [`FileStore.path`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.FileStore.path)
    * [`PrefixStore`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.PrefixStore)
      * [`PrefixStore.__init__()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.PrefixStore.__init__)
      * [`PrefixStore.underlying_store`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.PrefixStore.underlying_store)
  * [Profiling Collective Communication](https://docs.pytorch.org/docs/stable/distributed.html#profiling-collective-communication)
  * [Optimization with Symmetric Memory](https://docs.pytorch.org/docs/stable/distributed.html#optimization-with-symmetric-memory)
    * [Copy Engine Collectives](https://docs.pytorch.org/docs/stable/distributed.html#copy-engine-collectives)
    * [Higher-Precision Reduction](https://docs.pytorch.org/docs/stable/distributed.html#higher-precision-reduction)
  * [Multi-GPU collective functions](https://docs.pytorch.org/docs/stable/distributed.html#multi-gpu-collective-functions)
  * [Object collectives](https://docs.pytorch.org/docs/stable/distributed.html#object-collectives)
  * [Third-party backends](https://docs.pytorch.org/docs/stable/distributed.html#third-party-backends)
  * [Launch utility](https://docs.pytorch.org/docs/stable/distributed.html#launch-utility)
  * [Spawn utility](https://docs.pytorch.org/docs/stable/distributed.html#spawn-utility)
  * [Debugging `torch.distributed` applications](https://docs.pytorch.org/docs/stable/distributed.html#debugging-torch-distributed-applications)
    * [Python Breakpoint](https://docs.pytorch.org/docs/stable/distributed.html#python-breakpoint)
    * [Monitored Barrier](https://docs.pytorch.org/docs/stable/distributed.html#monitored-barrier)
    * [`TORCH_DISTRIBUTED_DEBUG`](https://docs.pytorch.org/docs/stable/distributed.html#torch-distributed-debug)
    * [torch.distributed.debug HTTP Server](https://docs.pytorch.org/docs/stable/distributed.html#torch-distributed-debug-http-server)
      * [`start_debug_server()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.debug.start_debug_server)
      * [`stop_debug_server()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.debug.stop_debug_server)
  * [Logging](https://docs.pytorch.org/docs/stable/distributed.html#logging)
    * [`DistError`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistError)
    * [`DistBackendError`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistBackendError)
    * [`DistNetworkError`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistNetworkError)
    * [`DistStoreError`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.DistStoreError)
    * [`breakpoint()`](https://docs.pytorch.org/docs/stable/distributed.html#torch.distributed.breakpoint)


[ Edit on GitHub ](https://github.com/pytorch/pytorch/edit/main/docs/source/distributed.md)
[ Show Source ](https://docs.pytorch.org/docs/stable/_sources/distributed.md.txt)
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
