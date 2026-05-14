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
  if (obj.pubkey_fp) {
    lines.push(`pubkey_fp: ${String(obj.pubkey_fp).slice(0, 20)}… (${String(obj.pubkey_fp).length} hex chars)`);
  }
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
  st.textContent = "Ready — you can generate a certificate below.";
  st.classList.add("wasm-ready");
} catch (e) {
  const st = $("wasmStatus");
  st.textContent = `WASM could not load (open this site over http(s), not file://): ${e.message}`;
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

function switchTab(panelId) {
  document.querySelectorAll(".tab").forEach((btn) => {
    const on = btn.dataset.tab === panelId;
    btn.classList.toggle("tab-active", on);
    btn.setAttribute("aria-selected", on ? "true" : "false");
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("hidden", panel.id !== panelId);
  });
}

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => switchTab(btn.dataset.tab));
});

function setOut(el, cls, text) {
  el.className = `out out-tight ${cls}`;
  el.textContent = text;
}

$("btnGenerate").addEventListener("click", () => {
  const out = $("outWasm");
  if (!wasmReady) {
    setOut(out, "err", "WASM not available.");
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
    setOut(
      out,
      "ok",
      "Certificate generated. JSON is in the “Certificate JSON” tab (switched for you). You can verify or copy it there.",
    );
    switchTab("panel-cert");
    $("certIn").focus();
  } catch (e) {
    setOut(out, "err", e?.message ?? String(e));
  }
});

$("btnVerifyCrypto").addEventListener("click", () => {
  const out = $("out");
  if (!wasmReady) {
    setOut(out, "err", "WASM not available.");
    return;
  }
  const raw = $("certIn").value.trim();
  if (!raw) {
    setOut(out, "err", "Add certificate JSON first (generate or paste).");
    return;
  }
  try {
    const ok = wasm_verify_certificate(raw);
    setOut(
      out,
      ok ? "ok" : "err",
      ok ? "PASS — P(σ) = y holds for the embedded public key." : "FAIL — signature does not match digest.",
    );
  } catch (e) {
    setOut(out, "err", e?.message ?? String(e));
  }
});

$("btnParse").addEventListener("click", () => {
  const out = $("out");
  const raw = $("certIn").value.trim();
  if (!raw) {
    setOut(out, "err", "Paste JSON first.");
    return;
  }
  try {
    const obj = JSON.parse(raw);
    if (typeof obj !== "object" || obj === null) {
      throw new Error("Root JSON must be an object.");
    }
    setOut(out, "ok", summarize(obj));
  } catch (e) {
    setOut(out, "err", `Invalid JSON: ${e.message}`);
  }
});

$("btnClear").addEventListener("click", () => {
  $("certIn").value = "";
  const out = $("out");
  out.textContent = "";
  out.className = "out out-tight";
});

$("btnRandomSeeds").addEventListener("click", () => {
  const r = () => BigInt(Math.floor(Math.random() * Number.MAX_SAFE_INTEGER));
  $("keySeed").value = String(r());
  $("signSeed").value = String(r());
});

$("btnResetDemo").addEventListener("click", () => {
  $("msgIn").value = "hello from SilentVerify";
  $("paramQ").value = "31";
  $("paramO").value = "4";
  $("paramV").value = "8";
  $("keySeed").value = "42";
  $("signSeed").value = "7";
  const ow = $("outWasm");
  ow.textContent = "";
  ow.className = "out out-tight";
});

