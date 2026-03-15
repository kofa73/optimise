compute convolutions directly using kernel symmetries to reduce multiplications

The 3x3 anisotropic diffusion kernels possess strong spatial symmetry (e.g., corners are `b11` and `-b11`, top/bottom are `a22`, left/right are `a11`, center is `b22`). Instead of expanding these components into full 9-element `kern_*` arrays and performing 9 independent multiplications per pixel for each diffusion order, we can inline the convolution algebraically. By pre-calculating the 4 unique combinations of the neighbor pixels (e.g., `N0 - N2 - N6 + N8`, `N1 + N7`, `N3 + N5`, and `N4`) and multiplying them directly by the unique kernel weights, we reduce the convolution cost from 36 multiplications to just 16 per channel, while completely eliminating the intermediate kernel arrays.
outcome: improvement
commit: 08db73b634
Reduced sum(user) from 317.712s to 280.618s (~11.7% improvement)

# Individual timings
| user | cpu |
| ---- | ---- |
| 1.398 | 11.372 |
| 66.006 | 727.246 |
| 5.481 | 55.854 |
| 17.404 | 187.053 |
| 17.448 | 187.983 |
| 30.099 | 335.053 |
| 20.025 | 223.125 |
| 25.106 | 279.313 |
| 12.646 | 125.160 |
| 22.577 | 249.563 |
| 15.194 | 165.670 |
| 6.471 | 70.183 |
| 1.968 | 16.483 |
| 8.883 | 94.668 |
| 17.430 | 192.938 |
| 1.087 | 8.550 |
| 0.848 | 6.574 |
| 1.746 | 14.487 |
| 2.215 | 21.697 |
| 4.091 | 43.277 |
| 2.495 | 23.903 |

# Totals
| user | cpu |
| ---- | ---- |
| 280.618 | 3040.152 |

# Averages
| user | cpu |
| ---- | ---- |
| 13.363 | 144.769 |
