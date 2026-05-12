# UOV — C++ Implementation (planned)

Will mirror `impl/python/` with the same module breakdown:

| File | Mirrors |
|---|---|
| `field.hpp` / `field.cpp` | `uov/field.py` |
| `central_map.hpp` / `central_map.cpp` | `uov/central_map.py` |
| `scheme.hpp` / `scheme.cpp` | `uov/scheme.py` |
| `keygen.hpp` / `keygen.cpp` | `uov/keygen.py` |
| `main.cpp` | `examples/demo.py` |

Planned dependencies: none beyond the C++17 standard library (field arithmetic is self-contained).

Build system: CMake.
