# SilentVerify mini-site (static)

Single-page explainer plus a **WASM-backed** demo: generate `silentverify.state_cert/v1` JSON in the browser (Rust `uov` + `wasm-bindgen`) and run cryptographic verify `P(σ) = y`.

## Build WASM (required before `file://` or static hosting)

From repo root:

```bash
cd web/uov-wasm && wasm-pack build --target web --release --out-dir ../pkg
```

Install [wasm-pack](https://rustwasm.github.io/wasm-pack/installer/) once if needed. This writes `web/pkg/` (`uov_wasm.js`, `uov_wasm_bg.wasm`, …). That directory is gitignored; **GitHub Actions** runs the same build before uploading the `web/` artifact.

### Chain verify API (optional)

The static site can call a small Python server that fetches EVM state over JSON-RPC (avoids browser CORS). See [`statecert/README_CHAIN_API.md`](statecert/README_CHAIN_API.md).

```bash
cd impl/python && python -m statecert.api_server
```

Then open the **Chain verify (API)** section on the site (same origin or set `SILENTVERIFY_CORS_ORIGIN`).

## Free hosting (GitHub Pages)

### One-time setup (required — fixes `configure-pages` “Not Found”)

GitHub only exposes the Pages API **after** the repo is configured to build with Actions:

1. Open the repo on GitHub → **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment**, set **Source** to **GitHub Actions** (not “Deploy from a branch”, not “None”).
3. Save. Wait a few seconds so GitHub registers the site (this step is what prevents `Get Pages site failed` / HTTP 404 from `actions/configure-pages`).

`actions/configure-pages` cannot turn Pages on using the default `GITHUB_TOKEN` alone; the UI step above is required unless you supply a separate PAT with admin scope (not documented here).

### After setup

1. Push to `main` (or run **Actions → GitHub Pages → Run workflow**). The workflow `.github/workflows/pages.yml` builds WASM into `web/pkg/` then publishes the `web/` folder.
2. Site URL (project pages): `https://<user>.github.io/<repo>/`  
   Example: `https://beanapologist.github.io/UOVscheme/`

### Local preview

Use an HTTP server (ES modules + WASM do not work reliably from `file://`):

```bash
cd web/uov-wasm && wasm-pack build --target web --release --out-dir ../pkg
cd ../.. && cd web && python3 -m http.server 8080
# open http://127.0.0.1:8080/
```

## Assets

`assets/silentverify-logo.png` is copied from `branding/` for self-contained static hosting. Regenerate if the brand asset changes:

```bash
cp ../branding/silentverify-logo.png assets/
```
