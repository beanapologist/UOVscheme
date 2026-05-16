/-
  CryptoGame.lean — Finite **measure spaces** for game-based cryptography.

  ### Measure-theoretic reading

  A `FinDist Ω` is a probability measure `μ` on a finite outcome space `Ω`
  (each atom `ω` has mass `μ({ω}) = pmf ω`, and `μ(Ω) = 1`).

  A decidable predicate `E : Ω → Prop` is our stand-in for a **measurable**
  subset; `measure M E` is its probability mass.

  * **Monotonicity** (`measure_mono`): if `E ⊆ₑ F` pointwise, then `μ(E) ≤ μ(F)`.
  * **Coupling** (`CoupledExperiment`): one measure space, nested events on the same `ω`.
  * **Decidable events**: every set we measure is constructively decidable.
-/

import Mathlib.Algebra.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith

noncomputable section

open scoped BigOperators

structure FinDist (Ω : Type*) [Fintype Ω] [DecidableEq Ω] where
  pmf : Ω → ℝ
  nonneg : ∀ ω, 0 ≤ pmf ω
  sum_one : ∑ ω, pmf ω = 1

namespace FinDist

variable {Ω : Type*} [Fintype Ω] [DecidableEq Ω]

def prob (μ : FinDist Ω) (E : Ω → Prop) [DecidablePred E] : ℝ :=
  ∑ ω, if E ω then μ.pmf ω else 0

lemma prob_nonneg (μ : FinDist Ω) (E : Ω → Prop) [DecidablePred E] : 0 ≤ μ.prob E := by
  unfold prob
  refine Finset.sum_nonneg fun ω _ => ?_
  split_ifs <;> [exact μ.nonneg ω; simp]

lemma prob_le_one (μ : FinDist Ω) (E : Ω → Prop) [DecidablePred E] : μ.prob E ≤ 1 := by
  unfold prob
  have hle : ∑ ω, (if E ω then μ.pmf ω else 0) ≤ ∑ ω, μ.pmf ω :=
    Finset.sum_le_sum fun ω _ => by
      by_cases hE : E ω <;> simp [hE, le_rfl, μ.nonneg ω]
  calc
    μ.prob E = ∑ ω, if E ω then μ.pmf ω else 0 := rfl
    _ ≤ ∑ ω, μ.pmf ω := hle
    _ = 1 := μ.sum_one

def Subevent (E F : Ω → Prop) : Prop :=
  ∀ ω, E ω → F ω

infixl:50 " ⊆ₑ " => Subevent

theorem prob_mono (μ : FinDist Ω) {E F : Ω → Prop} [DecidablePred E] [DecidablePred F]
    (h : E ⊆ₑ F) : μ.prob E ≤ μ.prob F := by
  unfold Subevent at h
  unfold prob
  refine Finset.sum_le_sum fun ω _ => ?_
  by_cases hE : E ω
  · by_cases hF : F ω
    · simp [hE, hF]
    · exfalso
      exact hF (h ω hE)
  · by_cases hF : F ω
    · simp [hE, hF, μ.nonneg ω]
    · simp [hE, hF, le_rfl]

def uniform [Nonempty Ω] : FinDist Ω where
  pmf := fun _ => (Fintype.card Ω : ℝ)⁻¹
  nonneg := fun _ => inv_nonneg.mpr (Nat.cast_nonneg _)
  sum_one := by
    have hcard : 0 < (Fintype.card Ω : ℕ) := Fintype.card_pos
    simp only [Finset.sum_const, nsmul_eq_mul]
    field_simp [Nat.cast_ne_zero.mpr hcard.ne']

/-- Distribution supported on a finite finset `s` (weights zero off support). -/
noncomputable def ofFinset (s : Finset Ω) (w : Ω → ℝ)
    (hpos : ∀ a ∈ s, 0 ≤ w a) (hsum : ∑ a in s, w a = 1) : FinDist Ω where
  pmf a := if a ∈ s then w a else 0
  nonneg a := by
    by_cases ha : a ∈ s <;> simp [ha, hpos]
  sum_one := by
    have hsum' : ∑ a, (if a ∈ s then w a else 0) = ∑ a in s, w a := by
      rw [← Finset.sum_filter (s := Finset.univ) (p := fun a => a ∈ s) (f := w)]
      congr 1
      simp [Finset.inter_univ, Finset.filter_eq']
    simpa [hsum'] using hsum

end FinDist

structure FinMeasureSpace (Ω : Type*) [Fintype Ω] [DecidableEq Ω] where
  μ : FinDist Ω

namespace FinMeasureSpace

variable {Ω : Type*} [Fintype Ω] [DecidableEq Ω]

noncomputable def measure (M : FinMeasureSpace Ω) (E : Ω → Prop) [DecidablePred E] : ℝ :=
  M.μ.prob E

theorem measure_mono (M : FinMeasureSpace Ω) {E F : Ω → Prop}
    [DecidablePred E] [DecidablePred F] (h : E ⊆ₑ F) :
    measure M E ≤ measure M F :=
  FinDist.prob_mono M.μ h

theorem measure_nonneg (M : FinMeasureSpace Ω) (E : Ω → Prop) [DecidablePred E] :
    0 ≤ measure M E :=
  FinDist.prob_nonneg M.μ E

end FinMeasureSpace

/-- Decidable predicate = **measurable event** in this finite development. -/
abbrev MeasurableEvent (Ω : Type*) (E : Ω → Prop) :=
  DecidablePred E

structure CoupledExperiment (Ω : Type*) [Fintype Ω] [DecidableEq Ω] where
  space : FinMeasureSpace Ω
  eufWin : Ω → Prop
  mqWin : Ω → Prop
  euf_subset_mq : eufWin ⊆ₑ mqWin
  dec_eufWin : DecidablePred eufWin
  dec_mqWin : DecidablePred mqWin

namespace CoupledExperiment

variable {Ω : Type*} [Fintype Ω] [DecidableEq Ω]

noncomputable def eufMeasure (C : CoupledExperiment Ω) : ℝ :=
  @FinMeasureSpace.measure Ω _ _ C.space C.eufWin C.dec_eufWin

noncomputable def mqMeasure (C : CoupledExperiment Ω) : ℝ :=
  @FinMeasureSpace.measure Ω _ _ C.space C.mqWin C.dec_mqWin

theorem eufMeasure_le_mqMeasure (C : CoupledExperiment Ω) :
    C.eufMeasure ≤ C.mqMeasure :=
  @FinMeasureSpace.measure_mono Ω _ _ C.space C.eufWin C.mqWin C.dec_eufWin C.dec_mqWin C.euf_subset_mq

noncomputable def advantageGap (C : CoupledExperiment Ω) : ℝ :=
  C.mqMeasure - C.eufMeasure

theorem advantageGap_nonneg (C : CoupledExperiment Ω) : 0 ≤ C.advantageGap := by
  unfold advantageGap
  linarith [C.eufMeasure_le_mqMeasure]

end CoupledExperiment

end
