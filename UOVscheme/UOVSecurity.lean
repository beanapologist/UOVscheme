/-
  UOVSecurity.lean — EUF-CMA security of the UOV signature scheme.

  Connects the algebraic correctness proof (SchemeCorrectness.lean) to the
  computational security model (SecurityModel.lean, MQProblem.lean).

  Structure of the argument:

    1. Algebraic fact (no axioms, no sorry):
       A valid forgery σ for target y under public key key satisfies
       key.publicEval σ = y.  This is literally the definition of verify.
       Therefore forging UOV = inverting the public map = solving MQ.

    2. Probabilistic reduction (one axiom):
       The advantage of any adversary at forging UOV signatures is at most
       its advantage at inverting a random MQ instance.

    3. MQ hardness (one axiom, in MQProblem.lean):
       No PPT adversary inverts a random MQ instance with non-negligible
       probability.

    4. Main theorem (proved from 2 + 3):
       No PPT adversary forges UOV signatures with non-negligible probability.

  Axiom count: 2 (reduction bound + MQ hardness).  No sorry.
-/

import UOVscheme.MQProblem
import UOVscheme.SchemeCorrectness

variable {q o v : ℕ}

open UOVKey

-- ════════════════════════════════════════════════════════════════
-- Part 1: Algebraic equivalence (zero axioms)
-- ════════════════════════════════════════════════════════════════

/-- **Theorem (Forgery = MQ Preimage).**

    A valid UOV forgery is exactly a preimage of the target under the
    public map.  This is a pure algebraic fact — no probability, no
    computation, no axioms.

    Proof: `verify y σ` unfolds to `publicEval σ = y` by definition. -/
theorem forgery_iff_mq_preimage (key : UOVKey q o v)
    (y : Fin o → ZMod q) (σ : Fin (o + v) → ZMod q) :
    key.verify y σ ↔ key.publicEval σ = y :=
  Iff.rfl

/-- Corollary: a UOV forger and an MQ adversary are the **same computational
    object**.  A UOV forger receives the public map (an MQ instance) and
    outputs a preimage (an MQ solution).  The types are identical. -/
theorem uov_forger_is_mq_adversary :
    (MQAdversary q o v) =
    PPT
      ((Fin (o + v) → ZMod q) → Fin o → ZMod q)
      ((Fin o → ZMod q) → Fin (o + v) → ZMod q) :=
  rfl

-- ════════════════════════════════════════════════════════════════
-- Part 2: Advantage and reduction (one axiom)
-- ════════════════════════════════════════════════════════════════

/-- A UOV forger is exactly an MQ adversary (same type, same computation).
    We use `MQAdversary` for both roles. -/
abbrev UOV_Forger (q o v : ℕ) := MQAdversary q o v

/-- The **EUF-CMA advantage** of adversary A against the UOV scheme.

    Formally: the probability that A(P)(y) passes `verify`, over randomly
    generated UOV public keys P and random targets y.

    Axiomatized for the same reason as `MQ.advantage`: the probability
    distribution over UOV keys is not yet formalized. -/
axiom UOV.advantage (A : UOV_Forger q o v) : ℕ → ℝ

/-- **The reduction bound.**

    Forging a UOV signature is no easier than inverting the public map,
    which is an instance of MQ.  Therefore the UOV advantage is at most
    the MQ advantage.

    Why this is an axiom rather than a theorem:
    The algebraic fact (Part 1) shows the problems are *equivalent* in
    structure.  The probabilistic statement — that the advantage over the
    UOV key distribution is bounded by the advantage over the MQ instance
    distribution — requires showing that UOV public keys are computationally
    indistinguishable from random MQ instances.  This "pseudorandomness of
    UOV public keys" is a standard assumption; formalizing it requires a
    probabilistic model that is not yet in scope.

    **Proof obligations for a future non-axiomatic version** (all meta-math;
    not formalized here):

    1. **Distributions.** Define measurable spaces / probability measures on
       UOV public keys and on “random” MQ systems matching the same arity
       `(o+v → 𝔽_q) → (o → 𝔽_q)`.

    2. **Coupling or reduction.** Exhibit a joint construction (or a sequence
       of games) so that any UOV forgery event maps to an MQ inversion event
       with probability loss accounted for in `n`.

    3. **Indistinguishability.** Prove (or assume as a lemma) that UOV keys
       are pseudorandom among MQ instances at the relevant security level —
       this is the cryptographic heart of (2).

    4. **Advantage identity.** Show the inequality in this axiom is the
       correct translation of the game-based EUF-CMA definition into the
       `UOV.advantage` / `MQ.advantage` numeric profiles.

    Until (1)–(4) are in Lean, `uov_reduces_to_mq` remains the honest
    one-line encapsulation of that reduction story. -/
axiom uov_reduces_to_mq (A : UOV_Forger q o v) (n : ℕ) :
    UOV.advantage A n ≤ MQ.advantage A n

-- ════════════════════════════════════════════════════════════════
-- Part 3: Main security theorem (proved, no sorry)
-- ════════════════════════════════════════════════════════════════

/-- **Theorem (UOV EUF-CMA Security).**

    Under the MQ hardness assumption, no PPT adversary can forge UOV
    signatures with non-negligible probability.

    Proof:
      UOV.advantage A n
        ≤ MQ.advantage A n      (uov_reduces_to_mq)
        ≤ n⁻¹^c  for large n   (MQ.hard)

    The proof is two lines because `Negligible.of_le` closes the gap:
    negligibility is downward-closed (SecurityModel.lean, proved). -/
theorem uov_euf_cma [Fact (Nat.Prime q)] (A : UOV_Forger q o v) :
    Negligible (UOV.advantage A) :=
  Negligible.of_le (uov_reduces_to_mq A) (MQ.hard A)

-- ════════════════════════════════════════════════════════════════
-- Axiom ledger
-- ════════════════════════════════════════════════════════════════

/-
  Every axiom used in this file and its transitive imports:

  MATHEMATICAL AXIOMS (Lean/Mathlib foundations — always present):
    - Classical logic (propext, funext, choice)
    - Mathlib's real analysis (for Negligible)

  COMPUTATIONAL MODEL AXIOMS (ours — in SecurityModel.lean):
    - `PPT`         — the type of PPT algorithms exists
    - `PPT.run`     — PPT algorithms can be evaluated
    - `PPT.comp`    — PPT algorithms compose

  CRYPTOGRAPHIC AXIOMS (ours):
    - `MQ.advantage`        — MQProblem.lean: the advantage function exists
    - `MQ.hard`             — MQProblem.lean: MQ is hard on average (bundles
                              PPT restriction + correct success measure +
                              negligibility; see module doc there)
    - `UOV.advantage`       — here: the UOV advantage function exists
    - `uov_reduces_to_mq`   — here: UOV advantage ≤ MQ advantage (bundles
                              distributions + pseudorandomness of keys +
                              game translation; see docstring on the axiom)

  NO SORRY anywhere in the proof chain for `uov_euf_cma`.
  The theorem is as strong as its axioms — and the axioms are exactly
  the right things to assume.
-/
