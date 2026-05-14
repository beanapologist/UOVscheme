import init, { wasm_issue_message_certificate, wasm_verify_certificate } from "./pkg/uov_wasm.js";

const $ = (id) => document.getElementById(id);

function summarize(obj) {
  const lines = [];
  const sv = obj.schema_version;
  lines.push(`schema_version: ${sv ?? "(missing)"}`);
  if (sv && sv !== "silentverify.state_cert/v1") {
    lines.push("(note: may be legacy or custom schema)");
  }
  if (obj.q != null) lines.push(`field: GF(${obj.q})  oil o=${obj.o}  vinegar v=${obj.v}`);
  if (Array.isArray(obj.digest_y)) lines.push(`digest_y: length ${obj.digest_y.length}`);
  if (Array.isArray(obj.sigma)) lines.push(`sigma: length ${obj.sigma.length}`);
  if (obj.pubkey_fp) lines.push(`pubkey_fp: ${String(obj.pubkey_fp).slice(0, 20)}… (${String(obj.pubkey_fp).length} hex chars)`);
  if (obj.metadata && typeof obj.metadata === "object") {
    lines.push(`metadata keys: ${Object.keys(obj.metadata).join(", ") || "(empty)"}`);
  }
  lines.push(`raw JSON size: ${JSON.stringify(obj).length} chars`);
  return lines.join("\n");
}

let wasmReady = false;

try {
  await init();
  wasmReady = true;
  const st = $("wasmStatus");
  st.textContent = "WASM loaded: in-browser issue + verify (demo parameters).";
  st.classList.add("wasm-ready");
} catch (e) {
  const st = $("wasmStatus");
  st.textContent = `WASM failed to load (use a local server, not file://): ${e.message}`;
  st.classList.add("wasm-err");
}

function readU32(id, fallback) {
  const n = Number.parseInt(String($(id).value).trim(), 10);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
}

function readSeed(id, fallback) {
  const s = String($(id).value).trim();
  if (!s) return BigInt(fallback);
  return BigInt(s);
}

$("btnGenerate").addEventListener("click", () => {
  const out = $("out");
  if (!wasmReady) {
    out.className = "out err";
    out.textContent = "WASM not available.";
    return;
  }
  const message = $("msgIn").value;
  const q = readU32("paramQ", 31);
  const o = readU32("paramO", 4);
  const v = readU32("paramV", 8);
  const keySeed = readSeed("keySeed", 1n);
  const signSeed = readSeed("signSeed", 2n);
  try {
    const json = wasm_issue_message_certificate(message, q, o, v, keySeed, signSeed);
    $("certIn").value = json;
    out.className = "out ok";
    out.textContent = "Generated silentverify.state_cert/v1 (see textarea). You can “Verify crypto” or “Parse & summarize”.";
  } catch (e) {
    out.className = "out err";
    out.textContent = e?.message ?? String(e);
  }
});

$("btnVerifyCrypto").addEventListener("click", () => {
  const out = $("out");
  if (!wasmReady) {
    out.className = "out err";
    out.textContent = "WASM not available.";
    return;
  }
  const raw = $("certIn").value.trim();
  if (!raw) {
    out.className = "out err";
    out.textContent = "Paste certificate JSON first.";
    return;
  }
  try {
    const ok = wasm_verify_certificate(raw);
    out.className = ok ? "out ok" : "out err";
    out.textContent = ok ? "Cryptographic verify: PASS (P(σ) = y under embedded public key)." : "Cryptographic verify: FAIL.";
  } catch (e) {
    out.className = "out err";
    out.textContent = e?.message ?? String(e);
  }
});

$("btnParse").addEventListener("click", () => {
  const out = $("out");
  const raw = $("certIn").value.trim();
  if (!raw) {
    out.className = "out err";
    out.textContent = "Paste JSON first.";
    return;
  }
  try {
    const obj = JSON.parse(raw);
    if (typeof obj !== "object" || obj === null) {
      throw new Error("Root JSON must be an object.");
    }
    out.className = "out ok";
    out.textContent = summarize(obj);
  } catch (e) {
    out.className = "out err";
    out.textContent = `Invalid JSON: ${e.message}`;
  }
});

$("btnClear").addEventListener("click", () => {
  $("certIn").value = "";
  const out = $("out");
  out.textContent = "";
  out.className = "out";
});

$("btnRandomSeeds").addEventListener("click", () => {
  const r = () => BigInt(Math.floor(Math.random() * Number.MAX_SAFE_INTEGER));
  $("keySeed").value = String(r());
  $("signSeed").value = String(r());
});

function parseBlockArg(s) {
  const t = String(s).trim();
  if (t === "") return "latest";
  if (/^\d+$/.test(t)) return parseInt(t, 10);
  return t;
}

