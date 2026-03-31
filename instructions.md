# Optimisation Instructions

<!-- Describe what to optimise and any constraints. This file is passed
     verbatim to the LLM for every task. -->

Optimise the performance of the target file(s). Focus on algorithmic improvements and reducing unnecessary computation.
You MUST NOT touch the OpenCL codepath (`process_cl` and other `..._cl` functions, or ANY code that is ONLY called from those, and not from `process`), as the QA checks and the benchmarks DO NOT verify those paths. If you do, YOU RISK INTRODUCING QUALITY AND PEROFMANCE REGRESSION. YOU MUST NOT DO THAT. DOING SO WILL LEAD TO LOSS OF TRUST, PENALTIES AND TERMINATION OF THE PROCESS. The ONLY reason you may change OpenCL-related ..._cl functions is if you make changes to **SHARED** code (tested by the CPU path), and the OpenCL code needs to be updated in a TRIVIAL way (parameter changes in a function, introduction of a new function with repeated code that can also be used from OpenCL).

Code readability and future maintainability are MORE IMPORTANT than performance. A change that improves performance but makes the code harder to maintain, understand, or refactor MUST NOT be submitted. Specifically:
- NEVER introduce large macros. Use `static inline` functions with `__attribute__((always_inline))` instead. Macros are a maintenance headache — inlined functions give the same performance with type safety and debuggability.
- Repeated code snippets created by unswitching MUST be factored out into separate `always_inline` functions. Do not duplicate logic across branches.
- When you remove or change code, remove or update ALL comments that referred to the old code. Stale comments (describing logic that no longer exists) are a bug. After every change, re-read the surrounding comments and delete any that no longer apply.
