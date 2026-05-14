(() => {
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
})();
