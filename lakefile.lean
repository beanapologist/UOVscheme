import Lake
open Lake DSL

package UOVscheme where
  leanVersion := .v4_10_0

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.10.0"

lean_lib UOVscheme where
  globs := #[.subModules `UOVscheme]

lean_lib Test where
  globs := #[.subModules `Test]
