/-
  ToyCoupledGame.lean — Flashlight / shadow analogy on `Ω = Fin 4`.

  Outcomes `0,1` light only the **star** (EUF); `0,1,2` light the **square** (MQ).
  Uniform `μ` on four wall positions.  Proves measure monotonicity end-to-end.
-/

import UOVscheme.CryptoGame

open FinDist FinMeasureSpace CoupledExperiment

/-- Wall positions under the flashlight. -/
abbrev ToyΩ := Fin 4

/-- **Small star** stencil: positions `0` and `1`. -/
def starWin (ω : ToyΩ) : Prop :=
  ω.val ≤ 1

/-- **Big square** stencil: positions `0`, `1`, and `2` (covers the star). -/
def squareWin (ω : ToyΩ) : Prop :=
  ω.val ≤ 2

theorem star_subset_square : starWin ⊆ₑ squareWin := by
  intro ω h
  unfold squareWin starWin at *
  omega

instance : DecidablePred starWin := fun ⟨i, _⟩ => by
  dsimp [starWin]
  infer_instance

instance : DecidablePred squareWin := fun ⟨i, _⟩ => by
  dsimp [squareWin]
  infer_instance

/-- Uniform flashlight over four positions. -/
noncomputable def toySpace : FinMeasureSpace ToyΩ :=
  ⟨FinDist.uniform⟩

/-- Coupled toy experiment: star event nested in square event. -/
noncomputable def toyCoupled : CoupledExperiment ToyΩ where
  space := toySpace
  eufWin := starWin
  mqWin := squareWin
  euf_subset_mq := star_subset_square
  dec_eufWin := inferInstance
  dec_mqWin := inferInstance

/-- Star area ≤ square area: `μ(star) ≤ μ(square) = 3/4`. -/
theorem toy_star_measure_le_square : toyCoupled.eufMeasure ≤ toyCoupled.mqMeasure :=
  toyCoupled.eufMeasure_le_mqMeasure

/-- Closed form: `μ(star) = 2/4 = 1/2`. -/
theorem toy_star_measure_eq : toyCoupled.eufMeasure = 1 / 2 := by
  native_decide

/-- Closed form: `μ(square) = 3/4`. -/
theorem toy_square_measure_eq : toyCoupled.mqMeasure = 3 / 4 := by
  native_decide
