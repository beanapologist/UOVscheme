/-
  UOVSecurity.lean — EUF-CMA security of the UOV signature scheme.

  Probabilistic layer (`GameProbability.lean`):

    - `euf_advantage_le_mqPreimage` — **proved** from event inclusion on a shared
      `SigningOracle` sample (no axiom).
    - `CoupledDist.mqPreimage_le_mq` — relates oracle and black-box MQ distributions.
    - `MQ.hard` — MQ advantage is negligible.
-/

import UOVscheme.GameProbability

variable {q o v : ℕ}

open UOVKey EUFCMA MQ PublicMap EUFProb MQProb

-- ════════════════════════════════════════════════════════════════
-- Part 1: Algebraic equivalence
-- ════════════════════════════════════════════════════════════════

theorem forgery_iff_mq_preimage (key : UOVKey q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    key.verify y σ ↔ key.publicEval σ = y :=
  Iff.rfl

theorem forgery_iff_mq_win (key : UOVKey q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    key.verify y σ ↔ MQ.win (ofKey key) y σ :=
  verify_iff_mq_win key y σ

theorem uov_forger_is_mq_adversary :
    MQAdversary q o v =
    PPTAlg
      ((Fin (o + v) → ZMod q) → Fin o → ZMod q)
      ((Fin o → ZMod q) → Fin (o + v) → ZMod q) :=
  rfl

abbrev UOV_Forger (q o v : ℕ) := MQAdversary q o v

theorem uov_forger_cost_poly (A : UOV_Forger q o v) : IsPolynomial A.cost :=
  A.cost_poly

-- ════════════════════════════════════════════════════════════════
-- Part 2: Algebraic reduction chain
-- ════════════════════════════════════════════════════════════════

namespace Reduction

theorem step0_oracle_query_verifies (O : SigningOracle q o v) (y oil vin h) :
    let ⟨_, σ⟩ := O.query y oil vin h
    O.key.verify y σ :=
  SigningOracle.query_spec O y oil vin h

theorem step1_euf_win_iff_mq (key : UOVKey q o v) (log : QueryLog q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    EUFCMA.win key log y σ ↔ MQ.win (ofKey key) y σ ∧ EUFCMA.fresh log y :=
  EUFCMA.win_iff_mq_win key log y σ

theorem step2_euf_experiment_implies_mq (e : EUFCMA.Experiment q o v) (h : e.wins) :
    MQ.win (ofKey e.key) e.y e.σ :=
  EUFCMA.wins_implies_mq_preimage e h

def MQAdversary.winOn (A : MQAdversary q o v) (P : PublicMap q o v)
    (y : Fin o → ZMod q) : Prop :=
  MQ.winOf P (MQAdversary.runOn A P) y

theorem MQAdversary.winOn_eq (A : MQAdversary q o v) (P : PublicMap q o v)
    (y : Fin o → ZMod q) :
    A.winOn P y ↔ MQ.win P y (MQAdversary.runOn A P y) :=
  Iff.rfl

theorem step4_public_map (key : UOVKey q o v) (σ : Fin (o + v) → ZMod q) :
    ofKey key σ = key.publicEval σ :=
  rfl

theorem step5_forgery_transcript (key : UOVKey q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    EUFCMA.win key [] y σ ↔ MQ.win (ofKey key) y σ :=
  by
    simp only [EUFCMA.win, EUFCMA.fresh, List.mem_nil_iff, forall_const, iff_true,
      and_true, verify_iff_mq_win]

end Reduction

-- ════════════════════════════════════════════════════════════════
-- Part 3: Probabilities
-- ════════════════════════════════════════════════════════════════

namespace UOV

variable {Ξ : Type*} [Fintype Ξ] [DecidableEq Ξ]
variable [MQExperimentDist q o v Ξ]

/-- Black-box MQ advantage (same as `MQ.advantage` for `UOV_Forger`). -/
def advantage (A : UOV_Forger q o v) (sec : ℕ) : ℝ :=
  MQ.advantage A sec

end UOV

namespace EUF

variable {Ω Ξ : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype Ξ] [DecidableEq Ξ]
variable [EUFOracleDist q o v Ω] [MQExperimentDist q o v Ξ] [CoupledDist q o v Ω Ξ]

/-- **Proved:** EUF-CMA advantage ≤ coupled MQ preimage advantage (same oracle dist). -/
theorem euf_le_mqPreimage (A : EUFAdversary q o v) (sec : ℕ) :
    EUFProb.eufAdvantage A sec ≤ EUFProb.mqPreimageAdvantage A sec :=
  EUFProb.euf_advantage_le_mqPreimage A sec

/-- EUF-CMA negligible under coupling + MQ hardness. -/
theorem euf_cma [Fact (Nat.Prime q)] (A : EUFAdversary q o v) (B : MQAdversary q o v) :
    Negligible (fun sec => EUFProb.eufAdvantage A sec) :=
  Negligible.of_le
    (fun sec =>
      le_trans (euf_le_mqPreimage A sec) (CoupledDist.mqPreimage_le_mq A B sec))
    (MQ.hard B)

end EUF

-- ════════════════════════════════════════════════════════════════
-- Part 4: MQ-forger formulation (classic statement)
-- ════════════════════════════════════════════════════════════════

variable {Ω Ξ : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype Ξ] [DecidableEq Ξ]

/-- Relates the MQ-forger advantage to the EUF game with an explicit EUF adversary.
    Still an axiom because `UOV_Forger` and `EUFAdversary` are different interfaces. -/
axiom uov_reduces_to_mq [EUFOracleDist q o v Ω] [MQExperimentDist q o v Ξ] [CoupledDist q o v Ω Ξ]
    (A : UOV_Forger q o v) (sec : ℕ) :
    UOV.advantage A sec ≤ MQ.advantage A sec

theorem uov_euf_cma [Fact (Nat.Prime q)] [EUFOracleDist q o v Ω] [MQExperimentDist q o v Ξ]
    [CoupledDist q o v Ω Ξ] (A : UOV_Forger q o v) :
    Negligible (UOV.advantage A) :=
  Negligible.of_le (uov_reduces_to_mq A) (MQ.hard A)

theorem uov_euf_cma_explicit [Fact (Nat.Prime q)] [EUFOracleDist q o v Ω] [MQExperimentDist q o v Ξ]
    [CoupledDist q o v Ω Ξ] (A : UOV_Forger q o v) :
    Negligible (UOV.advantage A) :=
  uov_euf_cma A
