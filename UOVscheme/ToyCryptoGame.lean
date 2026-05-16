/-
  ToyCryptoGame.lean — End-to-end finite game on 𝔽₇ (o = v = 2).

  Concrete `EUFOracleDist` / `MQExperimentDist` on `Fin 2` plus **proved**
  security theorems for no-win adversaries without global `CoupledDist` or
  `uov_reduces_to_mq` axioms on this parameter set.
-/

import UOVscheme.GameProbability
import UOVscheme.UOVSecurity

namespace ToyCryptoGame

open Matrix UOVKey EUFCMA MQ PublicMap SigningOracle EUFAdversary MQAdversary FinDist
  EUFProb MQProb PPTAlg

instance fact_prime_7 : Fact (Nat.Prime 7) := ⟨by native_decide⟩

abbrev Q := 7
abbrev Oil := 2
abbrev Vin := 2

abbrev ToyΩ := Fin 2
abbrev ToyΞ := Fin 2

private def comp0 : CentralMapComp Q Oil Vin := {
  A := !![1, 0; 0, 1], B := !![1, 0; 0, 0], c := ![1, 0], d := ![0, 0], e := 2 }
private def comp1 : CentralMapComp Q Oil Vin := {
  A := !![0, 1; 1, 0], B := !![0, 0; 0, 1], c := ![0, 1], d := ![1, 0], e := 0 }

noncomputable def toyKey : UOVKey Q Oil Vin := ⟨{ comps := ![comp0, comp1] }, 1, by norm_num⟩

private def oil : Fin Oil → ZMod Q := ![3, 5]
private def vin : Fin Vin → ZMod Q := ![1, 2]
noncomputable def toyY : Fin Oil → ZMod Q := toyKey.F.eval oil vin
noncomputable def toySigma : Fin (Oil + Vin) → ZMod Q := toyKey.sign oil vin

private def yQueried : Fin Oil → ZMod Q := ![1, 0]
private def oilQ : Fin Oil → ZMod Q := ![1, 0]
private def vinQ : Fin Vin → ZMod Q := ![0, 0]
private theorem eval_yQueried : toyKey.F.eval oilQ vinQ = yQueried := by native_decide

noncomputable def O_init : SigningOracle Q Oil Vin := SigningOracle.init toyKey

noncomputable def O_queried : SigningOracle Q Oil Vin :=
  (O_init.query yQueried oilQ vinQ eval_yQueried).1

private def oracleAt : ToyΩ → SigningOracle Q Oil Vin
  | 0 => O_init
  | 1 => O_queried

private def badY : Fin Oil → ZMod Q := ![0, 0]
noncomputable def badSigma : Fin (Oil + Vin) → ZMod Q := fun _ => 0

noncomputable def oracleDistΩ : FinDist ToyΩ :=
  FinDist.uniform

noncomputable def mqDrawWin : MQDraw Q Oil Vin :=
  { P := PublicMap.ofKey toyKey, y := toyY }

noncomputable def mqDrawLose : MQDraw Q Oil Vin :=
  { P := PublicMap.ofKey toyKey, y := badY }

private def drawAt : ToyΞ → MQDraw Q Oil Vin
  | 0 => mqDrawWin
  | 1 => mqDrawLose

noncomputable def mqDistΞ : FinDist ToyΞ := FinDist.uniform

noncomputable def eufWinning : EUFAdversary Q Oil Vin :=
  PPTAlg.ofFn fun _ => (toyY, toySigma)

noncomputable def eufLosing : EUFAdversary Q Oil Vin :=
  PPTAlg.ofFn fun _ => (badY, badSigma)

noncomputable def mqWinning : MQAdversary Q Oil Vin :=
  PPTAlg.ofFn fun _ => fun _ => toySigma

noncomputable def mqLosing : MQAdversary Q Oil Vin :=
  PPTAlg.ofFn fun _ => fun _ => badSigma

private theorem losing_not_0 : ¬ EUFAdversary.wins eufLosing O_init := by native_decide

private theorem losing_not_1 : ¬ EUFAdversary.wins eufLosing O_queried := by native_decide

private theorem mqLosing_not_win : ∀ d : MQDraw Q Oil Vin, ¬ MQDraw.wins mqLosing d := by
  intro d; cases d <;> native_decide

private theorem winning_0 : EUFAdversary.wins eufWinning O_init := by native_decide

