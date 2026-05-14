//! Browser-side UOV certificate issuance + verification (matches `impl/python` wire format).

use sha2::{Digest, Sha256};
use sha3::digest::{ExtendableOutput, Update, XofReader};
use sha3::Shake256;
use uov::central_map::{CentralMap, CentralMapComp};
use uov::field::{gf_matinv, Rng};
use uov::keygen;
use uov::scheme::UOVKey;
use wasm_bindgen::prelude::*;

const DOMAIN: &[u8] = b"UOVscheme/v1|";

fn hash_message_to_digest(q: u64, o: usize, message: &[u8]) -> Result<Vec<u64>, String> {
    if o < 1 {
        return Err("o must be positive".into());
    }
    let mut hasher = Shake256::default();
    hasher.update(DOMAIN);
    hasher.update(&(message.len() as u64).to_be_bytes());
    hasher.update(message);
    let nbytes = o * 8 * 16;
    let mut buf = vec![0u8; nbytes];
    hasher.finalize_xof().read(&mut buf);
    uniform_mod_q(&buf, q, o)
}

fn uniform_mod_q(stream: &[u8], q: u64, o: usize) -> Result<Vec<u64>, String> {
    if q < 2 {
        return Err("q must be >= 2".into());
    }
    let max_valid = (1u128 << 64) / (q as u128) * (q as u128);
    let mut out = Vec::with_capacity(o);
    let mut pos = 0usize;
    while out.len() < o {
        if pos + 8 > stream.len() {
            return Err("insufficient XOF output for rejection sampling".into());
        }
        let chunk = u64::from_be_bytes(stream[pos..pos + 8].try_into().unwrap());
        pos += 8;
        if (chunk as u128) < max_valid {
            out.push(chunk % q);
        }
    }
    Ok(out)
}

fn comp_wire(c: &CentralMapComp) -> serde_json::Value {
    serde_json::json!({
        "A": c.a,
        "B": c.b,
        "c": c.c,
        "d": c.d,
        "e": c.e,
    })
}

fn public_key_wire(key: &UOVKey) -> serde_json::Value {
    serde_json::json!({
        "q": key.q,
        "o": key.o,
        "v": key.v,
        "central_map": {
            "comps": key.f.comps.iter().map(comp_wire).collect::<Vec<_>>()
        },
        "T": key.t,
    })
}

