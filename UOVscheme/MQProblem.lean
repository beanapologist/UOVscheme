/-
  MQProblem.lean — The Multivariate Quadratic (MQ) problem.

  The MQ problem: given a system of o quadratic polynomials in n = o+v
  unknowns over 𝔽_q, find a common root.

  Two facts matter for UOV security:

    1. (Theorem) Worst-case MQ is NP-complete.
       Solving an arbitrary system of quadratic equations over a finite field
       is NP-hard. This is a known result and not proved here; we cite it.

    2. (Assumption) Average-case MQ is computationally hard.
       No PPT algorithm inverts a *random* quadratic map with non-negligible
       probability. This is unproven — it is the foundational assumption
       that underlies UOV and most multivariate cryptography.

  We state (2) as an axiom.  This is honest: it cannot be derived from
  P ≠ NP (which is worst-case), from analytic structure, or from any
  current mathematics.
-/

import UOVscheme.SecurityModel
import UOVscheme.CentralMap

variable {q o v : ℕ}

-- ════════════════════════════════════════════════════════════════
-- Adversary type
-- ════════════════════════════════════════════════════════════════

/-- A **cryptographic adversary** against the MQ inversion problem.

    The adversary receives a multivariate quadratic map P : 𝔽_q^(o+v) → 𝔽_q^o
    (as a black-box evaluation function) and must output an inverter: a
    function that, given any target y ∈ 𝔽_q^o, produces a preimage σ with
    P(σ) = y.

    We use `PPT` as the efficiency wrapper; without it this would be any
    function, which is trivially satisfiable by exhaustive search. -/
def MQAdversary (q o v : ℕ) :=
  PPT
    ((Fin (o + v) → ZMod q) → Fin o → ZMod q)   -- the public map P
    ((Fin o → ZMod q) → Fin (o + v) → ZMod q)   -- claimed inverter

namespace MQAdversary

/-- Run the adversary on a public map, obtaining an inverter. -/
def runOn (A : MQAdversary q o v)
    (P : (Fin (o + v) → ZMod q) → Fin o → ZMod q) :
    (Fin o → ZMod q) → Fin (o + v) → ZMod q :=
  PPT.run A P

end MQAdversary

-- ════════════════════════════════════════════════════════════════
-- Advantage and hardness
-- ════════════════════════════════════════════════════════════════

/-- The **advantage** of adversary A at the MQ problem.

    Formally: the probability that A(P)(y) is a preimage of y, where P is
    a random UOV-structured quadratic map and y is a random target.

    Axiomatized because formalizing "random quadratic map" requires a
    probability distribution over the key space, which is outside the
    scope of this file. -/
axiom MQ.advantage (A : MQAdversary q o v) : ℕ → ℝ

/-- **MQ Hardness Assumption (average-case).**

    For any PPT adversary A and any polynomial c, eventually the probability
    that A successfully inverts a random MQ instance is at most n^(−c).

    This is the central unproved assumption in multivariate cryptography.

    Supporting evidence (not proofs):
    - No polynomial-time algorithm is known for average-case MQ.
    - Exhaustive search requires ~q^v operations; for q=2, v=64 this is 2^64.
    - The best known algebraic attacks (Gröbner bases, XL) are exponential
      in the ratio o/v for random systems.
    - Decades of cryptanalysis have not broken the assumption for good parameters.

    Contra-evidence that it cannot be *derived*:
    - P ≠ NP (if true) implies worst-case hardness, not average-case.
    - Average-case reductions from worst-case MQ are unknown.
    - The resolvent degree of a generic quadratic system is ≥ 2, placing it
      above the floor where analytic linearization techniques (log, Fourier,
      Cauchy) have grip. -/
axiom MQ.hard [Fact (Nat.Prime q)] (A : MQAdversary q o v) :
    Negligible (MQ.advantage A)

-- ════════════════════════════════════════════════════════════════
-- Worst-case NP-hardness (cited, not proved)
-- ════════════════════════════════════════════════════════════════

/-- **MQ is NP-complete (worst-case).**

    Determining whether a system of quadratic equations over 𝔽_2 has a
    solution is NP-complete (Garey & Johnson 1979; also follows from
    a reduction from 3-SAT).

    We state this as an axiom here to document the fact; a full proof
    would require formalizing NP-completeness, which is a separate project. -/
axiom MQ.NP_hard : True
-- Replace with: ∀ (inst : MQInstance), MQDecide inst ≤_p SAT
-- once NP-completeness infrastructure is available in Mathlib.
