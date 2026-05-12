//! Key generation for the UOV signature scheme.

use crate::central_map::CentralMap;
use crate::field::{gf_matinv, Rng};
use crate::scheme::UOVKey;

pub fn keygen(q: u64, o: usize, v: usize, rng: &mut Rng) -> UOVKey {
    let f = CentralMap::random(q, o, v, rng);
    let t = rng.random_invertible(o + v, q);
    let t_inv = gf_matinv(&t, q).expect("T must be invertible");
    UOVKey { q, o, v, f, t, t_inv }
}
