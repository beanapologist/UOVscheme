//! Alice signs, Bob verifies, Eve fails  (GF(31), o=4, v=8)

use uov::{keygen, field::Rng};

fn main() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    println!("UOV demo  q={}  o={}  v={}  n={}\n", q, o, v, o + v);

    let mut rng = Rng::new(42);

    // --- Key generation ---
    let key = keygen(q, o, v, &mut rng);
    println!("Key generation: OK");

    // --- Alice signs ---
    let mut sign_rng = Rng::new(1);
    let msg: Vec<u64> = (0..o).map(|_| sign_rng.next_field(q)).collect();
    let sig = key.sign(&msg, &mut sign_rng, 1000).expect("signing failed");

    print!("Alice's message :");
    for x in &msg { print!(" {}", x); }
    print!("\nAlice's signature:");
    for x in &sig { print!(" {}", x); }
    println!();

    // --- Bob verifies ---
    let ok = key.verify(&msg, &sig);
    println!("Bob verifies    : {}", if ok { "PASS" } else { "FAIL" });
    assert!(ok);

    // --- Wrong message rejected ---
    let wrong: Vec<u64> = msg.iter().map(|&x| (x + 1) % q).collect();
    let wrong_ok = key.verify(&wrong, &sig);
    println!("Wrong message   : {}", if wrong_ok { "BUG" } else { "correctly rejected" });
    assert!(!wrong_ok);

    // --- Eve tries 1000 random forgeries ---
    let mut eve_rng = Rng::new(999);
    let successes: usize = (0..1000)
        .filter(|_| {
            let forgery: Vec<u64> = (0..o + v).map(|_| eve_rng.next_field(q)).collect();
            key.verify(&msg, &forgery)
        })
        .count();
    println!("Eve's forgeries : {}/1000 accepted  (expect 0)", successes);
    assert_eq!(successes, 0);

    println!("\nAll checks passed.");
}
