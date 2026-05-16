import UOVscheme.SecurityModel
import UOVscheme.EUFCMA

open PPTAlg IsPolynomial PPT EUFCMA EUFAdversary SigningOracle

example : IsPolynomial (PPTAlg.ofFn (fun (x : ℕ) => x * 2)).cost :=
  (PPTAlg.ofFn _).cost_poly

example (A : PPT ℕ ℕ) (B : PPT ℕ ℕ) (n : ℕ) :
    (A.comp B).cost n = A.cost n + B.cost n :=
  PPTAlg.comp_cost A B n

example (A : PPT ℕ ℕ) (B : PPT ℕ ℕ) :
    IsPolynomial (A.comp B).cost :=
  (A.comp B).cost_poly

example (A : EUFAdversary 7 2 2) (O : SigningOracle 7 2 2) :
    IsPolynomial A.cost :=
  A.cost_poly
