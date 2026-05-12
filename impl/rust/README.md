# UOV — Rust Implementation (planned)

Will mirror `impl/python/` as a Cargo crate:

```
uov/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── field.rs        # GF(q) arithmetic
    ├── central_map.rs  # CentralMapComp, CentralMap
    ├── scheme.rs       # UOVKey, sign, verify
    └── keygen.rs       # random key generation
```

Planned dependencies: `rand`, `ndarray` (or plain `Vec<Vec<u64>>`).

The Rust implementation will expose a clean public API and be no_std compatible for embedded targets.