fn mat_from_json(v: &serde_json::Value) -> Result<Vec<Vec<u64>>, String> {
    let rows = v
        .as_array()
        .ok_or("matrix must be array")?
        .iter()
        .map(|row| {
            row.as_array()
                .ok_or("matrix row must be array")?
                .iter()
                .map(|x| json_u64(x))
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    Ok(rows)
}

fn json_u64(x: &serde_json::Value) -> Result<u64, String> {
    if let Some(n) = x.as_u64() {
        return Ok(n);
    }
    if let Some(n) = x.as_i64() {
        if n >= 0 {
            return Ok(n as u64);
        }
    }
    Err(format!("expected non-negative integer, got {x}"))
}

fn parse_comp(q: u64, o: usize, v: usize, d: &serde_json::Value) -> Result<CentralMapComp, String> {
    Ok(CentralMapComp {
        q,
        o,
        v,
        a: mat_from_json(&d["A"])?,
        b: mat_from_json(&d["B"])?,
        c: d["c"]
            .as_array()
            .ok_or("c")?
            .iter()
            .map(json_u64)
            .collect::<Result<Vec<_>, _>>()?,
        d: d["d"]
            .as_array()
            .ok_or("d")?
            .iter()
            .map(json_u64)
            .collect::<Result<Vec<_>, _>>()?,
        e: json_u64(&d["e"])?,
    })
}

fn uovkey_from_public_wire(pk: &serde_json::Value) -> Result<UOVKey, String> {
    let q = json_u64(&pk["q"])?;
    let o = pk["o"].as_u64().ok_or("o")? as usize;
    let v = pk["v"].as_u64().ok_or("v")? as usize;
    let comps_arr = pk["central_map"]["comps"]
        .as_array()
        .ok_or("central_map.comps")?;
    let mut comps = Vec::with_capacity(comps_arr.len());
    for c in comps_arr {
        comps.push(parse_comp(q, o, v, c)?);
    }
    let t = mat_from_json(&pk["T"])?;
    let t_inv = gf_matinv(&t, q).ok_or("singular T")?;
    let f = CentralMap { q, o, v, comps };
    Ok(UOVKey {
        q,
        o,
        v,
        f,
        t,
        t_inv,
    })
}

/// Issue `silentverify.state_cert/v1` over UTF-8 message bytes (same as Python `issue_message_certificate`).
#[wasm_bindgen]
pub fn wasm_issue_message_certificate(
    message: &str,
    q: u32,
    o: u32,
    v: u32,
    key_seed: u64,
    sign_seed: u64,
) -> Result<String, JsValue> {
    let q = q as u64;
    let o = o as usize;
    let v = v as usize;
    let message = message.as_bytes();

    let mut krng = Rng::new(key_seed);
    let key = keygen(q, o, v, &mut krng);

    let digest_y = hash_message_to_digest(q, o, message).map_err(JsValue::from)?;
    let mut srng = Rng::new(sign_seed);
    let sigma = key
        .sign(&digest_y, &mut srng, 10_000)
        .ok_or_else(|| JsValue::from_str("signing failed (retry with another sign_seed)"))?;

    let message_sha256_hex = format!("{:x}", Sha256::digest(message));

    let cert = serde_json::json!({
        "schema_version": "silentverify.state_cert/v1",
        "q": key.q,
        "o": key.o,
        "v": key.v,
        "digest_y": digest_y,
        "sigma": sigma,
        "public_key": public_key_wire(&key),
        "message_sha256_hex": message_sha256_hex,
    });

    serde_json::to_string_pretty(&cert).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// Cryptographic verify: `P(σ) = digest_y` under embedded public key (matches Python `verify_certificate`).
#[wasm_bindgen]
pub fn wasm_verify_certificate(json: &str) -> Result<bool, JsValue> {
    let v: serde_json::Value =
        serde_json::from_str(json).map_err(|e| JsValue::from_str(&e.to_string()))?;
    if v["schema_version"].as_str() != Some("silentverify.state_cert/v1") {
        return Ok(false);
    }
    let q = match json_u64(&v["q"]) {
        Ok(x) => x,
        Err(_) => return Ok(false),
    };
    let o = match v["o"].as_u64() {
        Some(x) => x as usize,
        None => return Ok(false),
    };
    let v_dim = match v["v"].as_u64() {
        Some(x) => x as usize,
        None => return Ok(false),
    };
    let digest_y: Vec<u64> = match v["digest_y"].as_array() {
        Some(a) if a.len() == o => match a.iter().map(json_u64).collect::<Result<Vec<_>, _>>() {
            Ok(x) => x,
            Err(_) => return Ok(false),
        },
        _ => return Ok(false),
    };
    let sigma: Vec<u64> = match v["sigma"].as_array() {
        Some(a) if a.len() == o + v_dim => match a.iter().map(json_u64).collect::<Result<Vec<_>, _>>() {
            Ok(x) => x,
            Err(_) => return Ok(false),
        },
        _ => return Ok(false),
    };
    let vk = match uovkey_from_public_wire(&v["public_key"]) {
        Ok(k) => k,
        Err(_) => return Ok(false),
    };
    if vk.q != q || vk.o != o || vk.v != v_dim {
        return Ok(false);
    }
    Ok(vk.verify(&digest_y, &sigma))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hash_message_parity_python_hello() {
        let d = hash_message_to_digest(31, 4, b"hello").unwrap();
        assert_eq!(d, vec![16, 1, 17, 1]);
        assert_eq!(
            format!("{:x}", Sha256::digest(b"hello")),
            "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        );
    }

    #[test]
    fn issue_verify_roundtrip_native() {
        let json = wasm_issue_message_certificate("roundtrip test", 31, 4, 8, 101, 202).unwrap();
        assert!(wasm_verify_certificate(&json).unwrap());
    }
}
