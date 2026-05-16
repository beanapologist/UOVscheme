import UOVscheme.CryptoGame

open FinDist FinMeasureSpace

example : (FinDist.uniform (α := Fin 3)).prob (fun i => i = 0) ≤
    (FinDist.uniform (α := Fin 3)).prob (fun i => i ≤ 1) := by
  apply prob_mono
  intro ⟨i, hi⟩
  rcases i with 0 | 1 | 2
  · intro h; simp at h; simp [h]
  · intro h; simp at h; simp [h]
  · intro h; simp at h; simp [h]

example : 0 ≤ measure (⟨FinDist.uniform (α := Fin 3)⟩) (fun _ => True) :=
  measure_nonneg _ _
