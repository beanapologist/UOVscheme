/-
  CentralMap.lean — Actual UOV central map over a finite field.

  The UOV central map F : 𝔽_q^o × 𝔽_q^v → 𝔽_q^o consists of o quadratic
  polynomials, each with no oil×oil cross terms. This is the property that
  makes signing work: fixing the vinegar variables reduces F to a linear
  (actually affine) system in the oil variables, which can be solved by
  Gaussian elimination.

  The ambient field is 𝔽_q = ZMod q, instantiated as a field when q is prime.
  Variables: o oil variables, v vinegar variables, n = o + v total.
-/

import Mathlib.Data.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.DotProduct
import Mathlib.Data.ZMod.Basic
import Mathlib.RingTheory.Finiteness

open Matrix

variable {q o v : ℕ}

-- ════════════════════════════════════════════════════════════════
-- Single polynomial component
-- ════════════════════════════════════════════════════════════════

/-- One polynomial in the UOV central map.

    F_k(oil, vin) = ⟨oil, A_k · vin⟩ + ⟨vin, B_k · vin⟩ + ⟨c_k, oil⟩ + ⟨d_k, vin⟩ + e_k

    The oil×oil block is **zero by construction** — only A_k (oil×vinegar)
    and B_k (vinegar×vinegar) appear as quadratic terms.  This is what
    distinguishes OV from a generic multivariate quadratic system.
-/
structure CentralMapComp (q o v : ℕ) where
  A : Matrix (Fin o) (Fin v) (ZMod q)  -- oil-vinegar cross terms
  B : Matrix (Fin v) (Fin v) (ZMod q)  -- vinegar-vinegar quadratic terms
  c : Fin o → ZMod q                   -- linear oil coefficients
  d : Fin v → ZMod q                   -- linear vinegar coefficients
  e : ZMod q                           -- constant term

namespace CentralMapComp

/-- Evaluate the polynomial at (oil, vin). -/
def eval (f : CentralMapComp q o v)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) : ZMod q :=
  dotProduct oil (f.A.mulVec vin) +
  dotProduct vin (f.B.mulVec vin) +
  dotProduct f.c oil +
  dotProduct f.d vin +
  f.e

/-- For fixed vinegar, the linear coefficient vector: (A_k)ᵀ · vin + c_k.
    Evaluating f at (oil, vin) is linear in oil with this coefficient vector. -/
def linCoeff (f : CentralMapComp q o v) (vin : Fin v → ZMod q) : Fin o → ZMod q :=
  f.A.mulVec vin + f.c

/-- The vinegar-only contribution (constant w.r.t. oil). -/
def vinConst (f : CentralMapComp q o v) (vin : Fin v → ZMod q) : ZMod q :=
  dotProduct vin (f.B.mulVec vin) + dotProduct f.d vin + f.e

/-- **Linearization lemma**: for fixed vinegar, f is affine in oil.

    f(oil, vin) = ⟨oil, linCoeff(vin)⟩ + vinConst(vin)

    Proof: expand both sides; the oil×oil-free structure makes this exact.
    The key step is dotProduct_add on the right and dotProduct_comm to swap
    the c · oil term. -/
lemma eval_affine (f : CentralMapComp q o v)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) :
    f.eval oil vin = dotProduct oil (f.linCoeff vin) + f.vinConst vin := by
  simp only [eval, linCoeff, vinConst, dotProduct_add, Pi.add_apply,
             dotProduct_comm f.c oil]
  abel

end CentralMapComp

-- ════════════════════════════════════════════════════════════════
-- Full central map (o components)
-- ════════════════════════════════════════════════════════════════

/-- The full UOV central map: o polynomial components over o+v variables. -/
structure CentralMap (q o v : ℕ) where
  comps : Fin o → CentralMapComp q o v

namespace CentralMap

/-- Evaluate the central map at (oil, vin), producing a vector in 𝔽_q^o. -/
def eval (F : CentralMap q o v)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) : Fin o → ZMod q :=
  fun k => (F.comps k).eval oil vin

/-- Linear coefficient matrix M(vin): row k is linCoeff of component k.
    When vinegar is fixed, F(·, vin) = M(vin) · oil + b(vin). -/
def linMatrix (F : CentralMap q o v) (vin : Fin v → ZMod q) :
    Matrix (Fin o) (Fin o) (ZMod q) :=
  fun k => (F.comps k).linCoeff vin

/-- Constant vector b(vin): entry k is vinConst of component k. -/
def vinConstVec (F : CentralMap q o v) (vin : Fin v → ZMod q) : Fin o → ZMod q :=
  fun k => (F.comps k).vinConst vin

/-- **Central linearization theorem**: the full map equals a matrix product plus constant.

    F(oil, vin) = M(vin) ·ᵥ oil + b(vin)

    This is the critical property enabling signing: given a target y ∈ 𝔽_q^o
    and a vinegar choice vin, solving for oil reduces to the linear system
    M(vin) · oil = y − b(vin). -/
theorem eval_as_linSystem (F : CentralMap q o v)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) :
    F.eval oil vin = F.linMatrix vin |>.mulVec oil + F.vinConstVec vin := by
  funext k
  simp only [eval, linMatrix, vinConstVec, Pi.add_apply, mulVec_apply]
  rw [dotProduct_comm]
  exact (F.comps k).eval_affine oil vin

end CentralMap
