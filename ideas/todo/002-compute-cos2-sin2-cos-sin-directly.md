Compute cos²θ, sin²θ, and cosθ·sinθ directly from squared gradient magnitude (gx²/m², gy²/m², gx·gy/m²) instead of normalizing the gradient first then squaring.

Reuses gx² and gy² already computed for magnitude, eliminating redundant squarings and one division per gradient direction per channel.
