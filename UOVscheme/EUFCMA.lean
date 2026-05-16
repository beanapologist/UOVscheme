/-
  EUFCMA.lean — Existential unforgeability under chosen-message attack (EUF-CMA),
  stated as explicit predicates before any probability / advantage axioms.

  This file is the **game layer**: what it means to win EUF-CMA or to invert MQ.
  The reduction `UOVSecurity.lean` shows (algebraically) that EUF wins imply MQ
  preimages; the inequality between *advantages* remains axiomatized until a
  measure-theoretic model exists.
-/

import UOVscheme.SchemeCorrectness
import UOVscheme.SecurityModel

variable {q o v : ℕ} [Fact (Nat.Prime q)]

-- ════════════════════════════════════════════════════════════════
-- Public map as an MQ instance
-- ════════════════════════════════════════════════════════════════

/-- A multivariate quadratic map in the MQ sense: one vector in, `o` components out. -/
abbrev PublicMap (q o v : ℕ) :=
  (Fin (o + v) → ZMod q) → Fin o → ZMod q

namespace PublicMap

/-- The public map induced by a UOV key (the object Bob uses in verification). -/
def ofKey (key : UOVKey q o v) : PublicMap q o v :=
  fun σ => key.publicEval σ

end PublicMap

-- ════════════════════════════════════════════════════════════════
-- MQ inversion (algebraic win condition)
-- ════════════════════════════════════════════════════════════════

namespace MQ

/-- **MQ win:** vector `σ` is a preimage of digest `y` under public map `P`. -/
def win (P : PublicMap q o v) (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) : Prop :=
  P σ = y

/-- Same condition, packaged as an inverter `inv` that maps target `y` to `σ`. -/
def winOf (P : PublicMap q o v) (inv : (Fin o → ZMod q) → Fin (o + v) → ZMod q)
    (y : Fin o → ZMod q) : Prop :=
  win P y (inv y)

theorem winOf_eq (P : PublicMap q o v) (inv : (Fin o → ZMod q) → Fin (o + v) → ZMod q)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    winOf P inv y ↔ win P y (inv y) :=
  Iff.rfl

end MQ

-- ════════════════════════════════════════════════════════════════
-- EUF-CMA experiment (digest-level, matching `verify` on `Fin o → ZMod q`)
-- ════════════════════════════════════════════════════════════════

namespace EUFCMA

/-- Digests `y` for which the signing oracle has returned a valid signature. -/
abbrev QueryLog (q o v : ℕ) := List (Fin o → ZMod q)

/-- The forgery digest `y*` is **fresh** if it was never queried. -/
def fresh (log : QueryLog q o v) (y : Fin o → ZMod q) : Prop :=
  ∀ z, z ∈ log → z ≠ y

/-- **EUF-CMA win** on a fixed key: valid signature on a fresh digest.

    This is the standard existential forgery predicate at the level of
    `SchemeCorrectness.verify` (equivalently `publicEval σ = y`). -/
def win (key : UOVKey q o v) (log : QueryLog q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) : Prop :=
  key.verify y σ ∧ fresh log y

-- ════════════════════════════════════════════════════════════════
-- Signing oracle (Alice / chosen-message phase)
-- ════════════════════════════════════════════════════════════════

/-- **Signing oracle** for the EUF-CMA game.

  Models Alice after key generation: she holds `key`, answers chosen digest
  queries with valid signatures, and records every queried `y` in `log`.

  A query supplies a witness `(oil, vin)` with `F(oil, vin) = y` — the trapdoor
  side of signing (vinegar + linear solve). The adversary only sees `(y, σ)`;
  the witness stays on the oracle side of the interface. -/
structure SigningOracle (q o v : ℕ) [Fact (Nat.Prime q)] where
  key : UOVKey q o v
  /-- Digests `y` for which the oracle has already returned a signature. -/
  log : QueryLog q o v

namespace SigningOracle

/-- Fresh oracle at the start of the EUF-CMA game (no queries yet). -/
def init (key : UOVKey q o v) : SigningOracle q o v :=
  { key := key, log := [] }

/-- Whether digest `y` was already sent to the oracle. -/
def wasQueried (O : SigningOracle q o v) (y : Fin o → ZMod q) : Prop :=
  y ∈ O.log

/-- `y` is admissible as a forgery target after interacting with `O`. -/
def fresh (O : SigningOracle q o v) (y : Fin o → ZMod q) : Prop :=
  EUFCMA.fresh O.log y

/-- **Chosen-message query:** sign digest `y`, extend the log, return `σ`.

  Returns the updated oracle (new state) and the signature vector. -/
noncomputable def query (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q)
    (h_solve : O.key.F.eval oil vin = y) :
    SigningOracle q o v × (Fin (o + v) → ZMod q) :=
  (⟨O.key, y :: O.log⟩, O.key.sign oil vin)

/-- Signature returned by `query` always verifies under the oracle key. -/
theorem query_spec (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q)
    (h_solve : O.key.F.eval oil vin = y) :
    let ⟨_, σ⟩ := O.query y oil vin h_solve
    O.key.verify y σ :=
    UOVKey.sign_then_verify O.key y oil vin h_solve

/-- The queried digest is recorded in the log. -/
theorem query_mem_log (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q)
    (h_solve : O.key.F.eval oil vin = y) :
    let ⟨O', _⟩ := O.query y oil vin h_solve
    y ∈ O'.log := by
  simp only [query, List.mem_cons_self]

