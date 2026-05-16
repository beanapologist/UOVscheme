import UOVscheme.EUFCMA
import UOVscheme.UOVSecurity

open Matrix UOVKey EUFCMA MQ SigningOracle UOVSecurity.Reduction

instance fact_prime_7 : Fact (Nat.Prime 7) := ⟨by native_decide⟩

private def comp0 : CentralMapComp 7 2 2 := {
  A := !![1, 0; 0, 1], B := !![1, 0; 0, 0], c := ![1, 0], d := ![0, 0], e := 2 }
private def comp1 : CentralMapComp 7 2 2 := {
  A := !![0, 1; 1, 0], B := !![0, 0; 0, 1], c := ![0, 1], d := ![1, 0], e := 0 }
private def F : CentralMap 7 2 2 := { comps := ![comp0, comp1] }
private def T : Matrix (Fin 4) (Fin 4) (ZMod 7) := 1
private def key : UOVKey 7 2 2 := ⟨F, T, by norm_num⟩

private def oil : Fin 2 → ZMod 7 := ![3, 5]
private def vin : Fin 2 → ZMod 7 := ![1, 2]
private def y : Fin 2 → ZMod 7 := F.eval oil vin
private noncomputable def σ := key.sign oil vin

-- Alice's oracle: two chosen-message queries, then Eve must forge a fresh digest
private def O0 : SigningOracle 7 2 2 := SigningOracle.init key

private def y1 : Fin 2 → ZMod 7 := ![1, 0]
private def oil1 : Fin 2 → ZMod 7 := ![1, 0]
private def vin1 : Fin 2 → ZMod 7 := ![0, 0]
private theorem h1 : key.F.eval oil1 vin1 = y1 := by native_decide

private def O1 : SigningOracle 7 2 2 × Fin 4 → ZMod 7 := O0.query y1 oil1 vin1 h1
private def O1' : SigningOracle 7 2 2 := O1.1
private def σ1 : Fin 4 → ZMod 7 := O1.2

example : O1'.key.verify y1 σ1 := SigningOracle.query_spec O0 y1 oil1 vin1 h1

example : y1 ∈ O1'.log := SigningOracle.query_mem_log O0 y1 oil1 vin1 h1

-- Forgery on a digest Alice never signed (empty log path — same as before)
example : adversaryWins (SigningOracle.init key) y σ :=
  ⟨correctness key y oil vin rfl, by intro z hz; cases hz⟩

example : MQ.win (PublicMap.ofKey key) y σ :=
  wins_implies_mq_preimage ⟨key, [], y, σ⟩ (adversaryWins_iff_experiment _ _ _ |>.mp
    ⟨correctness key y oil vin rfl, by intro z hz; cases hz⟩)

-- `uov_euf_cma` needs `[EUFOracleDist] [MQExperimentDist] [CoupledDist]` instances
-- (see `GameProbability.lean`); toy 𝔽₇ parameters are not packaged as a `Fintype`.
