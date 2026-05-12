//! GF(q) arithmetic over a prime field (runtime q).

pub type Vec = std::vec::Vec<u64>;
pub type Mat = std::vec::Vec<std::vec::Vec<u64>>;

// ── Scalar operations ─────────────────────────────────────────────────────────

pub fn gf_add(a: u64, b: u64, q: u64) -> u64 { (a + b) % q }
pub fn gf_mul(a: u64, b: u64, q: u64) -> u64 { (a * b) % q }

/// Modular inverse via extended Euclidean algorithm.
pub fn gf_inv(a: u64, q: u64) -> u64 {
    assert!(a % q != 0, "zero has no inverse in GF(q)");
    let (mut old_r, mut r) = (a as i64, q as i64);
    let (mut old_s, mut s) = (1i64, 0i64);
    while r != 0 {
        let quot = old_r / r;
        (old_r, r) = (r, old_r - quot * r);
        (old_s, s) = (s, old_s - quot * s);
    }
    ((old_s % q as i64 + q as i64) as u64) % q
}

pub fn mod_sub(a: u64, b: u64, q: u64) -> u64 {
    ((a as i64 - b as i64).rem_euclid(q as i64)) as u64
}

// ── Vector operations ─────────────────────────────────────────────────────────

pub fn dot(u: &[u64], v: &[u64], q: u64) -> u64 {
    u.iter().zip(v.iter()).fold(0u64, |acc, (&a, &b)| (acc + a * b) % q)
}

pub fn vec_add(u: &[u64], v: &[u64], q: u64) -> Vec {
    u.iter().zip(v.iter()).map(|(&a, &b)| (a + b) % q).collect()
}

pub fn vec_sub(u: &[u64], v: &[u64], q: u64) -> Vec {
    u.iter().zip(v.iter()).map(|(&a, &b)| mod_sub(a, b, q)).collect()
}

// ── Matrix-vector product ─────────────────────────────────────────────────────

pub fn mat_mul_vec(m: &Mat, v: &[u64], q: u64) -> Vec {
    m.iter().map(|row| dot(row, v, q)).collect()
}

// ── Gaussian elimination ──────────────────────────────────────────────────────

/// Solve `m * x = b` over GF(q). Returns `None` if `m` is singular.
pub fn gauss_solve(m: &Mat, b: &[u64], q: u64) -> Option<Vec> {
    let n = b.len();
    // Augmented matrix [m | b]
    let mut aug: Mat = (0..n)
        .map(|i| { let mut row = m[i].clone(); row.push(b[i]); row })
        .collect();

    for col in 0..n {
        let pivot = (col..n).find(|&row| aug[row][col] % q != 0)?;
        aug.swap(col, pivot);

        let inv_p = gf_inv(aug[col][col], q);
        for j in col..=n {
            aug[col][j] = gf_mul(aug[col][j], inv_p, q);
        }

        for row in 0..n {
            if row == col || aug[row][col] == 0 { continue; }
            let factor = aug[row][col];
            for j in col..=n {
                let sub = gf_mul(factor, aug[col][j], q);
                aug[row][j] = mod_sub(aug[row][j], sub, q);
            }
        }
    }

    Some((0..n).map(|i| aug[i][n]).collect())
}

// ── Matrix inverse ────────────────────────────────────────────────────────────

pub fn gf_matinv(m: &Mat, q: u64) -> Option<Mat> {
    let n = m.len();
    let mut aug: Mat = (0..n)
        .map(|i| {
            let mut row = m[i].clone();
            row.extend((0..n).map(|j| if i == j { 1 } else { 0 }));
            row
        })
        .collect();

    for col in 0..n {
        let pivot = (col..n).find(|&row| aug[row][col] % q != 0)?;
        aug.swap(col, pivot);

        let inv_p = gf_inv(aug[col][col], q);
        for j in 0..2*n {
            aug[col][j] = gf_mul(aug[col][j], inv_p, q);
        }

        for row in 0..n {
            if row == col || aug[row][col] == 0 { continue; }
            let factor = aug[row][col];
            for j in 0..2*n {
                let sub = gf_mul(factor, aug[col][j], q);
                aug[row][j] = mod_sub(aug[row][j], sub, q);
            }
        }
    }

    Some((0..n).map(|i| (0..n).map(|j| aug[i][n + j]).collect()).collect())
}

// ── Random helpers ────────────────────────────────────────────────────────────

/// Simple seeded LCG for deterministic random numbers (no external deps).
pub struct Rng { state: u64 }

impl Rng {
    pub fn new(seed: u64) -> Self { Self { state: seed ^ 0x12345678ABCD } }

    pub fn next_u64(&mut self) -> u64 {
        // Splitmix64
        self.state = self.state.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        z ^ (z >> 31)
    }

    pub fn next_field(&mut self, q: u64) -> u64 { self.next_u64() % q }

    pub fn random_vec(&mut self, n: usize, q: u64) -> Vec {
        (0..n).map(|_| self.next_field(q)).collect()
    }

    pub fn random_mat(&mut self, rows: usize, cols: usize, q: u64) -> Mat {
        (0..rows).map(|_| self.random_vec(cols, q)).collect()
    }

    pub fn random_invertible(&mut self, n: usize, q: u64) -> Mat {
        loop {
            let m = self.random_mat(n, n, q);
            if gf_matinv(&m, q).is_some() { return m; }
        }
    }
}
