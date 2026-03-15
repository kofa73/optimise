Pair the 4 `compute_convolution` calls into 2 `for_each_channel` loops

Pair the 4 `compute_convolution` calls into 2 `for_each_channel` loops: derivatives 0+2 (sharing gradient angle data, applied to LF and HF sums) and derivatives 1+3 (sharing laplacian angle data, applied to LF and HF sums). Each loop computes 2 derivatives in one pass, halving loop overhead and improving register reuse for shared angle values. Careful (bug danger): using isotropy_type[0] for both derivatives 0 and 2 (and [1] for both 1 and 3). Use correct per-derivative isotropy_type
