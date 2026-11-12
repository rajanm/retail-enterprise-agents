# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Google Cloud Customer Engineers (CEs) and retail account teams presenting and demoing Gemini Enterprise Agents to retail customers during executive briefings, discovery workshops, and technical evaluations.

## Product Purpose

Provide a static web showcase portal (`index.html`) and standalone agent demo players (`demos/gemini-enterprise/<domain>/<agent>.html`) for the 100 Google ADK agents built for Gemini Enterprise across 9 retail business domains. The portal enables account teams to search agents, inspect KPIs and architecture tiers, explore Day-in-the-Life persona workflows, and launch 1080p recorded multi-turn demos instantaneously.

## Positioning

A unified 100-agent enterprise retail showcase organized from two complementary lenses — by retail business domain (9 domains, 300+ BigQuery tables, multi-region Cloud/ADK deployment) and by retail role/persona (10 persona archetypes with 5-state task bundles and interactive Before/After storyboards) — backed by declarative YAML ADK agents and live recorded walkthroughs.

## Operating Context

- **Scope**: Governs the showcase portal (`index.html`, `_shared/scripts/generate_portal_site.py`, `_shared/scripts/persona_catalog.py`) and standalone demo players (`_shared/scripts/generate_demo_html.py`, `demos/gemini-enterprise/**/*.html`).
- **Build & Hosting**: Compiled from Python generator scripts into standalone static HTML/CSS/JS and served via GitHub Pages (with `.nojekyll` at the repository root).
- **Development Workflow**: Portal updates are built and verified locally across viewports and themes inside isolated `.worktrees/` branches without altering agent definitions (`domains/**`), templates (`_shared/templates/**`), or recorded `.mp4` assets.

## Capabilities and Constraints

- **Static GitHub Pages output**: Must remain zero-bundler static HTML/CSS/JS (no Node/Vite/Next runtime required to host).
- **Generator-driven source of truth**: Structural and content changes belong in `_shared/scripts/generate_portal_site.py`, `_shared/scripts/persona_catalog.py`, and `_shared/scripts/generate_demo_html.py`, then recompiled into `index.html` and demo HTML files.
- **Dual browsing modes**: Supports "Browse by Domain" (live search, domain filter tabs, KPI cards, Architecture Blueprint modal, video modal) and "Browse by Persona" (10 retail personas, 5-state task bundle filters, Before/After storyboard, Connected Orchestration Conduit, Stage Focus Theater).
- **Persona View framing rules**: Use high-level horizon labels (`Weeks → Hours`, `Days → Minutes`, `Hours → Minutes`, `Stage 1`–`Stage 4`) and qualitative splits rather than specific numeric time savings or automation percentages; omit `"Autonomous"` and `"AI Co-Pilot"` from 5-state task bundle legend copy.
- **Link & video conventions**: Demo HTML players start playback at `00:10` (`#t=10` with seeking guard); footer documentation links target repository blob URLs in the same tab.
- **Security & hygiene**: Never include real GCP project IDs, service account emails, keys, or credentials in committed UI files or configs.

## Brand Commitments

- **Official Branding**: Title is `Gemini Enterprise Agents for Retail`; subtitle is `Google ADK & Gemini Enterprise Multi-Agent Swarm`.
- **Google-only ecosystem positioning**: Strictly Google Cloud, Google ADK, Gemini Enterprise, and BigQuery Conversational Analytics branding — never reference external third-party AI companies in UI text, comments, or documentation.
- **Theme persistence**: Supports dark and light themes persisted in `localStorage` (`retail_agents_theme`).

## Evidence on Hand

- `index.html`: Compiled single-page catalog featuring 100 agents across 9 domains and 10 persona workflows.
- `demos/gemini-enterprise/<domain>/<agent>.html` & `.mp4`: 100 standalone 1080p recorded multi-turn agent demos (BigQuery data insights, Google Search market grounding, visual chart generation).
- `domains/<domain>/agents/<agent>/README.md`: Source documentation providing each agent's business problem statement, tracked KPIs, and curated Q&A examples.
- `ARCHITECTURE.md` & `_shared/table_registry.yaml`: Domain footprint and multi-region deployment metadata.

## Product Principles

1. **Demo-ready clarity**: Keep search, filtering, persona walkthroughs, and 1080p video modals fast, scannable, and reliable during live customer meetings.
2. **Single-source generation**: Derive catalog cards, KPIs, and demo links from Python generators and agent metadata rather than duplicating content manually.
3. **Qualitative workflow truth**: Frame agent impact around task transformation horizons and concrete capabilities without inventing ROI metrics or automation percentages.
4. **Zero-dependency static resilience**: Ship self-contained static HTML that renders reliably on GitHub Pages without external build pipelines.

## Accessibility & Inclusion

Target **WCAG 2.2 AA** compliance across both dark and light themes, including sufficient text/surface contrast, keyboard accessibility for tabs, modals, and filters, visible focus indicators, and responsive support across desktop and mobile viewports.
