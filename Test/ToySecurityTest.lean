import UOVscheme.ToyCryptoGame

open ToyCryptoGame EUFProb MQProb

example : eufAdvantage_losing 0 = 0 := rfl

example : mqAdvantage_winning 3 = 1 / 2 := mqAdvantage_winning 3

example : coupling_winning 10 := coupling_winning 10

example : toy_euf_cma_via_reduction := toy_euf_cma_via_reduction

example : toy_uov_euf_cma_mqLosing := toy_uov_euf_cma_mqLosing

example : Negligible (fun n => EUFProb.eufAdvantage eufWinning n) → False := by
  intro h
  have := h 1
  have hhalf : EUFProb.eufAdvantage eufWinning 1 = 1 / 2 := eufAdvantage_winning 1
  have hone : (1 : ℝ)⁻¹ ^ 1 ≤ 1 / 2 := by
    simpa [hhalf] using this
  norm_num at hone
