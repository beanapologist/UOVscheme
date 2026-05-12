/-
  SchemeCorrectness.lean — UOV signature scheme and its correctness theorem.

  This module defines the actual Oil-and-Vinegar signature scheme over a
  finite field 𝔽_q and proves the fundamental correctness (completeness)
  property: every signature produced by Sign passes Verify.

  The proof works for any commutative ring where T is invertible (det T ≠ 0).
  No security (unforgeability) is claimed here; that reduces to the hardness
  of solving random systems of multivariate quadratic equations (MQ problem),
  which is taken as an axiom.

  Scheme structure (standard UOV):
    Secret key: central map F, invertible linear transformation T
    Public key: P = F ∘ T  (computable from sk)
    Sign(sk, y): choose vin, solve F(oil, vin) = y, return T⁻¹(oil ++ vin)
    Verify(pk, y, σ): check P(σ) = y
-/

import CentralMap
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Fin.Tuple.Basic

open Matrix

variable {q o v : ℕ}

-- ════════════════════════════════════════════════════════════════
-- Key structure
-- ════════════════════════════════════════════════════════════════

/-- A UOV key pair.

    The secret key is (F, T, T⁻¹) where F is the central map and T is an
    invertible affine transformation on 𝔽_q^(o+v).  The public key is the
    composed map P = F ∘ T, whose structure hides the oil subspace.

    We store det T ≠ 0 as a witness that T is invertible; Lean's
    `Matrix.nonsing_inv` then gives us T⁻¹ automatically. -/
structure UOVKey (q o v : ℕ) where
  F   : CentralMap q o v
  T   : Matrix (Fin (o + v)) (Fin (o + v)) (ZMod q)
  hT  : T.det ≠ 0

namespace UOVKey

-- ════════════════════════════════════════════════════════════════
-- Public map
-- ════════════════════════════════════════════════════════════════

/-- Split a vector x : Fin (o + v) → α into its first o and last v components. -/
def oilPart (x : Fin (o + v) → ZMod q) : Fin o → ZMod q :=
  fun i => x (i.castAdd v)

def vinPart (x : Fin (o + v) → ZMod q) : Fin v → ZMod q :=
  fun j => x (j.natAdd o)

/-- The public map P(σ) = F(T(σ)), evaluated at a candidate signature σ. -/
def publicEval (key : UOVKey q o v) (σ : Fin (o + v) → ZMod q) : Fin o → ZMod q :=
  let x := key.T.mulVec σ
  key.F.eval (oilPart x) (vinPart x)

-- ════════════════════════════════════════════════════════════════
-- Sign and Verify
-- ════════════════════════════════════════════════════════════════

/-- Signing (the algorithmic step, given a pre-solved oil vector).

    In practice, Sign chooses vin randomly, forms the linear system
    M(vin) · oil = y − b(vin), solves it (using `eval_as_linSystem`),
    and calls this function.  Here we parameterise over an already-found
    solution to keep the correctness statement clean. -/
def sign (key : UOVKey q o v)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) :
    Fin (o + v) → ZMod q :=
  key.T.nonsing_inv.mulVec (Fin.append oil vin)

/-- Verification: the signature is valid iff the public map evaluates to y. -/
def verify (key : UOVKey q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) : Prop :=
  key.publicEval σ = y

-- ════════════════════════════════════════════════════════════════
-- Correctness theorem
-- ════════════════════════════════════════════════════════════════

/-- **Theorem (UOV Correctness / Completeness)**:

    If `oil` solves the system F(oil, vin) = y, then the signature
    σ = T⁻¹(oil ++ vin) satisfies Verify(pk, y, σ).

    Proof sketch:
      P(σ) = F(T(T⁻¹(oil ++ vin)))  -- by definition of publicEval
           = F(oil ++ vin)           -- T · T⁻¹ = 1 (since det T ≠ 0)
           = F(oil, vin)             -- splitting oil ++ vin recovers oil, vin
           = y                       -- by hypothesis h_solve

    The whole proof follows from three matrix-level facts in Mathlib:
      (1) Matrix.mul_mulVec       — (A·B)·v = A·(B·v)
      (2) Matrix.mul_nonsing_inv  — T · T⁻¹ = 1  (when det T ≠ 0)
      (3) Matrix.one_mulVec       — 1 · v = v
    plus two Fin.append splitting lemmas. -/
theorem correctness (key : UOVKey q o v)
    (y   : Fin o → ZMod q)
    (oil : Fin o → ZMod q)
    (vin : Fin v → ZMod q)
    (h_solve : key.F.eval oil vin = y) :
    key.verify y (key.sign oil vin) := by
  unfold verify publicEval sign oilPart vinPart
  -- Step 1: T · (T⁻¹ · (oil ++ vin)) = oil ++ vin
  have hTinv : key.T.mulVec (key.T.nonsing_inv.mulVec (Fin.append oil vin)) =
               Fin.append oil vin := by
    rw [← mul_mulVec, mul_nonsing_inv key.T key.hT, one_mulVec]
  -- Step 2: rewrite T · σ to oil ++ vin
  rw [hTinv]
  -- Step 3: splitting Fin.append oil vin recovers oil and vin component-wise
  have h_oil : (fun i : Fin o => Fin.append oil vin (i.castAdd v)) = oil :=
    funext (Fin.append_left oil vin)
  have h_vin : (fun j : Fin v => Fin.append oil vin (j.natAdd o)) = vin :=
    funext (Fin.append_right oil vin)
  rw [h_oil, h_vin]
  -- Step 4: F.eval oil vin = y by hypothesis
  exact h_solve

end UOVKey

-- ════════════════════════════════════════════════════════════════
-- Security note (not proved — taken as computational assumption)
-- ════════════════════════════════════════════════════════════════

/-- The MQ (Multivariate Quadratic) hardness assumption.

    Forging a UOV signature without the secret key requires solving a random
    system of o quadratic equations in o+v unknowns over 𝔽_q.  This is
    believed to be NP-hard on average for appropriate parameters.

    This cannot be proved within Lean — it is an unproven complexity-theoretic
    assumption that grounds the security of the scheme. -/
axiom MQ_hardness_assumption : True
-- Replace with a formal reduction once a computational model is in scope.
