//! Integration tests mirroring every Lean theorem.

use uov::field::{dot, gauss_solve, gf_matinv, mat_mul_vec, Rng};
use uov::central_map::{CentralMap, CentralMapComp};
use uov::keygen;

// ── eval_affine ───────────────────────────────────────────────────────────────

#[test]
fn test_eval_affine_exhaustive() {
    let (q, o, v) = (7u64, 2usize, 2usize);
    let mut rng = Rng::new(0);
    let comp = CentralMapComp::random(q, o, v, &mut rng);
    for o0 in 0..q { for o1 in 0..q { for v0 in 0..q { for v1 in 0..q {
        let oil = vec![o0, o1];
        let vin = vec![v0, v1];
        let lhs = comp.eval(&oil, &vin);
        let lc = comp.lin_coeff(&vin);
        let rhs = (dot(&oil, &lc, q) + comp.vin_const(&vin)) % q;
        assert_eq!(lhs, rhs, "eval_affine at oil={:?} vin={:?}", oil, vin);
    }}}}
}

#[test]
fn test_eval_affine_random() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    let mut rng = Rng::new(7);
    let comp = CentralMapComp::random(q, o, v, &mut rng);
    for _ in 0..200 {
        let oil: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
        let vin: Vec<u64> = (0..v).map(|_| rng.next_field(q)).collect();
        let lhs = comp.eval(&oil, &vin);
        let lc = comp.lin_coeff(&vin);
        let rhs = (dot(&oil, &lc, q) + comp.vin_const(&vin)) % q;
        assert_eq!(lhs, rhs);
    }
}

#[test]
fn test_eval_zero_oil() {
    let (q, o, v) = (13u64, 3usize, 5usize);
    let mut rng = Rng::new(1);
    let comp = CentralMapComp::random(q, o, v, &mut rng);
    let zero_oil = vec![0u64; o];
    for _ in 0..20 {
        let vin: Vec<u64> = (0..v).map(|_| rng.next_field(q)).collect();
        assert_eq!(comp.eval(&zero_oil, &vin), comp.vin_const(&vin));
    }
}

#[test]
fn test_eval_zero_vin() {
    let (q, o, v) = (13u64, 3usize, 5usize);
    let mut rng = Rng::new(2);
    let comp = CentralMapComp::random(q, o, v, &mut rng);
    let zero_vin = vec![0u64; v];
    for _ in 0..20 {
        let oil: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
        let expected = (dot(&comp.c, &oil, q) + comp.e) % q;
        assert_eq!(comp.eval(&oil, &zero_vin), expected);
    }
}

// ── eval_as_linSystem ─────────────────────────────────────────────────────────

#[test]
fn test_eval_as_lin_system() {
    let (q, o, v) = (31u64, 4usize, 6usize);
    let mut rng = Rng::new(10);
    let f = CentralMap::random(q, o, v, &mut rng);
    for _ in 0..50 {
        let oil: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
        let vin: Vec<u64> = (0..v).map(|_| rng.next_field(q)).collect();
        let lhs = f.eval(&oil, &vin);
        let m = f.lin_matrix(&vin);
        let b = f.vin_const_vec(&vin);
        let moil = mat_mul_vec(&m, &oil, q);
        let rhs: Vec<u64> = (0..o).map(|k| (moil[k] + b[k]) % q).collect();
        assert_eq!(lhs, rhs);
    }
}

// ── Gaussian elimination ──────────────────────────────────────────────────────

#[test]
fn test_gauss_identity() {
    let q = 17u64;
    let n = 4;
    let identity: Vec<Vec<u64>> = (0..n)
        .map(|i| (0..n).map(|j| if i == j { 1 } else { 0 }).collect())
        .collect();
    let b = vec![3u64, 1, 4, 1];
    let x = gauss_solve(&identity, &b, q).unwrap();
    assert_eq!(x, b);
}

