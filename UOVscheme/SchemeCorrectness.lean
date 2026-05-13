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

import UOVscheme.CentralMap
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Fin.Tuple.Basic
import Mathlib.Data.ZMod.Basic

open Matrix

variable {q o v : ℕ} [Fact (Nat.Prime q)]

-- ════════════════════════════════════════════════════════════════
-- Key structure
-- ════════════════════════════════════════════════════════════════

/-- A UOV key pair.

    The secret key is (F, T, T⁻¹) where F is the central map and T is an
    invertible affine transformation on 𝔽_q^(o+v).  The public key is the
    composed map P = F ∘ T, whose structure hides the oil subspace.

    We store det T ≠ 0 as a witness that T is invertible; over `ZMod q` with
    prime `q`, this implies `IsUnit (det T)` and Mathlib's matrix inverse `T⁻¹`
    is a true two-sided inverse (`mul_nonsing_inv`). -/
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
  key.F.eval (oilPart (key.T.mulVec σ)) (vinPart (key.T.mulVec σ))

-- ════════════════════════════════════════════════════════════════
-- Sign and Verify
-- ════════════════════════════════════════════════════════════════

/-- Signing (the algorithmic step, given a pre-solved oil vector).

    In practice, Sign chooses vin randomly, forms the linear system
    M(vin) · oil = y − b(vin), solves it (using `eval_as_linSystem`),
    and calls this function.  Here we parameterise over an already-found
    solution to keep the correctness statement clean. -/
noncomputable def sign (key : UOVKey q o v)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) :
    Fin (o + v) → ZMod q :=
  key.T⁻¹.mulVec (Fin.append oil vin)

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
      (1) `Matrix.mulVec_mulVec` — associativity of `mulVec`
      (2) `Matrix.mul_nonsing_inv` — `T * T⁻¹ = 1` when `IsUnit (det T)`
      (3) `Matrix.one_mulVec` — identity acts trivially on vectors

    Nonzero determinant in the field `ZMod q` (`q` prime) gives `IsUnit (det T)`. -/
theorem correctness (key : UOVKey q o v)
    (y   : Fin o → ZMod q)
    (oil : Fin o → ZMod q)
    (vin : Fin v → ZMod q)
    (h_solve : key.F.eval oil vin = y) :
    key.verify y (key.sign oil vin) := by
  unfold verify publicEval sign oilPart vinPart
  have hTdet : IsUnit key.T.det := (isUnit_iff_ne_zero).mpr key.hT
  -- Step 1: T · (T⁻¹ · (oil ++ vin)) = oil ++ vin
  have hTinv : key.T.mulVec (key.T⁻¹.mulVec (Fin.append oil vin)) =
               Fin.append oil vin := by
    rw [Matrix.mulVec_mulVec (Fin.append oil vin) key.T key.T⁻¹,
      Matrix.mul_nonsing_inv key.T hTdet, Matrix.one_mulVec]
  -- Step 2: rewrite T · σ to oil ++ vin
  rw [hTinv, congr_arg₂ key.F.eval (funext (Fin.append_left oil vin)) (funext (Fin.append_right oil vin))]
  exact h_solve

/-- **Corollary (Sign → Verify)** — same content as `correctness`; name matches
    external docs / hackathon narrative (`sign_then_verify`). -/
theorem sign_then_verify (key : UOVKey q o v)
    (y   : Fin o → ZMod q)
    (oil : Fin o → ZMod q)
    (vin : Fin v → ZMod q)
    (h_solve : key.F.eval oil vin = y) :
    key.verify y (key.sign oil vin) :=
  correctness key y oil vin h_solve

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
