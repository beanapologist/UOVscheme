/-
  GameProbability.lean — Security advantages as **measures** of win events.

  Outcome spaces `Ω` (EUF oracle) and `Ξ` (MQ draw) are **finite** by design so
  `FinDist.prob` and `prob_mono` apply without a full measure library.
-/

import UOVscheme.CryptoGame
import UOVscheme.EUFCMA

variable {q o v : ℕ} [Fact (Nat.Prime q)]

open FinDist FinMeasureSpace CoupledExperiment EUFCMA MQ PublicMap SigningOracle
  EUFAdversary MQAdversary

-- ════════════════════════════════════════════════════════════════
-- EUF oracle distribution on a finite outcome space Ω
-- ════════════════════════════════════════════════════════════════

class EUFOracleDist (q o v : ℕ) [Fact (Nat.Prime q)] (Ω : Type*)
    [Fintype Ω] [DecidableEq Ω] where
  oracleAt : Ω → SigningOracle q o v
  μSec : ℕ → FinDist Ω

namespace EUFProb

section EUF
variable {Ω : Type*} [Fintype Ω] [DecidableEq Ω]
variable [eufD : EUFOracleDist q o v Ω]

def oracleOf (ω : Ω) : SigningOracle q o v :=
  eufD.oracleAt ω

def eufWinEvent (A : EUFAdversary q o v) (ω : Ω) : Prop :=
  A.wins (oracleOf ω)

def mqWinEvent (A : EUFAdversary q o v) (ω : Ω) : Prop :=
  let (y, σ) := A.forge (oracleOf ω)
  MQ.win (ofKey (oracleOf ω).key) y σ

theorem eufWinEvent_subset_mqWinEvent (A : EUFAdversary q o v) (ω : Ω)
    (h : eufWinEvent A ω) : mqWinEvent A ω :=
  EUFAdversary.wins_implies_mq A (oracleOf ω) h

theorem eufWinEvent_subevent (A : EUFAdversary q o v) :
    ∀ ω : Ω, eufWinEvent A ω → mqWinEvent A ω :=
  fun ω h => eufWinEvent_subset_mqWinEvent A ω h

noncomputable def coupledAt (sec : ℕ) (A : EUFAdversary q o v) : CoupledExperiment Ω where
  space := ⟨eufD.μSec sec⟩
  eufWin := eufWinEvent A
  mqWin := mqWinEvent A
  euf_subset_mq := fun ω h => eufWinEvent_subset_mqWinEvent A ω h
  dec_eufWin := Classical.decPred _
  dec_mqWin := Classical.decPred _

noncomputable def eufAdvantage (A : EUFAdversary q o v) (sec : ℕ) : ℝ := by
  classical
  exact (eufD.μSec sec).prob (eufWinEvent A)

noncomputable def mqPreimageAdvantage (A : EUFAdversary q o v) (sec : ℕ) : ℝ := by
  classical
  exact (eufD.μSec sec).prob (mqWinEvent A)

lemma eufAdvantage_nonneg (A : EUFAdversary q o v) (sec : ℕ) : 0 ≤ eufAdvantage A sec := by
  classical
  unfold eufAdvantage
  exact FinDist.prob_nonneg _ _

lemma mqPreimageAdvantage_nonneg (A : EUFAdversary q o v) (sec : ℕ) :
    0 ≤ mqPreimageAdvantage A sec := by
  classical
  unfold mqPreimageAdvantage
  exact FinDist.prob_nonneg _ _

theorem euf_advantage_le_mqPreimage (A : EUFAdversary q o v) (sec : ℕ) :
    eufAdvantage A sec ≤ mqPreimageAdvantage A sec := by
  classical
  unfold eufAdvantage mqPreimageAdvantage
  exact FinDist.prob_mono (eufD.μSec sec) (eufWinEvent_subevent A)

end EUF

end EUFProb

-- ════════════════════════════════════════════════════════════════
-- MQ black-box experiment on a finite outcome space Ξ
-- ════════════════════════════════════════════════════════════════

structure MQDraw (q o v : ℕ) where
  P : PublicMap q o v
  y : Fin o → ZMod q

namespace MQDraw

variable {q o v : ℕ}

def wins (A : MQAdversary q o v) (d : MQDraw q o v) : Prop :=
  MQ.win d.P d.y (MQAdversary.runOn A d.P d.y)

end MQDraw

class MQExperimentDist (q o v : ℕ) (Ξ : Type*) [Fintype Ξ] [DecidableEq Ξ] where
  drawAt : Ξ → MQDraw q o v
  μSec : ℕ → FinDist Ξ

namespace MQProb

section MQ
variable {Ξ : Type*} [Fintype Ξ] [DecidableEq Ξ]
variable [mqD : MQExperimentDist q o v Ξ]

noncomputable def mqAdvantage (A : MQAdversary q o v) (sec : ℕ) : ℝ := by
  classical
  exact (mqD.μSec sec).prob (fun ξ => MQDraw.wins A (mqD.drawAt ξ))

lemma mqAdvantage_nonneg (A : MQAdversary q o v) (sec : ℕ) : 0 ≤ mqAdvantage A sec := by
  classical
  unfold mqAdvantage
  exact FinDist.prob_nonneg _ _

end MQ

end MQProb

-- ════════════════════════════════════════════════════════════════
-- Push-forward / cross-space coupling (axiom layer)
-- ════════════════════════════════════════════════════════════════

/-- Cross-space coupling: oracle-state MQ preimage mass ≤ black-box MQ advantage. -/
axiom mqPreimage_le_mq_axiom (q o v : ℕ) [Fact (Nat.Prime q)] (Ω Ξ : Type*)
    [Fintype Ω] [DecidableEq Ω] [Fintype Ξ] [DecidableEq Ξ]
    [eufD : EUFOracleDist q o v Ω] [mqD : MQExperimentDist q o v Ξ]
    (A : EUFAdversary q o v) (B : MQAdversary q o v) (sec : ℕ) :
    @EUFProb.mqPreimageAdvantage q o v _ Ω _ _ eufD A sec ≤
      @MQProb.mqAdvantage q o v _ Ξ _ _ mqD B sec

class CoupledDist (q o v : ℕ) [Fact (Nat.Prime q)] (Ω Ξ : Type*)
    [Fintype Ω] [DecidableEq Ω] [Fintype Ξ] [DecidableEq Ξ]
    [eufD : EUFOracleDist q o v Ω] [mqD : MQExperimentDist q o v Ξ] where
  mqPreimage_le_mq := mqPreimage_le_mq_axiom q o v Ω Ξ _ _ _ _ eufD mqD