$("btnCopyCert").addEventListener("click", async () => {
  const raw = $("certIn").value.trim();
  const out = $("out");
  if (!raw) {
    setOut(out, "err", "Nothing to copy.");
    return;
  }
  try {
    await navigator.clipboard.writeText(raw);
    setOut(out, "ok", "Copied certificate JSON to clipboard.");
  } catch {
    $("certIn").select();
    setOut(out, "ok", "Clipboard blocked — JSON is selected; use Ctrl/Cmd+C.");
  }
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

function summarizeApiPayload(data) {
  if (!data || typeof data !== "object" || data.result == null) return "";
  const r = data.result;
  const parts = [];
  if (r.ok) parts.push("Overall: PASS.");
  else parts.push("Overall: FAIL.");
  if (typeof r.digest_binds_to_anchor === "boolean") {
    parts.push(r.digest_binds_to_anchor ? "Digest matches live anchor." : "Digest does NOT match live anchor.");
  }
  if (typeof r.certificate_crypto_ok === "boolean") {
    parts.push(r.certificate_crypto_ok ? "UOV verify OK." : "UOV verify failed.");
  }
  return `${parts.join(" ")}\n\n`;
}

async function postChainApi(path, body, outEl) {
  const base = $("apiBase").value.trim().replace(/\/$/, "");
  if (!base) {
    setOut(outEl, "err", "Set API base URL, then run: cd impl/python && python -m statecert.api_server");
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
    setOut(outEl, "err", `Non-JSON response (HTTP ${res.status}): ${text.slice(0, 400)}`);
    return;
  }
  if (!res.ok) {
    setOut(outEl, "err", JSON.stringify(data, null, 2));
    return;
  }
  const summary = summarizeApiPayload(data);
  outEl.className = `out out-tight ${data.result?.ok ? "ok" : "err"}`;
  outEl.textContent = `${summary}${JSON.stringify(data, null, 2)}`;
}

$("btnApiVerify").addEventListener("click", async () => {
  const out = $("apiOut");
  const btn = $("btnApiVerify");
  const base = $("apiBase").value.trim().replace(/\/$/, "");
  if (!base) {
    setOut(out, "err", "Set API base URL first.");
    return;
  }
  const raw = $("certIn").value.trim();
  if (!raw) {
    setOut(out, "err", "Put a chain-issued certificate in the “Certificate JSON” tab first.");
    switchTab("panel-cert");
    return;
  }
  let certObj;
  try {
    certObj = JSON.parse(raw);
  } catch (e) {
    setOut(out, "err", `Invalid certificate JSON: ${e.message}`);
    return;
  }
  const kind = $("apiChainKind").value;
  const prevLabel = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Verifying…";
  try {
    if (kind === "evm") {
      const rpc = $("apiRpc").value.trim();
      if (!rpc) {
        setOut(out, "err", "Set EVM JSON-RPC URL.");
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
        setOut(out, "err", "Set Solana JSON-RPC URL.");
        return;
      }
      const body = {
        rpc_url: rpc,
        certificate: certObj,
        cluster_id: $("apiClusterId").value.trim() || "mainnet-beta",
        commitment: $("apiCommitment").value.trim() || "finalized",
      };
      const slotRaw = $("apiSlot").value.trim();
      if (slotRaw) {
        const s = parseInt(slotRaw, 10);
        if (!Number.isFinite(s)) {
          setOut(out, "err", "Slot must be a number.");
          return;
        }
        body.slot = s;
      }
      await postChainApi("/api/v1/solana/verify-state-cert", body, out);
      return;
    }
    if (kind === "cosmos") {
      const rest = $("apiRest").value.trim();
      const cid = $("apiCosmosChainId").value.trim();
      if (!rest) {
        setOut(out, "err", "Set Cosmos REST base URL.");
        return;
      }
      if (!cid) {
        setOut(out, "err", "Set Cosmos chain_id.");
        return;
      }
      const body = { rest_base: rest, chain_id: cid, certificate: certObj };
      const hRaw = $("apiCosmosHeight").value.trim();
      if (hRaw) {
        const h = parseInt(hRaw, 10);
        if (!Number.isFinite(h)) {
          setOut(out, "err", "Height must be a number.");
          return;
        }
        body.height = h;
      }
      await postChainApi("/api/v1/cosmos/verify-state-cert", body, out);
      return;
    }
    if (kind === "xrp") {
      const rpc = $("apiRpcXrp").value.trim();
      const nid = $("apiXrpNetworkId").value.trim();
      if (!rpc) {
        setOut(out, "err", "Set XRPL JSON-RPC URL.");
        return;
      }
      if (!nid) {
        setOut(out, "err", "Set network_id (must match issuance).");
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
    setOut(out, "err", "Unknown chain type.");
  } catch (e) {
    setOut(out, "err", e?.message ?? String(e));
  } finally {
    btn.disabled = false;
    btn.textContent = prevLabel;
  }
});
