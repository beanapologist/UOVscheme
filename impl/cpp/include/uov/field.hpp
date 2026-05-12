#pragma once
/**
 * field.hpp — GF(q) arithmetic over a prime field (runtime q).
 *
 * All elements are represented as int in [0, q).
 * Matrices are row-major: std::vector<std::vector<int>>.
 */

#include <cassert>
#include <optional>
#include <random>
#include <stdexcept>
#include <vector>

namespace uov {

using Vec = std::vector<int>;
using Mat = std::vector<Vec>;

// ─────────────────────────────────────────────────────────────────────────────
// Scalar operations
// ─────────────────────────────────────────────────────────────────────────────

inline int mod(long long a, int q) {
    return static_cast<int>(((a % q) + q) % q);
}

inline int gf_add(int a, int b, int q) { return (a + b) % q; }
inline int gf_mul(int a, int b, int q) { return static_cast<int>((long long)a * b % q); }

inline int gf_inv(int a, int q) {
    assert(a % q != 0 && "zero has no inverse");
    // Extended Euclidean algorithm
    long long old_r = a, r = q;
    long long old_s = 1, s = 0;
    while (r != 0) {
        long long quot = old_r / r;
        long long tmp = r;  r = old_r - quot * r;  old_r = tmp;
        tmp = s;  s = old_s - quot * s;  old_s = tmp;
    }
    return static_cast<int>(((old_s % q) + q) % q);
}

// ─────────────────────────────────────────────────────────────────────────────
// Vector operations
// ─────────────────────────────────────────────────────────────────────────────

inline int dot(const Vec& u, const Vec& v, int q) {
    long long acc = 0;
    for (std::size_t i = 0; i < u.size(); ++i)
        acc += (long long)u[i] * v[i];
    return static_cast<int>(acc % q);
}

inline Vec vec_add(const Vec& u, const Vec& v, int q) {
    Vec w(u.size());
    for (std::size_t i = 0; i < u.size(); ++i)
        w[i] = (u[i] + v[i]) % q;
    return w;
}

inline Vec vec_sub(const Vec& u, const Vec& v, int q) {
    Vec w(u.size());
    for (std::size_t i = 0; i < u.size(); ++i)
        w[i] = mod(u[i] - v[i], q);
    return w;
}

// ─────────────────────────────────────────────────────────────────────────────
// Matrix-vector product
// ─────────────────────────────────────────────────────────────────────────────

inline Vec mat_mul_vec(const Mat& M, const Vec& v, int q) {
    Vec out(M.size());
    for (std::size_t i = 0; i < M.size(); ++i)
        out[i] = dot(M[i], v, q);
    return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// Gaussian elimination: solve M·x = b over GF(q)
// Returns nullopt if M is singular.
// ─────────────────────────────────────────────────────────────────────────────

inline std::optional<Vec> gauss_solve(Mat M, Vec b, int q) {
    int n = static_cast<int>(b.size());
    // Build augmented matrix [M | b]
    for (int i = 0; i < n; ++i)
        M[i].push_back(b[i]);

    for (int col = 0; col < n; ++col) {
        // Find pivot
        int pivot = -1;
        for (int row = col; row < n; ++row) {
            if (M[row][col] % q != 0) { pivot = row; break; }
        }
        if (pivot == -1) return std::nullopt;
        std::swap(M[col], M[pivot]);

        int inv_p = gf_inv(M[col][col], q);
        for (int j = col; j <= n; ++j)
            M[col][j] = gf_mul(M[col][j], inv_p, q);

        for (int row = 0; row < n; ++row) {
            if (row == col || M[row][col] == 0) continue;
            int factor = M[row][col];
            for (int j = col; j <= n; ++j)
                M[row][j] = mod(M[row][j] - gf_mul(factor, M[col][j], q), q);
        }
    }

    Vec x(n);
    for (int i = 0; i < n; ++i) x[i] = M[i][n];
    return x;
}

// ─────────────────────────────────────────────────────────────────────────────
// Matrix inverse over GF(q)
// Returns nullopt if singular.
// ─────────────────────────────────────────────────────────────────────────────

inline std::optional<Mat> gf_matinv(Mat M, int q) {
    int n = static_cast<int>(M.size());
    // Augment with identity
    Mat aug(n, Vec(2 * n, 0));
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) aug[i][j] = M[i][j];
        aug[i][n + i] = 1;
    }

    for (int col = 0; col < n; ++col) {
        int pivot = -1;
        for (int row = col; row < n; ++row) {
            if (aug[row][col] % q != 0) { pivot = row; break; }
        }
        if (pivot == -1) return std::nullopt;
        std::swap(aug[col], aug[pivot]);

        int inv_p = gf_inv(aug[col][col], q);
        for (int j = 0; j < 2 * n; ++j)
            aug[col][j] = gf_mul(aug[col][j], inv_p, q);

        for (int row = 0; row < n; ++row) {
            if (row == col || aug[row][col] == 0) continue;
            int factor = aug[row][col];
            for (int j = 0; j < 2 * n; ++j)
                aug[row][j] = mod(aug[row][j] - gf_mul(factor, aug[col][j], q), q);
        }
    }

    Mat inv(n, Vec(n));
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            inv[i][j] = aug[i][n + j];
    return inv;
}

// ─────────────────────────────────────────────────────────────────────────────
// Random helpers
// ─────────────────────────────────────────────────────────────────────────────

template <typename RNG>
Vec random_vec(int n, int q, RNG& rng) {
    std::uniform_int_distribution<int> dist(0, q - 1);
    Vec v(n);
    for (auto& x : v) x = dist(rng);
    return v;
}

template <typename RNG>
Mat random_mat(int rows, int cols, int q, RNG& rng) {
    Mat M(rows);
    for (auto& row : M) row = random_vec(cols, q, rng);
    return M;
}

template <typename RNG>
Mat random_invertible(int n, int q, RNG& rng) {
    while (true) {
        Mat M = random_mat(n, n, q, rng);
        if (gf_matinv(M, q).has_value()) return M;
    }
}

} // namespace uov
