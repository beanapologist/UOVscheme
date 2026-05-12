/**
 * demo.cpp — Alice signs, Bob verifies, Eve fails  (GF(31), o=4, v=8)
 */

#include <iostream>
#include <random>
#include <cassert>
#include "uov/keygen.hpp"

int main() {
    const int q = 31, o = 4, v = 8;
    std::cout << "UOV demo  q=" << q << "  o=" << o << "  v=" << v
              << "  n=" << (o+v) << "\n\n";

    std::mt19937 rng(42);

    // --- Key generation ---
    auto key = uov::keygen(q, o, v, rng);
    std::cout << "Key generation: OK\n";

    // --- Alice signs ---
    std::mt19937 sign_rng(1);
    std::uniform_int_distribution<int> dist(0, q - 1);
    uov::Vec msg(o);
    for (auto& x : msg) x = dist(sign_rng);

    auto sig_opt = key.sign(msg, sign_rng);
    assert(sig_opt.has_value() && "signing failed");
    auto& sig = *sig_opt;

    std::cout << "Alice's message :";
    for (int x : msg) std::cout << " " << x;
    std::cout << "\nAlice's signature:";
    for (int x : sig) std::cout << " " << x;
    std::cout << "\n";

    // --- Bob verifies ---
    bool ok = key.verify(msg, sig);
    std::cout << "Bob verifies    : " << (ok ? "PASS" : "FAIL") << "\n";
    assert(ok);

    // --- Wrong message rejected ---
    uov::Vec wrong_msg = msg;
    for (auto& x : wrong_msg) x = (x + 1) % q;
    bool wrong_ok = key.verify(wrong_msg, sig);
    std::cout << "Wrong message   : " << (wrong_ok ? "BUG" : "correctly rejected") << "\n";
    assert(!wrong_ok);

    // --- Eve tries 1000 random forgeries ---
    std::mt19937 eve_rng(999);
    int successes = 0;
    for (int i = 0; i < 1000; ++i) {
        uov::Vec forgery(o + v);
        for (auto& x : forgery) x = dist(eve_rng);
        if (key.verify(msg, forgery)) ++successes;
    }
    std::cout << "Eve's forgeries : " << successes << "/1000 accepted  (expect 0)\n";
    assert(successes == 0);

    std::cout << "\nAll checks passed.\n";
    return 0;
}