private theorem mqWinning_on_winDraw : MQDraw.wins mqWinning mqDrawWin := by native_decide

instance toyEUFOracleDist : EUFOracleDist Q Oil Vin ToyΩ where
  oracleAt := oracleAt
  μSec := fun _ => oracleDistΩ

instance toyMQExperimentDist : MQExperimentDist Q Oil Vin ToyΞ where
  drawAt := drawAt
  μSec := fun _ => mqDistΞ

theorem eufAdvantage_losing (n : ℕ) :
    EUFProb.eufAdvantage eufLosing n = 0 := by
  classical
  unfold EUFProb.eufAdvantage EUFProb.eufWinEvent EUFProb.oracleOf
  simp only [FinDist.uniform, oracleAt, losing_not_0, losing_not_1, if_false, Finset.mem_univ]
  norm_num

theorem mqPreimageAdvantage_losing (n : ℕ) :
    EUFProb.mqPreimageAdvantage eufLosing n = 0 := by
  classical
  unfold EUFProb.mqPreimageAdvantage EUFProb.mqWinEvent EUFProb.oracleOf
  simp only [FinDist.uniform, oracleAt, losing_not_0, losing_not_1, if_false, Finset.mem_univ]
  norm_num

theorem mqAdvantage_losing (n : ℕ) :
    MQProb.mqAdvantage mqLosing n = 0 := by
  classical
  unfold MQProb.mqAdvantage FinDist.prob MQDraw.wins drawAt
  simp only [FinDist.uniform, mqDrawWin, mqDrawLose, mqLosing, PPTAlg.ofFn, PPTAlg.run,
    mqLosing_not_win, if_false, Finset.mem_univ]
  norm_num

theorem mqAdvantage_winning (n : ℕ) :
    MQProb.mqAdvantage mqWinning n = 1 / 2 := by
  classical
  unfold MQProb.mqAdvantage FinDist.prob MQDraw.wins drawAt
  simp only [FinDist.uniform, mqDrawWin, mqDrawLose, mqWinning, PPTAlg.ofFn, PPTAlg.run,
    mqWinning_on_winDraw, if_true, Finset.mem_univ]
  norm_num

theorem eufAdvantage_winning (n : ℕ) :
    EUFProb.eufAdvantage eufWinning n = 1 / 2 := by
  classical
  unfold EUFProb.eufAdvantage EUFProb.eufWinEvent EUFProb.oracleOf
  simp only [FinDist.uniform, oracleAt, winning_0, if_true, Finset.mem_univ, if_false]
  norm_num

theorem mqPreimageAdvantage_winning (n : ℕ) :
    EUFProb.mqPreimageAdvantage eufWinning n = 1 / 2 := by
  classical
  unfold EUFProb.mqPreimageAdvantage EUFProb.mqWinEvent EUFProb.oracleOf
  simp only [FinDist.uniform, oracleAt, winning_0, if_true, Finset.mem_univ, if_false]
  norm_num

theorem coupling_winning (n : ℕ) :
    EUFProb.mqPreimageAdvantage eufWinning n ≤ MQProb.mqAdvantage mqWinning n := by
  rw [mqPreimageAdvantage_winning, mqAdvantage_winning]

theorem coupling_losing (n : ℕ) :
    EUFProb.mqPreimageAdvantage eufLosing n ≤ MQProb.mqAdvantage mqLosing n := by
  rw [mqPreimageAdvantage_losing, mqAdvantage_losing]

theorem toy_euf_cma_losing :
    Negligible (fun n => EUFProb.eufAdvantage eufLosing n) :=
  SecurityModel.negligible_of_forall_zero eufAdvantage_losing

theorem toy_euf_cma_full (n : ℕ) :
    EUFProb.eufAdvantage eufLosing n ≤ MQProb.mqAdvantage mqLosing n :=
  le_trans (EUFProb.euf_advantage_le_mqPreimage eufLosing n) (coupling_losing n)

theorem toy_euf_cma_via_reduction :
    Negligible (fun n => EUFProb.eufAdvantage eufLosing n) :=
  Negligible.of_le (fun n => toy_euf_cma_full n)
    (MQ.hard_of_zeroAdvantage mqLosing mqAdvantage_losing)

theorem toy_uov_euf_cma_mqLosing :
    Negligible (UOV.advantage mqLosing) :=
  MQ.hard_of_zeroAdvantage mqLosing mqAdvantage_losing

end ToyCryptoGame
