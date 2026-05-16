import UOVscheme.ToyCoupledGame
import UOVscheme.CryptoGame

open FinDist CoupledExperiment ToyCoupledGame

example : toyCoupled.eufMeasure ≤ toyCoupled.mqMeasure :=
  toy_star_measure_le_square

example : toyCoupled.eufMeasure = 1 / 2 :=
  toy_star_measure_eq

example : toyCoupled.mqMeasure = 3 / 4 :=
  toy_square_measure_eq

-- Generic monotonicity on Fin 3 (shadow smaller than shadow)
example : (uniform (α := Fin 3)).prob (fun i => i = 0) ≤
    (uniform (α := Fin 3)).prob (fun i => i ≤ 1) := by
  apply FinDist.prob_mono
  intro ⟨i, hi⟩
  interval_cases i <;> simp at *

example (C : CoupledExperiment (Fin 3)) : 0 ≤ C.advantageGap :=
  C.advantageGap_nonneg
