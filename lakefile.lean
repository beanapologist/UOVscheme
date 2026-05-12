import Lake
open Lake DSL

package UOVscheme where
  leanVersion := .v4_10_0

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.10.0"

lean_lib UOVscheme where
  globs := #[
    .subModules `OilVinegar,
    .subModules `DualityStructure,
    .subModules `BalanceHypothesis,
    .subModules `UOV,
    .subModules `CentralMap,
    .subModules `SchemeCorrectness,
    .subModules `SecurityModel,
    .subModules `MQProblem,
    .subModules `UOVSecurity
  ]
