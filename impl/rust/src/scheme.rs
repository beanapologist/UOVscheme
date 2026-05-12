//! UOVKey: public-key evaluation, signing, and verification.

use crate::central_map::CentralMap;
use crate::field::{gauss_solve, mat_mul_vec, mod_sub, Mat, Rng, Vec as FVec};

pub struct UOVKey {
    pub q: u64,
    pub o: usize,
    pub v: usize,
    pub f: CentralMap,
    pub t: Mat,     // (o+v)×(o+v) invertible
    pub t_inv: Mat, // precomputed inverse
}

impl UOVKey {
    pub fn public_eval(&self, sigma: &[u64]) -> FVec {
        let x = mat_mul_vec(&self.t, sigma, self.q);
        let oil = &x[..self.o];
        let vin = &x[self.o..];
        self.f.eval(oil, vin)
    }

    /// Sign message y ∈ GF(q)^o.
    /// Returns None if max_attempts exhausted (extremely unlikely for typical params).
    pub fn sign(&self, y: &[u64], rng: &mut Rng, max_attempts: usize) -> Option<FVec> {
        for _ in 0..max_attempts {
            let vin: FVec = (0..self.v).map(|_| rng.next_field(self.q)).collect();
            let m = self.f.lin_matrix(&vin);
            let b = self.f.vin_const_vec(&vin);
            let rhs: FVec = (0..self.o).map(|i| mod_sub(y[i], b[i], self.q)).collect();

            if let Some(oil) = gauss_solve(&m, &rhs, self.q) {
                let combined: FVec = oil.into_iter().chain(vin).collect();
                return Some(mat_mul_vec(&self.t_inv, &combined, self.q));
            }
        }
        None
    }

    pub fn verify(&self, y: &[u64], sigma: &[u64]) -> bool {
        self.public_eval(sigma) == y
    }
}
