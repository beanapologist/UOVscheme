/-
  Certificate.lean — State certificate bundle (digest + signature).

  A *certificate* in the SilentVerify / state-certificate sense is the pair `(y, σ)` together with
  public key material (the composed map `P = F ∘ T`, represented in Lean by
  `UOVKey` minus the computational distinction between public and secret —
  verification only uses `publicEval` / `verify`).

  This module packages the bookkeeping used in the Python JSON pipeline
  (`impl/python/uov/certificate.py`) at the proof level: validity is exactly
  `verify`, and validity follows from `SchemeCorrectness.sign_then_verify`.
-/

import UOVscheme.SchemeCorrectness

variable {q o v : ℕ} [Fact (Nat.Prime q)]

namespace UOVKey

/-- A state certificate: target digest `y` and candidate signature `σ`. -/
structure StateCertificate (q o v : ℕ) [Fact (Nat.Prime q)] where
  /-- Digest in `𝔽_q^o` (e.g. a hash output). -/
  y : Fin o → ZMod q
  /-- Signature vector in `𝔽_q^(o+v)`. -/
  σ : Fin (o + v) → ZMod q

namespace StateCertificate

/-- Certificate is *valid* under `key` iff UOV verification succeeds. -/
def isValid (c : StateCertificate q o v) (key : UOVKey q o v) : Prop :=
  key.verify c.y c.σ

theorem isValid_iff (c : StateCertificate q o v) (key : UOVKey q o v) :
    c.isValid key ↔ key.publicEval c.σ = c.y :=
  Iff.rfl

/-- Soundness direction: validity implies equality on the public map. -/
theorem valid_publicEval (c : StateCertificate q o v) (key : UOVKey q o v)
    (h : c.isValid key) : key.publicEval c.σ = c.y :=
  h

/-- **Issuance theorem**: if `oil` solves `F.eval oil vin = y`, the signed
    bundle is a valid certificate. -/
theorem valid_of_sign (key : UOVKey q o v) (y : Fin o → ZMod q)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q)
    (h_solve : key.F.eval oil vin = y) :
    (StateCertificate.mk y (key.sign oil vin)).isValid key :=
  sign_then_verify key y oil vin h_solve

end StateCertificate

end UOVKey
