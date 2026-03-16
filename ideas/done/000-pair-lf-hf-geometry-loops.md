pair LF and HF gradient and magnitude loops to increase ILP

The local geometry analysis (calculating gradients/laplacians, their magnitudes, and trigonometric components) currently executes in separate, sequential `for_each_channel` loops for the LF and HF layers. By manually inlining and pairing these identical operations side-by-side into unified loops, we provide the processor with multiple independent instruction streams. This allows the CPU to overlap the execution of high-latency instructions like `sqrtf` and floating-point divisions, directly increasing Instruction-Level Parallelism (ILP) and pipeline utilization without altering the mathematical evaluation order.
outcome: not applicable
