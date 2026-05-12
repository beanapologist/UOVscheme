//! CentralMapComp and CentralMap — Rust mirror of CentralMap.lean.

use crate::field::{dot, mat_mul_vec, vec_add, Mat, Rng, Vec};

// ── CentralMapComp ────────────────────────────────────────────────────────────

/// One UOV polynomial: F_k(oil, vin) = oil·A·vin + vin·B·vin + c·oil + d·vin + e.
/// The oil×oil block is absent by construction.
pub struct CentralMapComp {
    pub q: u64,
    pub o: usize,
    pub v: usize,
    pub a: Mat,  // o×v — oil-vinegar cross terms
    pub b: Mat,  // v×v — vinegar-vinegar quadratic terms
    pub c: Vec,  // length o — linear oil coefficients
    pub d: Vec,  // length v — linear vinegar coefficients
    pub e: u64,  // constant term
}

impl CentralMapComp {
    pub fn eval(&self, oil: &[u64], vin: &[u64]) -> u64 {
        let q = self.q;
        let avin = mat_mul_vec(&self.a, vin, q);
        let bvin = mat_mul_vec(&self.b, vin, q);
        (dot(oil, &avin, q)
            + dot(vin, &bvin, q)
            + dot(&self.c, oil, q)
            + dot(&self.d, vin, q)
            + self.e)
            % q
    }

    /// A·vin + c  (linear coefficient vector for fixed vin).
    pub fn lin_coeff(&self, vin: &[u64]) -> Vec {
        let avin = mat_mul_vec(&self.a, vin, self.q);
        vec_add(&avin, &self.c, self.q)
    }

    /// vin·B·vin + d·vin + e  (constant w.r.t. oil).
    pub fn vin_const(&self, vin: &[u64]) -> u64 {
        let q = self.q;
        let bvin = mat_mul_vec(&self.b, vin, q);
        (dot(vin, &bvin, q) + dot(&self.d, vin, q) + self.e) % q
    }

    pub fn random(q: u64, o: usize, v: usize, rng: &mut Rng) -> Self {
        Self {
            q, o, v,
            a: rng.random_mat(o, v, q),
            b: rng.random_mat(v, v, q),
            c: rng.random_vec(o, q),
            d: rng.random_vec(v, q),
            e: rng.next_field(q),
        }
    }
}

// ── CentralMap ────────────────────────────────────────────────────────────────

/// The full UOV central map: o polynomial components over (o+v) variables.
pub struct CentralMap {
    pub q: u64,
    pub o: usize,
    pub v: usize,
    pub comps: std::vec::Vec<CentralMapComp>,  // length o
}

impl CentralMap {
    pub fn eval(&self, oil: &[u64], vin: &[u64]) -> Vec {
        self.comps.iter().map(|c| c.eval(oil, vin)).collect()
    }

    /// o×o matrix M(vin): row k = lin_coeff of comp k.
    pub fn lin_matrix(&self, vin: &[u64]) -> Mat {
        self.comps.iter().map(|c| c.lin_coeff(vin)).collect()
    }

    /// o-vector b(vin): entry k = vin_const of comp k.
    pub fn vin_const_vec(&self, vin: &[u64]) -> Vec {
        self.comps.iter().map(|c| c.vin_const(vin)).collect()
    }

    pub fn random(q: u64, o: usize, v: usize, rng: &mut Rng) -> Self {
        Self {
            q, o, v,
            comps: (0..o).map(|_| CentralMapComp::random(q, o, v, rng)).collect(),
        }
    }
}
