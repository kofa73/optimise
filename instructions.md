# Optimisation Instructions

<!-- Describe what to optimise and any constraints. This file is passed
     verbatim to the LLM for every task. -->

Optimise the performance of the target file(s). Focus on algorithmic improvements and reducing unnecessary computation.
You MUST NOT touch the OpenCL codepath (`process_cl` and other `..._cl` functions, or ANY code that is ONLY called from those, and not from `process`), as the QA checks and the benchmarks DO NOT verify those paths. If you do, YOU RISK INTRODUCING QUALITY AND PEROFMANCE REGRESSION. YOU MUST NOT DO THAT. DOING SO WILL LEAD TO LOSS OF TRUST, PENALTIES AND TERMINATION OF THE PROCESS. The ONLY reason you may change OpenCL-related ..._cl functions is if you make changes to **SHARED** code (tested by the CPU path), and the OpenCL code needs to be updated in a TRIVIAL way (parameter changes in a function, introduction of a new function with repeated code that can also be used from OpenCL).

Your PRIMARY OPTIMISATION TARGET is the preset "sharpen demosaicing / AA filter"; improve code paths that are triggered by using that preset. The definition of the preset can be found in /workspace/darktable/src/iop/diffuse.c .
