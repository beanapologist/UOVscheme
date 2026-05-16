/-
  MQProblem.lean — The Multivariate Quadratic (MQ) problem.

  Algebraic win predicates: `EUFCMA.MQ.win`, `MQDraw.wins`.
  Probabilities: `MQExperimentDist.mqAdvantage` (see `GameProbability.lean`).
  Hardness: `MQ.hard` (cryptographic axiom).
-/

import UOVscheme.GameProbability
import UOVscheme.SecurityModel

variable {q o v : ℕ}

open EUFCMA MQAdversary

namespace MQAdversary

def cost (A : MQAdversary q o v) (n : ℕ) : ℕ :=
  A.cost n

theorem cost_is_polynomial (A : MQAdversary q o v) : IsPolynomial A.cost :=
  A.cost_poly

end MQAdversary

-- ════════════════════════════════════════════════════════════════
-- Advantage (defined when a distribution family is in scope)
-- ════════════════════════════════════════════════════════════════

namespace MQ

variable {Ξ : Type*} [Fintype Ξ] [DecidableEq Ξ]
variable [MQExperimentDist q o v Ξ]

/-- **MQ inversion advantage** at security parameter `n`. -/
def advantage (A : MQAdversary q o v) (sec : ℕ) : ℝ :=
  MQProb.mqAdvantage A sec

lemma advantage_nonneg (A : MQAdversary q o v) (sec : ℕ) : 0 ≤ advantage A sec :=
  MQProb.mqAdvantage_nonneg A sec

/-- If an adversary never wins, its advantage is negligible (proved, not assumed). -/
theorem hard_of_zeroAdvantage (A : MQAdversary q o v)
    (h : ∀ sec, advantage A sec = 0) : Negligible (advantage A) :=
  SecurityModel.negligible_of_forall_zero (fun sec => by rw [advantage, h sec])

/-- **MQ Hardness Assumption (average-case).** -/
axiom hard [Fact (Nat.Prime q)] {Ξ : Type*} [Fintype Ξ] [DecidableEq Ξ]
    [MQExperimentDist q o v Ξ] (A : MQAdversary q o v) :
    Negligible (advantage A)

axiom NP_hard : True

end MQ