#[test]
fn test_gauss_random() {
    let q = 31u64;
    let mut rng = Rng::new(42);
    for _ in 0..50 {
        let n = 2 + (rng.next_u64() % 5) as usize;
        let mut m = None;
        for _ in 0..20 {
            let candidate = rng.random_mat(n, n, q);
            if gf_matinv(&candidate, q).is_some() { m = Some(candidate); break; }
        }
        let m = match m { Some(x) => x, None => continue };
        let b: Vec<u64> = (0..n).map(|_| rng.next_field(q)).collect();
        let x = gauss_solve(&m, &b, q).unwrap();
        let check = mat_mul_vec(&m, &x, q);
        assert_eq!(check, b);
    }
}

#[test]
fn test_gauss_singular_returns_none() {
    let q = 7u64;
    let m: Vec<Vec<u64>> = vec![vec![1, 2], vec![2, 4]];
    assert!(gauss_solve(&m, &[1, 2], q).is_none());
}

// ── UOV correctness ───────────────────────────────────────────────────────────

#[test]
fn test_roundtrip_many() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    for i in 0..50u64 {
        let mut krng = Rng::new(i);
        let key = keygen(q, o, v, &mut krng);
        let mut srng = Rng::new(i + 1000);
        let msg: Vec<u64> = (0..o).map(|_| srng.next_field(q)).collect();
        let sig = key.sign(&msg, &mut srng, 1000).expect("sign failed");
        assert!(key.verify(&msg, &sig));
    }
}

#[test]
fn test_wrong_message_rejected() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    let mut rng = Rng::new(7);
    let key = keygen(q, o, v, &mut rng);
    let msg: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
    let sig = key.sign(&msg, &mut rng, 1000).unwrap();
    let wrong: Vec<u64> = msg.iter().map(|&x| (x + 1) % q).collect();
    assert!(!key.verify(&wrong, &sig));
}

#[test]
fn test_zero_vector_rejected() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    let mut rng = Rng::new(8);
    let key = keygen(q, o, v, &mut rng);
    let msg: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
    assert!(!key.verify(&msg, &vec![0u64; o + v]));
}

#[test]
fn test_forgery_rejected() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    let mut rng = Rng::new(77);
    let key = keygen(q, o, v, &mut rng);
    let mut erng = Rng::new(999);
    let msg: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
    let accepted: usize = (0..1000)
        .filter(|_| {
            let f: Vec<u64> = (0..o+v).map(|_| erng.next_field(q)).collect();
            key.verify(&msg, &f)
        })
        .count();
    assert_eq!(accepted, 0);
}

#[test]
fn test_cross_key_rejection() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    let mut rng1 = Rng::new(10);
    let mut rng2 = Rng::new(11);
    let key1 = keygen(q, o, v, &mut rng1);
    let key2 = keygen(q, o, v, &mut rng2);
    let mut srng = Rng::new(55);
    let msg: Vec<u64> = (0..o).map(|_| srng.next_field(q)).collect();
    let sig = key1.sign(&msg, &mut srng, 1000).unwrap();
    assert!(key1.verify(&msg, &sig));
    assert!(!key2.verify(&msg, &sig));
}

#[test]
fn test_public_eval_consistent() {
    let (q, o, v) = (31u64, 4usize, 8usize);
    let mut rng = Rng::new(1234);
    let key = keygen(q, o, v, &mut rng);
    let oil: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
    let vin: Vec<u64> = (0..v).map(|_| rng.next_field(q)).collect();
    let y = key.f.eval(&oil, &vin);
    let combined: Vec<u64> = oil.iter().chain(vin.iter()).copied().collect();
    let sigma = mat_mul_vec(&key.t_inv, &combined, q);
    assert_eq!(key.public_eval(&sigma), y);
    assert!(key.verify(&y, &sigma));
}

#[test]
fn test_parameters_gf7_o3_v5() {
    let (q, o, v) = (7u64, 3usize, 5usize);
    let mut rng = Rng::new(33);
    let key = keygen(q, o, v, &mut rng);
    for _ in 0..30 {
        let msg: Vec<u64> = (0..o).map(|_| rng.next_field(q)).collect();
        let sig = key.sign(&msg, &mut rng, 1000).expect("sign failed");
        assert!(key.verify(&msg, &sig));
    }
}
