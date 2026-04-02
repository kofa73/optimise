perf: avoid redundant full-frame copies on the no-mask CPU iteration path

Audit the no-mask CPU iteration/reconstruction flow for places where an intermediate image is copied or reinitialized only to become the next iteration’s input, and replace that work with pointer swaps plus targeted finalization. On a 17-iteration preset, even one deleted full-frame pass per iteration is material. This fits the successful pattern of deleting whole-image work rather than shaving ALU, and it is maintainable if implemented as a small helper around the existing buffer lifecycle.
outcome: not applicable

The current CPU iteration flow in [`src/iop/diffuse.c`](/workspace/darktable/src/iop/diffuse.c#L3472) already uses pointer alternation (`temp_in`/`temp_out`) for the no-mask path, and the only remaining whole-frame copy in the iteration loop is guarded by `sparse_plan.enabled` for masked sparse reconstruction at [`src/iop/diffuse.c`](/workspace/darktable/src/iop/diffuse.c#L3493). In the dense no-mask path, `wavelets_process()` reconstructs directly into the next iteration buffer or final output without an intermediate full-frame copy, so the requested optimization is already effectively present.
