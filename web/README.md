# SilentVerify mini-site (static)

Single-page **consumer-facing** explainer plus a **certificate JSON viewer** (shape only — no in-browser cryptography).

## Free hosting (GitHub Pages)

### One-time setup (required — fixes `configure-pages` “Not Found”)

GitHub only exposes the Pages API **after** the repo is configured to build with Actions:

1. Open the repo on GitHub → **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment**, set **Source** to **GitHub Actions** (not “Deploy from a branch”, not “None”).
3. Save. Wait a few seconds so GitHub registers the site (this step is what prevents `Get Pages site failed` / HTTP 404 from `actions/configure-pages`).

`actions/configure-pages` cannot turn Pages on using the default `GITHUB_TOKEN` alone; the UI step above is required unless you supply a separate PAT with admin scope (not documented here).

### After setup

1. Push to `main` (or run **Actions → GitHub Pages → Run workflow**). The workflow `.github/workflows/pages.yml` publishes the `web/` folder.
2. Site URL (project pages): `https://<user>.github.io/<repo>/`  
   Example: `https://beanapologist.github.io/UOVscheme/`

### Local preview

```bash
cd web && python3 -m http.server 8080
# open http://127.0.0.1:8080/
```

## Assets

`assets/silentverify-logo.png` is copied from `branding/` for self-contained static hosting. Regenerate if the brand asset changes:

```bash
cp ../branding/silentverify-logo.png assets/
```
