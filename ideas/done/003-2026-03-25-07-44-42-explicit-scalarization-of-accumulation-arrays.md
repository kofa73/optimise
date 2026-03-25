perf: explicitly scalarize accumulation and variance arrays to prevent L1 spills

In the PDE pixel loop, intermediate vectors like `acc`, `variance`, and local convolution sums are declared as `dt_aligned_pixel_t` stack arrays and processed via `for_each_channel`. Because compilers must safely handle potential aliasing when these arrays interact with macros and SIMD regions, they are frequently forced to spill them to L1 memory instead of mapping them cleanly to vector registers. By replacing these inner structures with strictly typed native scalar variables (e.g., `float acc_0, acc_1...`) and manually unrolling their updates, we force the compiler to keep the entire integration pipeline in fast hardware registers, eliminating latent store-to-load forwarding penalties.
outcome: benchmark early abort: Benchmark early abort: 366.331s vs baseline 172.940s (-111.8%, need -2.0%)

# Individual timings
| user | cpu |
| ---- | ---- |
| 5.881 | 60.402 |
| 20.565 | 231.883 |
| 20.624 | 232.709 |
| 19.627 | 224.742 |
| 19.790 | 223.477 |
| 16.636 | 189.535 |
| 16.056 | 184.144 |
| 16.578 | 189.180 |
| 9.780 | 112.787 |
| 22.038 | 249.878 |
| 21.579 | 245.552 |
| 20.535 | 234.146 |
| 14.429 | 159.404 |
| 22.955 | 260.572 |
| 23.883 | 270.018 |
| 12.213 | 139.470 |
| 12.606 | 140.767 |
| 14.171 | 158.345 |
| 18.527 | 214.146 |
| 22.068 | 250.857 |
| 15.790 | 176.850 |

# Totals
| user | cpu |
| ---- | ---- |
| 366.331 | 4148.864 |

# Averages
| user | cpu |
| ---- | ---- |
| 17.444 | 197.565 |
