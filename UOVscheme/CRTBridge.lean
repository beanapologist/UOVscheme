/-
  CRTBridge.lean — Chinese remainder theorem as an explicit encode/decode bridge.

  ## Mathematical content (all from Mathlib)

  When `Nat.Coprime m n`, Mathlib defines a **ring isomorphism**

    `ZMod.chineseRemainder h : ZMod (m * n) ≃+* ZMod m × ZMod n`.

  * **Encode** (forward): send `a : ZMod (m*n)` to its pair of residues `(a mod m, a mod n)`.
  * **Decode** (inverse): given compatible residues, **glue** them to the unique class
    `mod (m*n)` (implemented via `Nat.chineseRemainder` in Mathlib).

  This is a **perfect** bridge: inverse exists in polynomial time on public data.
  It is **not** a one-way function; it complements the UOV story (where hardness is MQ)
  as a clean “finite synchrony” example: two moduli cooperate iff they are coprime.

  ## Pedagogical link to the witness/observer vocabulary (informal)

  One can read the *pair* `(a mod m, a mod n)` as **two observable channels**—what you
  see after projecting to each factor—and the unique class `a : ZMod (m*n)` as the
  **single witness object** those channels jointly determine.  CRT is then the theorem
  that, under coprimality, the two observations **lock** a unique global state.  This is
  analogy only; the formal content below is pure ring theory.
-/

import Mathlib.Data.ZMod.Basic

variable {m n : ℕ}

namespace CRTBridge

/-- The CRT ring isomorphism for coprime `m`, `n` (Mathlib’s `ZMod.chineseRemainder`). -/
noncomputable abbrev crtRingEquiv (h : Nat.Coprime m n) : ZMod (m * n) ≃+* ZMod m × ZMod n :=
  ZMod.chineseRemainder h

/-- **Encode**: simultaneous reduction modulo `m` and `n`. -/
noncomputable def encode (h : Nat.Coprime m n) (a : ZMod (m * n)) : ZMod m × ZMod n :=
  crtRingEquiv h a

/-- **Decode**: glue a pair of residues to `ZMod (m * n)`. -/
noncomputable def decode (h : Nat.Coprime m n) (p : ZMod m × ZMod n) : ZMod (m * n) :=
  (crtRingEquiv h).symm p

@[simp]
theorem decode_encode (h : Nat.Coprime m n) (a : ZMod (m * n)) : decode h (encode h a) = a :=
  (crtRingEquiv h).symm_apply_apply a

@[simp]
theorem encode_decode (h : Nat.Coprime m n) (p : ZMod m × ZMod n) : encode h (decode h p) = p :=
  (crtRingEquiv h).apply_symm_apply p

/-- The bridge is bijective on carriers (so neither direction is “lossy”). -/
theorem encode_bijective (h : Nat.Coprime m n) : Function.Bijective (encode h) :=
  (crtRingEquiv h).bijective

theorem encode_surjective (h : Nat.Coprime m n) : Function.Surjective (encode h) :=
  (encode_bijective h).surjective

theorem encode_injective (h : Nat.Coprime m n) : Function.Injective (encode h) :=
  (encode_bijective h).injective

theorem decode_injective (h : Nat.Coprime m n) : Function.Injective (decode h) :=
  (crtRingEquiv h).symm.injective

theorem decode_surjective (h : Nat.Coprime m n) : Function.Surjective (decode h) :=
  (crtRingEquiv h).symm.surjective

end CRTBridge
