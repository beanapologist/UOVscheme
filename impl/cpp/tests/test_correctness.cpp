/**
 * test_correctness.cpp — correctness tests for the UOV C++ implementation.
 *
 * Build with CMake and run via ctest.  Each TEST_* function asserts its
 * invariants; any failure causes a non-zero exit code detected by ctest.
 */

#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include "uov/keygen.hpp"

static int passed = 0, failed = 0;

#define RUN_TEST(name) \
    do { \
        std::cout << "  " << #name << " ... "; std::cout.flush(); \
        try { name(); std::cout << "PASS\n"; ++passed; } \
        catch (std::exception& e) { std::cout << "FAIL: " << e.what() << "\n"; ++failed; } \
        catch (...) { std::cout << "FAIL (unknown)\n"; ++failed; } \
    } while(0)

static void CHECK(bool cond, const char* msg) {
    if (!cond) throw std::runtime_error(msg);
}

// ── eval_affine ───────────────────────────────────────────────────────────────

void test_eval_affine_exhaustive() {
    // Exhaustive over GF(7)^2 × GF(7)^2
    const int q = 7, o = 2, v = 2;
    std::mt19937 rng(0);
    auto comp = uov::CentralMapComp::random(q, o, v, rng);
    for (int o0 = 0; o0 < q; ++o0)
    for (int o1 = 0; o1 < q; ++o1)
    for (int v0 = 0; v0 < q; ++v0)
    for (int v1 = 0; v1 < q; ++v1) {
        uov::Vec oil{o0, o1}, vin{v0, v1};
        int lhs = comp.eval(oil, vin);
        auto lc = comp.lin_coeff(vin);
        int rhs = (uov::dot(oil, lc, q) + comp.vin_const(vin)) % q;
        CHECK(lhs == rhs, "eval_affine failed");
    }
}

