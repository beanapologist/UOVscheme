#pragma once
/**
 * scheme.hpp — UOVKey: public-key evaluation, signing, and verification.
 *
 * Mirrors SchemeCorrectness.lean:
 *   publicEval(σ) = F(oilPart(T·σ), vinPart(T·σ))
 *   sign(oil, vin) = T⁻¹·(oil ++ vin)
 *   verify(y, σ)   = publicEval(σ) == y
 */

#include "central_map.hpp"

namespace uov {

struct UOVKey {
    int q, o, v;
    CentralMap F;
    Mat T;      // (o+v)×(o+v) invertible
    Mat T_inv;  // precomputed inverse

    Vec public_eval(const Vec& sigma) const {
        Vec x = mat_mul_vec(T, sigma, q);
        Vec oil(x.begin(), x.begin() + o);
        Vec vin(x.begin() + o, x.end());
        return F.eval(oil, vin);
    }

    template <typename RNG>
    std::optional<Vec> sign(const Vec& y, RNG& rng, int max_attempts = 1000) const {
        std::uniform_int_distribution<int> dist(0, q - 1);
        for (int attempt = 0; attempt < max_attempts; ++attempt) {
            Vec vin(v);
            for (auto& x : vin) x = dist(rng);

            Mat M = F.lin_matrix(vin);
            Vec b = F.vin_const_vec(vin);

            Vec rhs(o);
            for (int i = 0; i < o; ++i)
                rhs[i] = mod(y[i] - b[i], q);

            auto oil_opt = gauss_solve(M, rhs, q);
            if (!oil_opt) continue;

            Vec combined;
            combined.insert(combined.end(), oil_opt->begin(), oil_opt->end());
            combined.insert(combined.end(), vin.begin(), vin.end());

            return mat_mul_vec(T_inv, combined, q);
        }
        return std::nullopt;
    }

    bool verify(const Vec& y, const Vec& sigma) const {
        return public_eval(sigma) == y;
    }
};

} // namespace uov
