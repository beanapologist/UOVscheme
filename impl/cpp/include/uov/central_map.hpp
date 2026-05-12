#pragma once
/**
 * central_map.hpp — CentralMapComp and CentralMap.
 *
 * Mirrors CentralMap.lean exactly:
 *   CentralMapComp: A (o×v), B (v×v), c (o), d (v), e (scalar)
 *   eval(oil, vin) = oil·(A·vin) + vin·(B·vin) + c·oil + d·vin + e
 */

#include "field.hpp"

namespace uov {

// ─────────────────────────────────────────────────────────────────────────────
// CentralMapComp
// ─────────────────────────────────────────────────────────────────────────────

struct CentralMapComp {
    int q, o, v;
    Mat A;  // o×v — oil-vinegar cross terms
    Mat B;  // v×v — vinegar-vinegar quadratic terms
    Vec c;  // length o — linear oil coefficients
    Vec d;  // length v — linear vinegar coefficients
    int e;  // constant term

    int eval(const Vec& oil, const Vec& vin) const {
        Vec Avin = mat_mul_vec(A, vin, q);
        Vec Bvin = mat_mul_vec(B, vin, q);
        long long result =
            dot(oil, Avin, q) +
            dot(vin, Bvin, q) +
            dot(c, oil, q) +
            dot(d, vin, q) +
            e;
        return static_cast<int>(result % q);
    }

    // A·vin + c  (the linear coefficient vector for fixed vin)
    Vec lin_coeff(const Vec& vin) const {
        Vec Avin = mat_mul_vec(A, vin, q);
        return vec_add(Avin, c, q);
    }

    // vin·B·vin + d·vin + e  (constant w.r.t. oil)
    int vin_const(const Vec& vin) const {
        Vec Bvin = mat_mul_vec(B, vin, q);
        long long result = dot(vin, Bvin, q) + dot(d, vin, q) + e;
        return static_cast<int>(result % q);
    }

    template <typename RNG>
    static CentralMapComp random(int q, int o, int v, RNG& rng) {
        std::uniform_int_distribution<int> dist(0, q - 1);
        return CentralMapComp{
            q, o, v,
            random_mat(o, v, q, rng),
            random_mat(v, v, q, rng),
            random_vec(o, q, rng),
            random_vec(v, q, rng),
            dist(rng),
        };
    }
};

// ─────────────────────────────────────────────────────────────────────────────
// CentralMap
// ─────────────────────────────────────────────────────────────────────────────

struct CentralMap {
    int q, o, v;
    std::vector<CentralMapComp> comps;  // length o

    Vec eval(const Vec& oil, const Vec& vin) const {
        Vec out(o);
        for (int k = 0; k < o; ++k)
            out[k] = comps[k].eval(oil, vin);
        return out;
    }

    // o×o matrix M(vin): row k = lin_coeff of comp k
    Mat lin_matrix(const Vec& vin) const {
        Mat M(o);
        for (int k = 0; k < o; ++k)
            M[k] = comps[k].lin_coeff(vin);
        return M;
    }

    // o-vector b(vin): entry k = vin_const of comp k
    Vec vin_const_vec(const Vec& vin) const {
        Vec b(o);
        for (int k = 0; k < o; ++k)
            b[k] = comps[k].vin_const(vin);
        return b;
    }

    template <typename RNG>
    static CentralMap random(int q, int o, int v, RNG& rng) {
        std::vector<CentralMapComp> cs;
        cs.reserve(o);
        for (int k = 0; k < o; ++k)
            cs.push_back(CentralMapComp::random(q, o, v, rng));
        return CentralMap{q, o, v, std::move(cs)};
    }
};

} // namespace uov
