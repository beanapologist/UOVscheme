#pragma once
/**
 * keygen.hpp — Key generation for the UOV signature scheme.
 */

#include "scheme.hpp"

namespace uov {

template <typename RNG>
UOVKey keygen(int q, int o, int v, RNG& rng) {
    auto F = CentralMap::random(q, o, v, rng);
    auto T = random_invertible(o + v, q, rng);
    auto T_inv = *gf_matinv(T, q);
    return UOVKey{q, o, v, std::move(F), std::move(T), std::move(T_inv)};
}

} // namespace uov
