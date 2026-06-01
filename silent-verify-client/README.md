# SilentVerify Client

A modern Next.js web application for the **SilentVerify** cryptographic state certificate platform. This client provides a user-friendly interface for understanding, generating, and verifying state certificates across multiple blockchain ecosystems (EVM, Solana, Cosmos, XRPL).

## Table of Contents

-   [Overview](#overview)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Configuration](#configuration)
    -   [Development](#development)
-   [Project Structure](#project-structure)
-   [Architecture](#architecture)
-   [Contributing](#contributing)
-   [Miscellaneous](#miscellaneous)
    -   [Related Resources](#related-resources)
    -   [External Resources](#external-resources)
-   [License](#license)

## Overview

**SilentVerify** is a post-quantum cryptographic solution that binds blockchain state to signed certificates using the **Oil-and-Vinegar (UOV)** signature scheme. This Next.js client serves as the public-facing interface for the protocol, offering:

-   **Interactive explainer** — understand Oil-and-Vinegar duality and state certificates
-   **Visual flow diagrams** — see how signing, verification, and cross-chain flows work
-   **Pricing / feature breakdown** — learn about different integration tiers
-   **Production-ready UI** — built with modern design patterns (Tailwind CSS, React 19, TypeScript)

## Getting Started

### Prerequisites

-   **Node.js** 18+
-   **Yarn** 1.x (classic)
-   **Python** 3.11+

### Installation

```bash
# Install JS dependencies
yarn install  # or: yarn
```

### Configuration

Create a `.env` file in the root of the `client/` folder:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5173
NEXT_PUBLIC_OPENAPI_URL=${NEXT_PUBLIC_API_URL}/openapi.json
NEXT_PUBLIC_APP_NAME=
NEXT_PUBLIC_APP_ENV=                        # dev | staging | prod
```

### Development

Start the development server:

```bash
yarn dev           # client + server
yarn client        # client only
yarn server        # server only
```

Open [http://localhost:3000](http://localhost:3000) in your browser. Pages auto-refresh as you edit.

## Project Structure

```
.
├── app
├── api
├── components/
│   ├── blocks
│   ├── layout
│   └── ui
├── hooks
├── lib
├── public
├── stores
├── styles
├── types
└── utils/
    ├── constants
    └── functions
```

## Architecture

-   **Framework:** [Next.js](https://nextjs.org) 16.2.6 with [React](https://react.dev) 19.2.4
-   **Language:** TypeScript 5
-   **Styling:**
    -   [Tailwind CSS](https://tailwindcss.com) 4 with PostCSS
    -   [Class Variance Authority](https://cva.style) for component variants
    -   [Tailwind Merge](https://github.com/dcastil-stripe/tailwind-merge) for smart class composition
-   **Icons:**
    -   [Lucide React](https://lucide.dev) 1.3.0 (primary icon library)
    -   [@icons-pack/react-simple-icons](https://www.npmjs.com/package/@icons-pack/react-simple-icons) 13.13.0
-   **UI Components:**
    -   [@base-ui/react](https://base-ui.com) 1.5.0 (unstyled, accessible headless components)
    -   `clsx` 2.1.1 (conditional class composition)
-   **Font:** DM Sans from Google Fonts (optimized via `next/font`)

## Contributing

1. Fork the repository
2. Create a feature branch from `ayomide/dev` (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'your message'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request targeting `ayomide/dev`

## Miscellaneous

### Related Resources

-   **UOVscheme Lean formalization:** [../../UOVscheme/](../../UOVscheme/)
-   **Python implementation:** [../../impl/python/](../../impl/python/)
-   **Smart contracts:** [../../contracts/](../../contracts/)
-   **WASM module:** [../../web/uov-wasm/](../../web/uov-wasm/)
-   **Static site:** [../../web/](../../web/)
-   **Solana program:** [../../programs/silentverify/](../../programs/silentverify/)
-   **Main README:** [../../README.md](../../README.md)

### External Resources

-   [Next.js Documentation](https://nextjs.org/docs)
-   [React 19 Documentation](https://react.dev)
-   [Tailwind CSS v4](https://tailwindcss.com/docs)
-   [TypeScript](https://www.typescriptlang.org/docs)
-   [Oil-and-Vinegar Signature Scheme](https://en.wikipedia.org/wiki/Oil_and_vinegar)

## License

Same as the parent repository (see [LICENSE](../../LICENSE)).
