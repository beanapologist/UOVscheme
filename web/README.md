# SilentVerify mini-site (static)

Single-page **consumer-facing** explainer plus a **certificate JSON viewer** (shape only — no in-browser cryptography).

## Free hosting (GitHub Pages)

1. In the GitHub repo: **Settings → Pages → Build and deployment → Source**: select **GitHub Actions** (not “Deploy from a branch” unless you prefer that).
2. Push to `main`; the workflow `.github/workflows/pages.yml` publishes the `web/` folder.
3. Site URL (project pages): `https://<user>.github.io/<repo>/`  
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
