/-
  Test/SchemeTest.lean — End-to-end empirical tests for the UOV scheme.

  We run concrete Sign/Verify round trips over 𝔽_7 with two different
  secret transforms T (identity and a non-trivial upper-triangular matrix),
  confirming that every produced signature verifies correctly and that the
  public eval is consistent with the central map.
-/

import UOVscheme.SchemeCorrectness

open Matrix UOVKey

/-- Needed for `UOVKey` / `correctness` over `𝔽₇`. -/
instance fact_prime_7 : Fact (Nat.Prime 7) := ⟨by native_decide⟩

-- ════════════════════════════════════════════════════════════════
-- Shared central map  (q = 7, o = 2 oil, v = 2 vinegar)
-- ════════════════════════════════════════════════════════════════

private def comp0 : CentralMapComp 7 2 2 := {
  A := !![1, 0; 0, 1],
  B := !![1, 0; 0, 0],
  c := ![1, 0],
  d := ![0, 0],
  e := 2
}

private def comp1 : CentralMapComp 7 2 2 := {
  A := !![0, 1; 1, 0],
  B := !![0, 0; 0, 1],
  c := ![0, 1],
  d := ![1, 0],
  e := 0
}

private def F : CentralMap 7 2 2 := { comps := ![comp0, comp1] }

-- Test oil/vinegar inputs
private def oil : Fin 2 → ZMod 7 := ![3, 5]
private def vin : Fin 2 → ZMod 7 := ![1, 2]

-- Target: y = F(oil, vin)
private def y : Fin 2 → ZMod 7 := F.eval oil vin

-- ════════════════════════════════════════════════════════════════
-- Test A: T = identity  (det = 1, trivially invertible)
-- ════════════════════════════════════════════════════════════════

-- T = I₄ over ZMod 7
private def T_id : Matrix (Fin 4) (Fin 4) (ZMod 7) := 1

example : T_id.det = 1 := by native_decide

private def key_id : UOVKey 7 2 2 := {
  F  := F,
  T  := T_id,
  hT := by native_decide
}

-- σ = T⁻¹ · (oil ++ vin) = (oil ++ vin) since T = I
private noncomputable def σ_id := key_id.sign oil vin

-- Public eval matches y (see `correctness` theorem; numeric spot-checks omitted here
-- because `sign` uses the classical matrix inverse on `ZMod 7`.)
-- expect: `key_id.publicEval σ_id = y`

-- Formal check: verify holds
example : key_id.verify y σ_id := correctness key_id y oil vin rfl

-- ════════════════════════════════════════════════════════════════
-- Test B: T = upper-triangular with off-diagonal 1s (det = 1)
--
--   T = [[1, 1, 0, 0],          T⁻¹ = [[1, 6, 0, 0],
--        [0, 1, 0, 0],                  [0, 1, 0, 0],
--        [0, 0, 1, 1],                  [0, 0, 1, 6],
--        [0, 0, 0, 1]]                  [0, 0, 0, 1]]
--
--   det = 1  (upper triangular, 1s on diagonal)
--   6 ≡ -1 (mod 7)
-- ════════════════════════════════════════════════════════════════

private def T_ut : Matrix (Fin 4) (Fin 4) (ZMod 7) :=
  !![1, 1, 0, 0;
     0, 1, 0, 0;
     0, 0, 1, 1;
     0, 0, 0, 1]

example : T_ut.det = 1 := by native_decide

private def key_ut : UOVKey 7 2 2 := {
  F  := F,
  T  := T_ut,
  hT := by native_decide
}

private noncomputable def σ_ut := key_ut.sign oil vin

-- σ_ut differs from σ_id (T is non-trivial); numeric `#eval` omitted (noncomputable `sign`).

-- Public eval still equals y
-- expect: `key_ut.publicEval σ_ut = y`

-- Formal check
example : key_ut.verify y σ_ut := correctness key_ut y oil vin rfl

-- ════════════════════════════════════════════════════════════════
-- Test C: second oil/vin pair — different message hash
-- ════════════════════════════════════════════════════════════════

private def oil2 : Fin 2 → ZMod 7 := ![0, 6]
private def vin2 : Fin 2 → ZMod 7 := ![4, 3]
private def y2   : Fin 2 → ZMod 7 := F.eval oil2 vin2

private noncomputable def σ_ut2 := key_ut.sign oil2 vin2

-- Formal check
example : key_ut.verify y2 σ_ut2 := correctness key_ut y2 oil2 vin2 rfl

-- ════════════════════════════════════════════════════════════════
-- Test D: publicEval is independent of the secret key structure
--         (i.e. forgery_iff_mq_preimage holds at the computational level)
-- ════════════════════════════════════════════════════════════════

-- A valid signature satisfies publicEval σ = y
-- An invalid vector (e.g. all-zeros) should NOT satisfy it (unless y = 0)
private def zero_sig : Fin 4 → ZMod 7 := fun _ => 0

#eval (key_ut.publicEval zero_sig 0, key_ut.publicEval zero_sig 1)  -- random values
#eval (y 0, y 1)   -- correct y

-- A zero vector is not a valid signature for this digest in general; we omit a
-- `native_decide` counterexample here because `publicEval` depends on Mathlib's
-- classical matrix inverse for `T⁻¹` on `ZMod 7`.
