/-
  CertificateTest.lean — sanity check that `Certificate` compiles and
  `StateCertificate.valid_of_sign` applies on the same toy key as `SchemeTest`.
-/

import UOVscheme.Certificate
import UOVscheme.SchemeCorrectness
import Mathlib.Data.Matrix.Notation

open Matrix UOVKey

instance fact_prime_7 : Fact (Nat.Prime 7) := ⟨by native_decide⟩

private def comp0 : CentralMapComp 7 2 2 := {
  A := !![1, 0; 0, 1],
  B := !![1, 0; 0, 0],
  c := ![1, 0],
  d := ![0, 0],
  e := 2
}

private def comp1 : CentralMapComp 7 2 2 := {
  A := !![0, 1; 1, 0],
  B := !![0, 0; 0, 1],
  c := ![0, 1],
  d := ![1, 0],
  e := 0
}

private def F : CentralMap 7 2 2 := { comps := ![comp0, comp1] }

private def oil : Fin 2 → ZMod 7 := ![3, 5]
private def vin : Fin 2 → ZMod 7 := ![1, 2]
private def y : Fin 2 → ZMod 7 := F.eval oil vin

private def T_id : Matrix (Fin 4) (Fin 4) (ZMod 7) := 1

private def key_id : UOVKey 7 2 2 := {
  F  := F,
  T  := T_id,
  hT := by native_decide
}

private noncomputable def cert : UOVKey.StateCertificate 7 2 2 :=
  UOVKey.StateCertificate.mk y (key_id.sign oil vin)

example : cert.isValid key_id := by
  exact UOVKey.StateCertificate.valid_of_sign key_id y oil vin rfl
