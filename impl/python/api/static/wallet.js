/** Browser cert wallet (localStorage). Shared by /docs and /verify. */
(function (global) {
  const STORAGE_KEY = 'sv_cert_wallet';

  function loadWallet() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const data = raw ? JSON.parse(raw) : { certs: [] };
      if (!Array.isArray(data.certs)) data.certs = [];
      return data;
    } catch {
      return { certs: [] };
    }
  }

  function saveWallet(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  function certLabel(wire) {
    const meta = wire.metadata || {};
    if (meta.agent_did) return String(meta.agent_did);
    if (meta.cert_type === 'state' && wire.metadata?.chain_id) {
      return `${wire.metadata.chain_id} @ ${wire.metadata.block_height || '?'}`;
    }
    const ct = meta.cert_type || 'certificate';
    return `${ct} · ${(wire.pubkey_fp || '').slice(0, 12)}…`;
  }

  function saveCert(wire, label) {
    const data = loadWallet();
    const id = crypto.randomUUID ? crypto.randomUUID() : `sv-${Date.now()}`;
    const entry = {
      id,
      label: label || certLabel(wire),
      saved_at: new Date().toISOString(),
      cert: wire,
    };
    const existing = data.certs.findIndex((c) => c.cert && c.cert.pubkey_fp === wire.pubkey_fp && JSON.stringify(c.cert.sigma) === JSON.stringify(wire.sigma));
    if (existing >= 0) {
      data.certs[existing] = { ...data.certs[existing], ...entry, id: data.certs[existing].id };
    } else {
      data.certs.unshift(entry);
    }
    if (data.certs.length > 50) data.certs = data.certs.slice(0, 50);
    saveWallet(data);
    return entry;
  }

  function removeCert(id) {
    const data = loadWallet();
    data.certs = data.certs.filter((c) => c.id !== id);
    saveWallet(data);
  }

  function getCert(id) {
    return loadWallet().certs.find((c) => c.id === id) || null;
  }

  function listCerts() {
    return loadWallet().certs;
  }

  function downloadJson(wire, filename) {
    const blob = new Blob([JSON.stringify(wire, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename || `silentverify-cert-${(wire.pubkey_fp || 'export').slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  global.SVCertWallet = {
    loadWallet,
    saveCert,
    removeCert,
    getCert,
    listCerts,
    certLabel,
    downloadJson,
  };
})(typeof window !== 'undefined' ? window : globalThis);
