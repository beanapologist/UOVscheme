/-
  Test/CentralMapTest.lean — Empirical checks for CentralMap over 𝔽_7.

  These tests evaluate the linearization lemmas on concrete inputs and
  confirm they compute the expected values.  `native_decide` checks that
  the proved equalities actually hold at the computational level.
-/

import UOVscheme.CentralMap
import Mathlib.Data.Matrix.Notation

open Matrix

-- ════════════════════════════════════════════════════════════════
-- Concrete parameters: q = 7, o = 2 oil vars, v = 2 vinegar vars
-- ════════════════════════════════════════════════════════════════

-- Component 0:
--   F_0(oil, vin) = oil[0]·vin[0] + oil[1]·vin[1]   -- A = I₂
--                 + vin[0]²                           -- B = diag(1,0)
--                 + oil[0]                            -- c = (1, 0)
--                 + 2                                 -- constant
def comp0 : CentralMapComp 7 2 2 := {
  A := !![1, 0; 0, 1],
  B := !![1, 0; 0, 0],
  c := ![1, 0],
  d := ![0, 0],
  e := 2
}

-- Component 1:
--   F_1(oil, vin) = oil[0]·vin[1] + oil[1]·vin[0]   -- A = antidiag
--                 + vin[1]²                           -- B = diag(0,1)
--                 + oil[1]                            -- c = (0, 1)
--                 + vin[0]                            -- d = (1, 0)
def comp1 : CentralMapComp 7 2 2 := {
  A := !![0, 1; 1, 0],
  B := !![0, 0; 0, 1],
  c := ![0, 1],
  d := ![1, 0],
  e := 0
}

def testF : CentralMap 7 2 2 := { comps := ![comp0, comp1] }

-- Test inputs
def oil0 : Fin 2 → ZMod 7 := ![3, 5]   -- oil = (3, 5)
def vin0 : Fin 2 → ZMod 7 := ![1, 2]   -- vin = (1, 2)

-- ════════════════════════════════════════════════════════════════
-- Section 1: eval_affine holds on concrete values
-- ════════════════════════════════════════════════════════════════

-- F_0(oil0, vin0) by hand:
--   A·vin = (1·1 + 0·2, 0·1 + 1·2) = (1, 2)
--   oil · (A·vin) = 3·1 + 5·2 = 3 + 10 = 13 ≡ 6 (mod 7)
--   B·vin = (1·1 + 0·2, 0·1 + 0·2) = (1, 0)
--   vin · (B·vin) = 1·1 + 2·0 = 1
--   c · oil = 1·3 + 0·5 = 3
--   d · vin = 0
--   e = 2
--   Total = 6 + 1 + 3 + 0 + 2 = 12 ≡ 5 (mod 7)
#eval comp0.eval oil0 vin0          -- expect: 5

#eval dotProduct oil0 (comp0.linCoeff vin0) + comp0.vinConst vin0  -- expect: 5

-- Confirm: both sides of eval_affine agree
example : comp0.eval oil0 vin0 =
    dotProduct oil0 (comp0.linCoeff vin0) + comp0.vinConst vin0 := by native_decide

-- Same for component 1
#eval comp1.eval oil0 vin0
#eval dotProduct oil0 (comp1.linCoeff vin0) + comp1.vinConst vin0

example : comp1.eval oil0 vin0 =
    dotProduct oil0 (comp1.linCoeff vin0) + comp1.vinConst vin0 := by native_decide

-- ════════════════════════════════════════════════════════════════
-- Section 2: eval_as_linSystem holds on concrete values
-- ════════════════════════════════════════════════════════════════

-- Full map output
#eval testF.eval oil0 vin0   -- should print a pair (mod 7 values)

-- Matrix-vector form: M(vin) ·ᵥ oil + b(vin) should match
#eval (testF.linMatrix vin0).mulVec oil0 + testF.vinConstVec vin0

-- Confirm: the linearization theorem holds numerically
example : testF.eval oil0 vin0 =
    (testF.linMatrix vin0).mulVec oil0 + testF.vinConstVec vin0 := by native_decide

-- ════════════════════════════════════════════════════════════════
-- Section 3: second input pair to exercise more values
-- ════════════════════════════════════════════════════════════════

def oil1 : Fin 2 → ZMod 7 := ![0, 6]
def vin1 : Fin 2 → ZMod 7 := ![4, 3]

#eval testF.eval oil1 vin1
#eval (testF.linMatrix vin1).mulVec oil1 + testF.vinConstVec vin1

example : testF.eval oil1 vin1 =
    (testF.linMatrix vin1).mulVec oil1 + testF.vinConstVec vin1 := by native_decide