void test_eval_affine_random() {
    const int q = 31, o = 4, v = 8;
    std::mt19937 rng(7);
    auto comp = uov::CentralMapComp::random(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    for (int t = 0; t < 200; ++t) {
        uov::Vec oil(o), vin(v);
        for (auto& x : oil) x = dist(rng);
        for (auto& x : vin) x = dist(rng);
        int lhs = comp.eval(oil, vin);
        auto lc = comp.lin_coeff(vin);
        int rhs = (uov::dot(oil, lc, q) + comp.vin_const(vin)) % q;
        CHECK(lhs == rhs, "eval_affine random failed");
    }
}

void test_eval_zero_oil() {
    const int q = 13, o = 3, v = 5;
    std::mt19937 rng(1);
    auto comp = uov::CentralMapComp::random(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec zero_oil(o, 0);
    for (int t = 0; t < 20; ++t) {
        uov::Vec vin(v);
        for (auto& x : vin) x = dist(rng);
        CHECK(comp.eval(zero_oil, vin) == comp.vin_const(vin), "eval_zero_oil failed");
    }
}

void test_eval_zero_vin() {
    const int q = 13, o = 3, v = 5;
    std::mt19937 rng(2);
    auto comp = uov::CentralMapComp::random(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec zero_vin(v, 0);
    for (int t = 0; t < 20; ++t) {
        uov::Vec oil(o);
        for (auto& x : oil) x = dist(rng);
        int expected = (uov::dot(comp.c, oil, q) + comp.e) % q;
        CHECK(comp.eval(oil, zero_vin) == expected, "eval_zero_vin failed");
    }
}

// ── eval_as_linSystem ─────────────────────────────────────────────────────────

void test_eval_as_lin_system() {
    const int q = 31, o = 4, v = 6;
    std::mt19937 rng(10);
    auto F = uov::CentralMap::random(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    for (int t = 0; t < 50; ++t) {
        uov::Vec oil(o), vin(v);
        for (auto& x : oil) x = dist(rng);
        for (auto& x : vin) x = dist(rng);
        auto lhs = F.eval(oil, vin);
        auto M = F.lin_matrix(vin);
        auto b = F.vin_const_vec(vin);
        auto Moil = uov::mat_mul_vec(M, oil, q);
        for (int k = 0; k < o; ++k)
            CHECK(lhs[k] == (Moil[k] + b[k]) % q, "eval_as_lin_system failed");
    }
}

// ── Gaussian elimination ──────────────────────────────────────────────────────

void test_gauss_identity() {
    const int q = 17, n = 4;
    uov::Mat I(n, uov::Vec(n, 0));
    for (int i = 0; i < n; ++i) I[i][i] = 1;
    uov::Vec b{3, 1, 4, 1};
    auto x = uov::gauss_solve(I, b, q);
    CHECK(x.has_value(), "gauss_solve failed on identity");
    CHECK(*x == b, "gauss_solve identity wrong result");
}

void test_gauss_random() {
    const int q = 31;
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(0, q - 1);
    for (int t = 0; t < 50; ++t) {
        int n = 2 + (rng() % 5);
        std::optional<uov::Mat> inv_opt;
        uov::Mat M;
        for (int attempt = 0; attempt < 20; ++attempt) {
            M = uov::random_mat(n, n, q, rng);
            inv_opt = uov::gf_matinv(M, q);
            if (inv_opt) break;
        }
        if (!inv_opt) continue;
        uov::Vec b(n);
        for (auto& x : b) x = dist(rng);
        auto x = uov::gauss_solve(M, b, q);
        CHECK(x.has_value(), "gauss_solve returned nullopt for invertible M");
        auto check = uov::mat_mul_vec(M, *x, q);
        CHECK(check == b, "gauss_solve solution wrong");
    }
}

void test_gauss_singular() {
    const int q = 7;
    uov::Mat M{{1, 2}, {2, 4}};  // rank 1
    auto x = uov::gauss_solve(M, {1, 2}, q);
    CHECK(!x.has_value(), "gauss_solve should return nullopt for singular M");
}

// ── UOV correctness ───────────────────────────────────────────────────────────

void test_roundtrip_many() {
    const int q = 31, o = 4, v = 8;
    for (int i = 0; i < 50; ++i) {
        std::mt19937 krng(i);
        auto key = uov::keygen(q, o, v, krng);
        std::uniform_int_distribution<int> dist(0, q - 1);
        std::mt19937 srng(i + 1000);
        uov::Vec msg(o);
        for (auto& x : msg) x = dist(srng);
        auto sig = key.sign(msg, srng);
        CHECK(sig.has_value(), "sign returned nullopt");
        CHECK(key.verify(msg, *sig), "verify failed after sign");
    }
}

void test_wrong_message_rejected() {
    const int q = 31, o = 4, v = 8;
    std::mt19937 rng(7);
    auto key = uov::keygen(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec msg(o);
    for (auto& x : msg) x = dist(rng);
    auto sig = key.sign(msg, rng);
    uov::Vec wrong = msg;
    for (auto& x : wrong) x = (x + 1) % q;
    CHECK(!key.verify(wrong, *sig), "wrong message should be rejected");
}

void test_forgery_rejected() {
    const int q = 31, o = 4, v = 8;
    std::mt19937 rng(77);
    auto key = uov::keygen(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec msg(o);
    for (auto& x : msg) x = dist(rng);
    int accepted = 0;
    for (int i = 0; i < 1000; ++i) {
        uov::Vec forgery(o + v);
        for (auto& x : forgery) x = dist(rng);
        if (key.verify(msg, forgery)) ++accepted;
    }
    CHECK(accepted == 0, "random forgery was accepted");
}

void test_cross_key_rejection() {
    const int q = 31, o = 4, v = 8;
    std::mt19937 rng1(10), rng2(11);
    auto key1 = uov::keygen(q, o, v, rng1);
    auto key2 = uov::keygen(q, o, v, rng2);
    std::mt19937 srng(55);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec msg(o);
    for (auto& x : msg) x = dist(srng);
    auto sig = key1.sign(msg, srng);
    CHECK(key1.verify(msg, *sig), "key1 verify failed");
    CHECK(!key2.verify(msg, *sig), "key2 should reject key1's signature");
}

void test_public_eval_consistent() {
    const int q = 31, o = 4, v = 8;
    std::mt19937 rng(1234);
    auto key = uov::keygen(q, o, v, rng);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec oil(o), vin(v);
    for (auto& x : oil) x = dist(rng);
    for (auto& x : vin) x = dist(rng);
    auto y = key.F.eval(oil, vin);
    uov::Vec combined(oil);
    combined.insert(combined.end(), vin.begin(), vin.end());
    auto sigma = uov::mat_mul_vec(key.T_inv, combined, q);
    CHECK(key.public_eval(sigma) == y, "public_eval inconsistent");
    CHECK(key.verify(y, sigma), "verify inconsistent with public_eval");
}

// ─────────────────────────────────────────────────────────────────────────────

int main() {
    std::cout << "UOV C++ correctness tests\n";

    RUN_TEST(test_eval_affine_exhaustive);
    RUN_TEST(test_eval_affine_random);
    RUN_TEST(test_eval_zero_oil);
    RUN_TEST(test_eval_zero_vin);
    RUN_TEST(test_eval_as_lin_system);
    RUN_TEST(test_gauss_identity);
    RUN_TEST(test_gauss_random);
    RUN_TEST(test_gauss_singular);
    RUN_TEST(test_roundtrip_many);
    RUN_TEST(test_wrong_message_rejected);
    RUN_TEST(test_forgery_rejected);
    RUN_TEST(test_cross_key_rejection);
    RUN_TEST(test_public_eval_consistent);

    std::cout << "\n" << passed << " passed, " << failed << " failed\n";
    return failed == 0 ? 0 : 1;
}