/-- Earlier queries remain in the log after a new query. -/
theorem query_log_mono (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (oil : Fin o → ZMod q) (vin : Fin v → ZMod q) (h_solve : O.key.F.eval oil vin = y)
    {z : Fin o → ZMod q} (hz : z ∈ O.log) :
    let ⟨O', _⟩ := O.query y oil vin h_solve
    z ∈ O'.log := by
  simp only [query, List.mem_cons]
  exact Or.inr hz

/-- EUF-CMA win against oracle state `O` (Bob checks forgery; `y` must be fresh). -/
def adversaryWins (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (σ : Fin (o + v) → ZMod q) : Prop :=
  EUFCMA.win O.key O.log y σ

end SigningOracle

/-- Bundle the experiment parameters for readability. -/
structure Experiment (q o v : ℕ) [Fact (Nat.Prime q)] where
  key : UOVKey q o v
  log : QueryLog q o v
  /-- Forged digest `y*`. -/
  y : Fin o → ZMod q
  /-- Forged signature `σ*`. -/
  σ : Fin (o + v) → ZMod q

def Experiment.wins (e : Experiment q o v) : Prop :=
  win e.key e.log e.y e.σ

/-- Build an experiment record from a post-game oracle state and a forgery attempt. -/
def Experiment.ofOracle (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (σ : Fin (o + v) → ZMod q) : Experiment q o v :=
  { key := O.key, log := O.log, y := y, σ := σ }

def Experiment.winsOracle (O : SigningOracle q o v) (y : Fin o → ZMod q)
    (σ : Fin (o + v) → ZMod q) : Prop :=
  (ofOracle O y σ).wins

theorem SigningOracle.adversaryWins_iff_experiment (O : SigningOracle q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    SigningOracle.adversaryWins O y σ ↔ (Experiment.ofOracle O y σ).wins :=
  Iff.rfl

-- ════════════════════════════════════════════════════════════════
-- PPT adversary (Eve after the query phase)
-- ════════════════════════════════════════════════════════════════

/-- Adversary output: digest `y*` and signature `σ*`. -/
abbrev Forgery (q o v : ℕ) := (Fin o → ZMod q) × (Fin (o + v) → ZMod q)

/-- A **PPT EUF-CMA adversary**: reads the final oracle state, outputs a forgery `(y*, σ*)`. -/
abbrev EUFAdversary (q o v : ℕ) [Fact (Nat.Prime q)] :=
  PPT (SigningOracle q o v) (Forgery q o v)

namespace EUFAdversary

/-- Run the adversary on the post-query oracle; obtain claimed `(y*, σ*)`. -/
def forge (A : EUFAdversary q o v) (O : SigningOracle q o v) : Forgery q o v :=
  A.run O

/-- **Win event:** output verifies and `y*` was never queried. -/
def wins (A : EUFAdversary q o v) (O : SigningOracle q o v) : Prop :=
  let (y, σ) := A.forge O
  SigningOracle.adversaryWins O y σ

theorem wins_iff (A : EUFAdversary q o v) (O : SigningOracle q o v) :
    wins A O ↔
      let (y, σ) := A.forge O
      SigningOracle.adversaryWins O y σ :=
  Iff.rfl

end EUFAdversary

-- ════════════════════════════════════════════════════════════════
-- MQ adversary (black-box inverter)
-- ════════════════════════════════════════════════════════════════

/-- **PPT MQ adversary:** maps public map `P` to a candidate preimage function. -/
def MQAdversary (q o v : ℕ) :=
  PPT
    ((Fin (o + v) → ZMod q) → Fin o → ZMod q)
    ((Fin o → ZMod q) → Fin (o + v) → ZMod q)

namespace MQAdversary

def runOn (A : MQAdversary q o v)
    (P : (Fin (o + v) → ZMod q) → Fin o → ZMod q) (y : Fin o → ZMod q) :
    Fin (o + v) → ZMod q :=
  A.run P y

end MQAdversary

-- ════════════════════════════════════════════════════════════════
-- Algebraic lemmas (no axioms, no sorry)
-- ════════════════════════════════════════════════════════════════

/-- Verification success is exactly an MQ preimage under the key's public map. -/
theorem verify_iff_mq_win (key : UOVKey q o v) (y : Fin o → ZMod q)
    (σ : Fin (o + v) → ZMod q) :
    key.verify y σ ↔ MQ.win (PublicMap.ofKey key) y σ :=
  Iff.rfl

theorem EUFAdversary.wins_implies_mq (A : EUFAdversary q o v) (O : SigningOracle q o v)
    (h : EUFAdversary.wins A O) :
    MQ.win (PublicMap.ofKey O.key) (A.forge O).1 (A.forge O).2 := by
  unfold EUFAdversary.wins SigningOracle.adversaryWins at h
  exact (verify_iff_mq_win O.key _ _).mp h.1

theorem win_iff_mq_win (key : UOVKey q o v) (log : QueryLog q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    win key log y σ ↔ MQ.win (PublicMap.ofKey key) y σ ∧ fresh log y := by
  unfold win
  rw [verify_iff_mq_win]

/-- Any EUF-CMA win yields an MQ preimage (ignoring freshness). -/
theorem wins_implies_mq_preimage (e : Experiment q o v) (h : e.wins) :
    MQ.win (PublicMap.ofKey e.key) e.y e.σ :=
  (win_iff_mq_win e.key e.log e.y e.σ).mp h |>.left

/-- EUF-CMA win implies MQ win **and** the digest was not in the query log. -/
theorem wins_iff_mq_and_fresh (e : Experiment q o v) :
    e.wins ↔ MQ.win (PublicMap.ofKey e.key) e.y e.σ ∧ fresh e.log e.y :=
  win_iff_mq_win e.key e.log e.y e.σ

end EUFCMA