function parseXrpLedgerIndex(s) {
  const t = String(s).trim();
  if (t === "") return "validated";
  if (/^\d+$/.test(t)) return parseInt(t, 10);
  return t;
}

const API_PANELS = {
  evm: "apiFieldsEvm",
  solana: "apiFieldsSolana",
  cosmos: "apiFieldsCosmos",
  xrp: "apiFieldsXrp",
};

function syncApiChainPanels() {
  const k = $("apiChainKind").value;
  for (const [key, id] of Object.entries(API_PANELS)) {
    $(id).classList.toggle("hidden", key !== k);
  }
}

$("apiChainKind").addEventListener("change", syncApiChainPanels);
syncApiChainPanels();

async function postChainApi(path, body, out) {
  const base = $("apiBase").value.trim().replace(/\/$/, "");
  if (!base) {
    out.className = "out err";
    out.textContent = "Set API base URL (run python -m statecert.api_server from impl/python).";
    return;
  }
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    out.className = "out err";
    out.textContent = `Non-JSON response (HTTP ${res.status}): ${text.slice(0, 400)}`;
    return;
  }
  if (!res.ok) {
    out.className = "out err";
    out.textContent = JSON.stringify(data, null, 2);
    return;
  }
  out.className = data.result?.ok ? "out ok" : "out err";
  out.textContent = JSON.stringify(data, null, 2);
}

$("btnApiVerify").addEventListener("click", async () => {
  const out = $("apiOut");
  const base = $("apiBase").value.trim().replace(/\/$/, "");
  if (!base) {
    out.className = "out err";
    out.textContent = "Set API base URL (run python -m statecert.api_server from impl/python).";
    return;
  }
  const raw = $("certIn").value.trim();
  if (!raw) {
    out.className = "out err";
    out.textContent = "Paste the state certificate JSON (from StateVerifier / Python) first.";
    return;
  }
  let certObj;
  try {
    certObj = JSON.parse(raw);
  } catch (e) {
    out.className = "out err";
    out.textContent = `Invalid certificate JSON: ${e.message}`;
    return;
  }
  const kind = $("apiChainKind").value;
  try {
    if (kind === "evm") {
      const rpc = $("apiRpc").value.trim();
      if (!rpc) {
        out.className = "out err";
        out.textContent = "Set EVM JSON-RPC URL.";
        return;
      }
      const body = {
        rpc_url: rpc,
        block: parseBlockArg($("apiBlock").value),
        certificate: certObj,
      };
      const caip2 = $("apiCaip2").value.trim();
      if (caip2) body.caip2_chain_id = caip2;
      await postChainApi("/api/v1/evm/verify-state-cert", body, out);
      return;
    }
    if (kind === "solana") {
      const rpc = $("apiRpcSol").value.trim();
      if (!rpc) {
        out.className = "out err";
        out.textContent = "Set Solana JSON-RPC URL.";
        return;
      }
      const body = {
        rpc_url: rpc,
        certificate: certObj,
        cluster_id: $("apiClusterId").value.trim() || "mainnet-beta",
        commitment: $("apiCommitment").value.trim() || "finalized",
      };
      const slotRaw = $("apiSlot").value.trim();
      if (slotRaw) body.slot = parseInt(slotRaw, 10);
      await postChainApi("/api/v1/solana/verify-state-cert", body, out);
      return;
    }
    if (kind === "cosmos") {
      const rest = $("apiRest").value.trim();
      const cid = $("apiCosmosChainId").value.trim();
      if (!rest) {
        out.className = "out err";
        out.textContent = "Set Cosmos REST base URL.";
        return;
      }
      if (!cid) {
        out.className = "out err";
        out.textContent = "Set Cosmos chain_id.";
        return;
      }
      const body = { rest_base: rest, chain_id: cid, certificate: certObj };
      const hRaw = $("apiCosmosHeight").value.trim();
      if (hRaw) body.height = parseInt(hRaw, 10);
      await postChainApi("/api/v1/cosmos/verify-state-cert", body, out);
      return;
    }
    if (kind === "xrp") {
      const rpc = $("apiRpcXrp").value.trim();
      const nid = $("apiXrpNetworkId").value.trim();
      if (!rpc) {
        out.className = "out err";
        out.textContent = "Set XRPL JSON-RPC URL.";
        return;
      }
      if (!nid) {
        out.className = "out err";
        out.textContent = "Set network_id (must match how the certificate was issued).";
        return;
      }
      const body = {
        rpc_url: rpc,
        network_id: nid,
        ledger_index: parseXrpLedgerIndex($("apiXrpLedger").value),
        certificate: certObj,
      };
      await postChainApi("/api/v1/xrp/verify-state-cert", body, out);
      return;
    }
    out.className = "out err";
    out.textContent = "Unknown chain kind.";
  } catch (e) {
    out.className = "out err";
    out.textContent = e?.message ?? String(e);
  }
});
