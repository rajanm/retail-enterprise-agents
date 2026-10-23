#!/usr/bin/env python3
"""
generate_portal_site.py — Retail Enterprise Agents Portal Generator

Programmatically reads _shared/table_registry.yaml and all agent READMEs across 9 domains
to generate a self-contained, lightning-fast, interactive single-page portal (index.html)
for GitHub Pages with live search, domain filtering, persona filtering, Day-in-the-Life
storyboards, KPI tags, prompt previews, architecture modal, and embedded 1080p video modal
players with dual light/dark themes.

Usage:
    uv run python _shared/scripts/generate_portal_site.py
"""

import html
import json
from pathlib import Path
import re
import sys
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from _shared.scripts.prompt_parser import parse_agent_prompts
from _shared.scripts.persona_catalog import (
    PERSONA_ARCHETYPES,
    PERSONA_ORDER,
    build_agent_transformation,
    classify_persona_archetype,
    extract_personas_from_readme,
)

__all__ = [
    "DOMAIN_DISPLAY_NAMES",
    "DOMAIN_ICONS",
    "DOMAIN_ORDER",
    "PERSONA_ARCHETYPES",
    "PERSONA_ORDER",
    "build_portal_html",
    "classify_persona_archetype",
    "extract_agent_metadata",
    "main",
]

DOMAIN_ICONS = {
    "merchandising": "🛍️",
    "supply_chain": "🚚",
    "store_operations": "🏬",
    "e_commerce": "🛒",
    "marketing": "📊",
    "finance": "💰",
    "customer_care": "🎧",
    "sustainability_compliance": "🌱",
    "human_resources": "👥",
}

DOMAIN_DISPLAY_NAMES = {
    "merchandising": "Merchandising",
    "supply_chain": "Supply Chain & Logistics",
    "store_operations": "Store Operations",
    "e_commerce": "E-Commerce & Digital",
    "marketing": "Marketing & Retail Media",
    "finance": "Finance, Real Estate & Accounting",
    "customer_care": "Customer Care & Experience",
    "sustainability_compliance": "Sustainability, ESG & Compliance",
    "human_resources": "Human Resources & Workforce",
}

DOMAIN_ORDER = [
    "merchandising",
    "supply_chain",
    "store_operations",
    "e_commerce",
    "marketing",
    "finance",
    "customer_care",
    "sustainability_compliance",
    "human_resources",
]


def extract_agent_metadata(agent_name: str, domain: str, reg_agent: dict, repo_root: Path) -> dict:
    """Extracts rich metadata, KPIs, prompts, personas, and transformations for an agent from its README.md."""
    readme_path = repo_root / "domains" / domain / "agents" / agent_name / "README.md"
    
    display_name = reg_agent.get("display_name", agent_name.replace("_", " ").title())
    location = reg_agent.get("location", "us-central1")
    tables = reg_agent.get("tables", [])
    
    description = f"Autonomous enterprise reasoning agent for {display_name} in retail operations."
    kpis = []
    prompts = []
    
    readme_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    if readme_content:
        content = readme_content
        
        # 1. Extract Description from Business Problem or Why This Agent Matters
        bp_match = re.search(r"###\s+Business Problem\s*\n+(.*?)(?=\n\s*###|\n\s*##|\n\s*---|\Z)", content, re.DOTALL)
        if bp_match:
            text = bp_match.group(1).strip()
            lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
            if lines:
                cleaned = " ".join(lines)
                cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cleaned).replace("**", "").replace("*", "").strip()
                if len(cleaned) > 20:
                    description = cleaned
        elif "Why This Agent Matters" in content:
            why_match = re.search(r"##\s+(?:1\.\s+)?Why This Agent Matters\s*\n+(.*?)(?=\n\s*###|\n\s*##|\n\s*---|\Z)", content, re.DOTALL)
            if why_match:
                text = why_match.group(1).strip()
                lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
                if lines:
                    cleaned = " ".join(lines)
                    cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cleaned).replace("**", "").replace("*", "").strip()
                    if len(cleaned) > 20:
                        description = cleaned
        else:
            # Fallback to paragraph before first section
            ans_match = re.search(r"^(Answers questions about.*?)(?=\n\s*\n|\n\s*#|\Z)", content, re.DOTALL | re.MULTILINE)
            if ans_match:
                cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", ans_match.group(1).strip()).replace("**", "").replace("*", "").strip()
                if len(cleaned) > 20:
                    description = cleaned
                    
        # 2. Extract KPIs from KPI table
        kpi_table_match = re.search(r"\|\s*Metric\s*\|\s*Definition\s*\|\s*Target\s*\|.*?\n((?:\|.*?\n)+)", content, re.IGNORECASE)
        if kpi_table_match:
            rows = kpi_table_match.group(1).strip().split("\n")
            for row in rows:
                cols = [c.strip() for c in row.split("|")[1:-1]]
                if len(cols) >= 3 and cols[0] and not cols[0].startswith("---") and cols[0] != ":---":
                    metric_name = cols[0].replace("**", "").strip()
                    target = cols[2].replace("**", "").strip()
                    if metric_name and target:
                        kpis.append(f"{metric_name}: {target}")
                    elif metric_name:
                        kpis.append(metric_name)
                    if len(kpis) >= 4:
                        break
                        
        # 3. Extract Prompts
        try:
            prompts = parse_agent_prompts(readme_path)
        except Exception:
            prompts = [
                f"What are our key performance metrics for {display_name} across store regions in 2026 YTD?",
                f"What are current retail industry benchmarks and best practices for {display_name}?",
                f"Show me a visual chart comparing our {display_name} performance vs annual target."
            ]
    else:
        prompts = [
            f"What are our key performance metrics for {display_name} across store regions in 2026 YTD?",
            f"What are current retail industry benchmarks and best practices for {display_name}?",
            f"Show me a visual chart comparing our {display_name} performance vs annual target."
        ]
        
    personas = extract_personas_from_readme(readme_content, display_name, domain, kpis, tables)
    persona_archetypes = [pid for pid in PERSONA_ORDER if any(p["archetype"] == pid for p in personas)]
    for arch in PERSONA_ARCHETYPES:
        arch_id = arch["id"]
        if arch_id not in persona_archetypes:
            for stage in arch.get("day_in_the_life", []):
                if agent_name in stage.get("featured_agents", []):
                    persona_archetypes.append(arch_id)
                    break
    persona_archetypes = [pid for pid in PERSONA_ORDER if pid in persona_archetypes]
    if not persona_archetypes:
        persona_archetypes = [classify_persona_archetype(display_name, domain)]
    transformation = build_agent_transformation(display_name, domain, description, personas, kpis, tables)
    
    demo_html_rel = f"demos/gemini-enterprise/{domain}/{agent_name}.html"
    demo_mp4_rel = f"demos/gemini-enterprise/{domain}/{agent_name}.mp4"
    readme_rel = f"domains/{domain}/{agents_dir_rel(domain, agent_name)}"
    
    return {
        "id": reg_agent.get("agent_id", ""),
        "name": agent_name,
        "display_name": display_name,
        "domain": domain,
        "domain_display": DOMAIN_DISPLAY_NAMES.get(domain, domain.title()),
        "icon": DOMAIN_ICONS.get(domain, "🤖"),
        "location": location,
        "description": description,
        "kpis": kpis[:4],
        "prompts": prompts[:3],
        "tables": tables,
        "personas": personas,
        "persona_archetypes": persona_archetypes,
        "transformation": transformation,
        "demo_html": demo_html_rel,
        "demo_mp4": demo_mp4_rel,
        "readme": readme_rel,
    }


def agents_dir_rel(domain: str, agent_name: str) -> str:
    return f"agents/{agent_name}/README.md"


def build_portal_html(agents_data: list[dict], domains_data: dict) -> str:
    """Generates the complete index.html file with Domain and Persona catalog views."""
    
    total_agents = len(agents_data)
    total_domains = len(DOMAIN_ORDER)
    total_tables = sum(len(a.get("tables", [])) for a in agents_data)
    
    # Pre-count agents per domain
    domain_counts = {}
    for a in agents_data:
        d = a["domain"]
        domain_counts[d] = domain_counts.get(d, 0) + 1

    # Pre-count agents per persona archetype
    persona_counts = {}
    for a in agents_data:
        for pid in a.get("persona_archetypes", []):
            persona_counts[pid] = persona_counts.get(pid, 0) + 1
    personas_json = json.dumps(PERSONA_ARCHETYPES, indent=2)
        
    agents_json = json.dumps(agents_data, indent=2)
    
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini Enterprise Agents for Retail — 100 Multi-Agent Catalog</title>
  <meta name="description" content="Explore 100 specialized Gemini Enterprise Agents for retail enterprise operations, built on Google ADK, Gemini Enterprise, and BigQuery Conversational Analytics.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  
  <script>
    // Synchronous theme initialization to prevent Flash of Unstyled Content (FOUC)
    (function() {{
      const savedTheme = localStorage.getItem('retail_agents_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', savedTheme);
    }})();
  </script>

  <style>
    :root, [data-theme="dark"] {{
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --bg-card: #1e293b;
      --bg-card-hover: #243248;
      --bg-surface: #0f172a;
      --bg-input: #0f172a;
      --border-color: #334155;
      --border-faint: rgba(255, 255, 255, 0.14);
      --border-subtle: #1e293b;
      --border-focus: #38bdf8;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --accent-blue: #38bdf8;
      --accent-blue-hover: #0284c7;
      --accent-indigo: #818cf8;
      --accent-emerald: #34d399;
      --accent-amber: #fbbf24;
      --badge-bg: rgba(56, 189, 248, 0.12);
      --badge-border: rgba(56, 189, 248, 0.28);
      --badge-text: #38bdf8;
      --kpi-bg: rgba(52, 211, 153, 0.1);
      --kpi-border: rgba(52, 211, 153, 0.25);
      --kpi-text: #34d399;
      --region-bg: rgba(129, 140, 248, 0.12);
      --region-border: rgba(129, 140, 248, 0.28);
      --region-text: #a5b4fc;
      --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
      --shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      --modal-overlay: rgba(15, 23, 42, 0.85);

      --without-bg: rgba(244, 63, 94, 0.10);
      --without-border: rgba(244, 63, 94, 0.30);
      --without-text: #fda4af;
      --with-bg: rgba(52, 211, 153, 0.10);
      --with-border: rgba(52, 211, 153, 0.30);
      --with-text: #6ee7b7;
      --aug-bg: rgba(129, 140, 248, 0.12);
      --aug-border: rgba(129, 140, 248, 0.30);
      --aug-text: #a5b4fc;
      --persona-pill-bg: rgba(168, 85, 247, 0.12);
      --persona-pill-border: rgba(168, 85, 247, 0.28);
      --persona-pill-text: #d8b4fe;

      /* 5-State Task Bundle Tokens (Dark Theme) */
      --task-unchanged-bg: rgba(148, 163, 184, 0.12);
      --task-unchanged-border: rgba(148, 163, 184, 0.35);
      --task-unchanged-text: #e2e8f0;
      --task-unchanged-dot: #94a3b8;

      --task-augmented-bg: rgba(168, 85, 247, 0.16);
      --task-augmented-border: rgba(192, 132, 252, 0.55);
      --task-augmented-text: #f3e8ff;
      --task-augmented-dot: #c084fc;
      --task-augmented-stack-1: rgba(168, 85, 247, 0.28);
      --task-augmented-stack-2: rgba(168, 85, 247, 0.14);

      --task-automated-bg: rgba(56, 189, 248, 0.16);
      --task-automated-border: rgba(56, 189, 248, 0.55);
      --task-automated-text: #e0f2fe;
      --task-automated-dot: #38bdf8;
      --task-automated-stack-1: rgba(56, 189, 248, 0.28);
      --task-automated-stack-2: rgba(56, 189, 248, 0.14);

      --task-new-bg: rgba(251, 191, 36, 0.16);
      --task-new-border: rgba(251, 191, 36, 0.55);
      --task-new-text: #fef3c7;
      --task-new-dot: #fbbf24;

      --task-retired-bg: rgba(148, 163, 184, 0.04);
      --task-retired-border: rgba(148, 163, 184, 0.24);
      --task-retired-text: #64748b;
      --task-retired-dot: #64748b;
    }}

    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --bg-card-hover: #f8fafc;
      --bg-surface: #f1f5f9;
      --bg-input: #ffffff;
      --border-color: #cbd5e1;
      --border-faint: #cbd5e1;
      --border-subtle: #e2e8f0;
      --border-focus: #0284c7;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --accent-blue: #0284c7;
      --accent-blue-hover: #0369a1;
      --accent-indigo: #6366f1;
      --accent-emerald: #059669;
      --accent-amber: #d97706;
      --badge-bg: #e0f2fe;
      --badge-border: #bae6fd;
      --badge-text: #0284c7;
      --kpi-bg: #d1fae5;
      --kpi-border: #a7f3d0;
      --kpi-text: #065f46;
      --region-bg: #e0e7ff;
      --region-border: #c7d2fe;
      --region-text: #4338ca;
      --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      --modal-overlay: rgba(15, 23, 42, 0.6);

      --without-bg: #fff1f2;
      --without-border: #fecdd3;
      --without-text: #be123c;
      --with-bg: #ecfdf5;
      --with-border: #a7f3d0;
      --with-text: #047857;
      --aug-bg: #eef2ff;
      --aug-border: #c7d2fe;
      --aug-text: #4338ca;
      --persona-pill-bg: #f3e8ff;
      --persona-pill-border: #d8b4fe;
      --persona-pill-text: #6b21a8;

      /* 5-State Task Bundle Tokens (Light Theme) */
      --task-unchanged-bg: #edeae2;
      --task-unchanged-border: #c7c2b6;
      --task-unchanged-text: #3f3d37;
      --task-unchanged-dot: #8c8577;

      --task-augmented-bg: #f3e8ff;
      --task-augmented-border: #9333ea;
      --task-augmented-text: #581c87;
      --task-augmented-dot: #9333ea;
      --task-augmented-stack-1: rgba(147, 51, 234, 0.22);
      --task-augmented-stack-2: rgba(147, 51, 234, 0.11);

      --task-automated-bg: #e0f2fe;
      --task-automated-border: #0284c7;
      --task-automated-text: #0c4a6e;
      --task-automated-dot: #0284c7;
      --task-automated-stack-1: rgba(2, 132, 199, 0.22);
      --task-automated-stack-2: rgba(2, 132, 199, 0.11);

      --task-new-bg: #fef3c7;
      --task-new-border: #d97706;
      --task-new-text: #78350f;
      --task-new-dot: #d97706;

      --task-retired-bg: #f4f3ee;
      --task-retired-border: #c4bfb3;
      --task-retired-text: #78716c;
      --task-retired-dot: #a8a29e;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    /* Global Header */
    .site-header {{
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 40;
      backdrop-filter: blur(8px);
    }}

    .header-inner {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}

    .brand-logo {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-primary);
    }}

    .brand-icon {{
      font-size: 1.6rem;
      line-height: 1;
    }}

    .brand-text {{
      display: flex;
      flex-direction: column;
    }}

    .brand-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--text-primary);
    }}

    .brand-subtitle {{
      font-size: 0.75rem;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .btn-header {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-primary);
      transition: all 0.15s ease;
    }}

    .btn-header:hover {{
      background: var(--bg-surface);
      border-color: var(--border-focus);
      color: var(--accent-blue);
    }}

    .btn-primary-header {{
      background: var(--accent-blue);
      color: #0f172a !important;
      border-color: var(--accent-blue);
      font-weight: 700;
    }}

    .btn-primary-header:hover {{
      background: var(--accent-blue-hover);
      border-color: var(--accent-blue-hover);
      color: #ffffff !important;
    }}

    /* Hero Section */
    .hero {{
      padding: 48px 24px 32px;
      max-width: 1360px;
      margin: 0 auto;
      width: 100%;
      text-align: center;
    }}

    .hero-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--accent-blue);
      margin-bottom: 16px;
    }}

    .hero-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 2.5rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 12px;
      color: var(--text-primary);
    }}

    .hero-title span {{
      background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .hero-desc {{
      max-width: 820px;
      margin: 0 auto 28px;
      font-size: 1.05rem;
      color: var(--text-secondary);
      line-height: 1.6;
    }}

    /* Stat Counters */
    .stat-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      max-width: 1080px;
      margin: 0 auto;
    }}

    .stat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 12px;
      padding: 12px 10px;
      text-align: center;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .stat-card:hover {{
      transform: translateY(-2px);
      border-color: var(--border-focus);
    }}

    .stat-number {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 2px;
    }}

    .stat-label {{
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      line-height: 1.35;
      color: var(--text-muted);
    }}

    /* Main Container */
    .main-container {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 24px;
      width: 100%;
      flex: 1;
    }}

    /* Search & Filter Toolbar */
    .toolbar {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-faint);
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 28px;
      box-shadow: var(--shadow-card);
    }}

    .search-row {{
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
      position: relative;
    }}

    .search-input-wrapper {{
      position: relative;
      flex: 1;
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 1rem;
      pointer-events: none;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-input);
      border: 1px solid var(--border-faint);
      border-radius: 10px;
      padding: 12px 14px 12px 42px;
      font-size: 0.95rem;
      color: var(--text-primary);
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}

    .search-input:focus {{
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }}

    .search-clear {{
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 1rem;
      padding: 4px;
      display: none;
    }}

    .search-clear:hover {{
      color: var(--text-primary);
    }}

    /* View Mode Bar */
    .view-mode-bar {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 16px;
    }}

    .view-mode-toggle {{
      display: inline-flex;
      background: var(--bg-surface);
      padding: 4px;
      border-radius: 12px;
      border: 1px solid var(--border-faint);
      width: fit-content;
      gap: 4px;
    }}

    .view-mode-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 18px;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .view-mode-btn:hover {{
      color: var(--text-primary);
    }}

    .view-mode-btn.active {{
      background: var(--accent-blue);
      color: #0f172a;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
    }}

    .view-mode-btn.active .domain-count {{
      background: rgba(15, 23, 42, 0.25);
      color: #0f172a;
    }}

    .view-mode-hint {{
      font-size: 0.8rem;
      color: var(--text-muted);
      font-style: italic;
    }}

    /* Domain Tabs */
    .domain-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .domain-btn {{
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
      color: var(--text-secondary);
      padding: 8px 14px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .domain-btn:hover {{
      color: var(--text-primary);
      border-color: var(--border-focus);
    }}

    .domain-btn.active {{
      background: var(--accent-blue);
      color: #0f172a;
      border-color: var(--accent-blue);
      font-weight: 700;
    }}

    .domain-count {{
      font-size: 0.72rem;
      padding: 2px 6px;
      border-radius: 9999px;
      background: rgba(0, 0, 0, 0.15);
      font-family: 'JetBrains Mono', monospace;
    }}

    .domain-btn.active .domain-count {{
      background: rgba(15, 23, 42, 0.25);
      color: #0f172a;
    }}

    /* Persona Tabs */
    .persona-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .persona-btn {{
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
      color: var(--text-secondary);
      padding: 8px 14px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .persona-btn:hover {{
      color: var(--text-primary);
      border-color: var(--border-focus);
    }}

    .persona-btn.active {{
      background: var(--accent-indigo);
      color: #ffffff;
      border-color: var(--accent-indigo);
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(129, 140, 248, 0.35);
    }}

    .persona-btn.active .domain-count {{
      background: rgba(0, 0, 0, 0.25);
      color: #ffffff;
    }}

    /* Persona Experience Container & Overview Grid */
    #personaExperienceContainer {{
      margin-bottom: 28px;
    }}

    .persona-overview-header {{
      margin-bottom: 18px;
    }}

    .persona-overview-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.45rem;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 4px;
    }}

    .persona-overview-subtitle {{
      font-size: 0.9rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }}

    .persona-overview-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 18px;
    }}

    .persona-overview-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-card);
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
      position: relative;
    }}

    .persona-overview-card:hover {{
      transform: translateY(-3px);
      border-color: var(--border-focus);
      box-shadow: 0 14px 28px -6px rgba(0, 0, 0, 0.35);
    }}

    .persona-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
    }}

    .persona-card-title-wrap {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .persona-card-icon {{
      font-size: 1.6rem;
      line-height: 1;
    }}

    .persona-card-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .persona-agent-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--persona-pill-bg);
      border: 1px solid var(--persona-pill-border);
      color: var(--persona-pill-text);
      font-family: 'JetBrains Mono', monospace;
      white-space: nowrap;
    }}

    .persona-card-subtitle {{
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--accent-blue);
      margin-bottom: 6px;
    }}

    .persona-card-summary {{
      font-size: 0.82rem;
      color: var(--text-secondary);
      line-height: 1.45;
      margin-bottom: 14px;
      flex: 1;
    }}

    .persona-metrics-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 14px;
      padding: 8px 12px;
      background: var(--bg-surface);
      border-radius: 8px;
      border: 1px solid var(--border-faint);
    }}

    .persona-metric-pill {{
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text-primary);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .persona-metric-pill strong {{
      color: var(--accent-emerald);
    }}

    .auto-aug-bar-container {{
      margin-bottom: 16px;
    }}

    .auto-aug-legend {{
      display: flex;
      justify-content: space-between;
      font-size: 0.74rem;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text-secondary);
    }}

    .auto-aug-legend .auto-text {{
      color: var(--accent-emerald);
    }}

    .auto-aug-legend .aug-text {{
      color: var(--accent-indigo);
    }}

    .auto-aug-bar {{
      display: flex;
      height: 8px;
      border-radius: 9999px;
      overflow: hidden;
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
    }}

    .auto-fill-bar {{
      height: 100%;
      background: var(--accent-emerald);
      transition: width 0.6s ease-out;
    }}

    .aug-fill-bar {{
      height: 100%;
      background: var(--accent-indigo);
      transition: width 0.6s ease-out;
    }}

    /* 5-State Task Bundle Legend Key & 5-Segment Distribution Bar */
    .task-bundle-key-bar {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 10px;
      padding: 10px 14px;
      margin-top: 12px;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .task-bundle-key-title {{
      font-size: 0.76rem;
      font-weight: 700;
      color: var(--text-primary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .task-bundle-key-items {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}

    .task-bundle-key-chip {{
      font-size: 0.72rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      line-height: 1.2;
    }}

    .task-bundle-key-chip.key-unchanged {{
      background: var(--task-unchanged-bg);
      border: 1px solid var(--task-unchanged-border);
      color: var(--task-unchanged-text);
    }}

    .task-bundle-key-chip.key-augmented {{
      background: var(--task-augmented-bg);
      border: 1px solid var(--task-augmented-border);
      color: var(--task-augmented-text);
    }}

    .task-bundle-key-chip.key-automated {{
      background: var(--task-automated-bg);
      border: 1px solid var(--task-automated-border);
      color: var(--task-automated-text);
    }}

    .task-bundle-key-chip.key-new {{
      background: var(--task-new-bg);
      border: 1px solid var(--task-new-border);
      color: var(--task-new-text);
    }}

    .task-bundle-key-chip.key-retired {{
      background: var(--task-retired-bg);
      border: 1px solid var(--task-retired-border);
      color: var(--task-retired-text);
    }}

    .task-dist-container {{
      margin-bottom: 16px;
    }}

    .task-dist-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 0.70rem;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text-secondary);
      flex-wrap: wrap;
      gap: 4px;
    }}

    .task-dist-bar {{
      display: flex;
      height: 8px;
      border-radius: 9999px;
      overflow: hidden;
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
    }}

    .task-dist-bar .seg-unchanged {{
      background: var(--task-unchanged-border);
      height: 100%;
    }}

    .task-dist-bar .seg-augmented {{
      background: var(--task-augmented-border);
      height: 100%;
    }}

    .task-dist-bar .seg-automated {{
      background: var(--task-automated-border);
      height: 100%;
    }}

    .task-dist-bar .seg-new {{
      background: var(--task-new-border);
      height: 100%;
    }}

    .task-dist-bar .seg-retired {{
      background: var(--task-retired-border);
      height: 100%;
    }}

    .btn-persona-cta {{
      width: 100%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: var(--bg-surface);
      color: var(--text-primary);
      padding: 9px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      border: 1px solid var(--border-color);
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .btn-persona-cta:hover {{
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #0f172a;
      transform: translateY(-1px);
    }}

    /* Day in the Life Storyboard */
    .ditl-banner {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 16px;
      padding: 24px;
      box-shadow: var(--shadow-card);
      margin-bottom: 20px;
    }}

    .ditl-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}

    .ditl-header-left {{
      flex: 1;
      min-width: 280px;
    }}

    .ditl-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .ditl-subtitle {{
      font-size: 0.88rem;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }}

    .ditl-stat-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .ditl-stat-pill {{
      font-size: 0.76rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 9999px;
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
      color: var(--text-primary);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .ditl-header-right {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}

    .ditl-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 14px;
    }}

    @media (max-width: 900px) {{
      .ditl-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .ditl-stage-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .ditl-stage-card:hover {{
      border-color: var(--border-focus);
    }}

    .ditl-stage-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }}

    .ditl-time-stage {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .ditl-mode-badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .ditl-mode-badge.automated {{
      background: var(--with-bg);
      border: 1px solid var(--with-border);
      color: var(--with-text);
    }}

    .ditl-mode-badge.augmented {{
      background: var(--aug-bg);
      border: 1px solid var(--aug-border);
      color: var(--aug-text);
    }}

    .ditl-compare-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}

    @media (max-width: 600px) {{
      .ditl-compare-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .ditl-without {{
      background: var(--without-bg);
      border: 1px solid var(--without-border);
      color: var(--without-text);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 0.8rem;
      line-height: 1.45;
    }}

    .ditl-with {{
      background: var(--with-bg);
      border: 1px solid var(--with-border);
      color: var(--with-text);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 0.8rem;
      line-height: 1.45;
    }}

    .ditl-compare-header {{
      font-weight: 700;
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .ditl-time-tag,
    .ditl-time-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      opacity: 0.9;
    }}

    .ditl-split-box {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 0.78rem;
      line-height: 1.45;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .ditl-split-box strong {{
      color: var(--text-primary);
    }}

    .ditl-agent-chips {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      align-items: center;
      padding-top: 4px;
    }}

    .ditl-agent-chips-label {{
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .ditl-agent-chip {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 4px 9px;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .ditl-agent-chip:hover {{
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #0f172a;
      transform: translateY(-1px);
    }}

    /* 2-State Switcher Controls Bar */
    .ditl-controls-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--border-faint);
      flex-wrap: wrap;
    }}

    .ditl-state-switcher {{
      display: inline-flex;
      background: var(--bg-surface);
      border: 1.5px solid var(--border-color);
      border-radius: 10px;
      padding: 3px;
      gap: 4px;
    }}

    .ditl-state-btn {{
      padding: 7px 14px;
      border-radius: 8px;
      border: 1.5px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-secondary);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .ditl-state-btn:hover {{
      color: var(--text-primary);
      transform: translateY(-1px);
      border-color: var(--border-focus);
    }}

    .ditl-state-btn.active-before {{
      background: #dc2626 !important;
      border-color: #b91c1c !important;
      color: #ffffff !important;
      font-weight: 700;
      box-shadow: 0 4px 12px rgba(220, 38, 38, 0.28);
    }}

    .ditl-state-btn.active-after {{
      background: #10b981 !important;
      border-color: #059669 !important;
      color: #ffffff !important;
      font-weight: 700;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.30);
    }}

    .mode-radio-dot {{
      font-size: 0.85rem;
      line-height: 1;
    }}

    /* Interactive 5-State Filter Pills */
    .ditl-state-filter-pill {{
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
      border-width: 1.5px !important;
      user-select: none;
    }}

    .ditl-state-filter-pill:hover {{
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
    }}

    .ditl-state-filter-pill.active-filter {{
      border-width: 2px !important;
      font-weight: 800 !important;
      transform: translateY(-2px);
      box-shadow: 0 0 0 3px var(--border-focus), 0 6px 14px rgba(0, 0, 0, 0.18) !important;
    }}

    .pill-check-ind {{
      font-size: 0.72rem;
      font-weight: 800;
      margin-right: 2px;
    }}

    .filter-reset-pill {{
      font-size: 0.70rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      cursor: pointer;
      font-family: inherit;
      transition: all 0.15s ease;
    }}

    .filter-reset-pill:hover {{
      background: var(--without-bg);
      border-color: var(--without-border);
      color: var(--without-text);
    }}

    .ditl-stage-top-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .stage-maximize-btn {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 9px;
      border-radius: 6px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.15s ease;
    }}

    .stage-maximize-btn:hover {{
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #0f172a;
      transform: translateY(-1px);
    }}

    .ditl-stage-horizon {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.74rem;
      font-weight: 700;
      padding: 4px 9px;
      border-radius: 6px;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--badge-text);
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .ditl-stage-horizon.manual-mode {{
      background: var(--without-bg);
      border-color: var(--without-border);
      color: var(--without-text);
    }}

    /* 3×2 Task-Bundle Grid */
    .task-bundle-wrap {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .task-bundle-title {{
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .task-bundle-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}

    @media (max-width: 900px) {{
      .task-bundle-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 600px) {{
      .task-bundle-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .task-tile {{
      border-radius: 10px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 8px;
      min-height: 88px;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      cursor: pointer;
      outline: none;
    }}

    .task-tile:focus-visible {{
      box-shadow: 0 0 0 2.5px var(--border-focus);
    }}

    .task-tile-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }}

    .task-state-tag {{
      font-size: 0.68rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      line-height: 1.2;
    }}

    .task-step-ref {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.66rem;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.10);
      color: inherit;
      white-space: nowrap;
    }}

    .task-tile-label {{
      font-size: 0.80rem;
      line-height: 1.35;
      font-weight: 600;
    }}

    .task-tile-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.64rem;
      color: var(--text-muted);
      padding-top: 4px;
      border-top: 1px dashed rgba(0, 0, 0, 0.08);
    }}

    .task-pin-chip {{
      font-size: 0.64rem;
      font-weight: 600;
      opacity: 0.75;
    }}

    .task-tile.is-pinned .task-pin-chip {{
      opacity: 1;
      font-weight: 800;
      color: var(--accent-blue);
    }}

    /* Task States */
    .task-tile.state-unchanged {{
      background: var(--task-unchanged-bg);
      border: 1px solid var(--task-unchanged-border);
      color: var(--task-unchanged-text);
    }}

    .task-tile.state-augmented {{
      background: var(--task-augmented-bg);
      border: 1px solid var(--task-augmented-border);
      color: var(--task-augmented-text);
      box-shadow: 0 2px 0 0 var(--task-augmented-stack-1), 0 4px 0 0 var(--task-augmented-stack-2);
    }}

    .task-tile.state-automated {{
      background: var(--task-automated-bg);
      border: 1px solid var(--task-automated-border);
      color: var(--task-automated-text);
      box-shadow: 0 2px 0 0 var(--task-automated-stack-1), 0 4px 0 0 var(--task-automated-stack-2);
    }}

    .task-tile.state-new {{
      background: var(--task-new-bg);
      border: 1px solid var(--task-new-border);
      color: var(--task-new-text);
    }}

    .task-tile.state-retired {{
      background: var(--task-retired-bg);
      border: 1px dashed var(--task-retired-border);
      color: var(--task-retired-text);
      opacity: 0.75;
    }}

    .task-tile.state-retired .task-tile-label {{
      text-decoration: line-through;
    }}

    .task-tile.state-dormant {{
      background: var(--task-retired-bg);
      border: 1px dashed var(--task-retired-border);
      color: var(--task-retired-text);
      opacity: 0.65;
    }}

    /* Prominent Motion Spotlighting & Dimming */
    .motion-spotlight {{
      transform: translateY(-4px) scale(1.03) !important;
      z-index: 6 !important;
      box-shadow: 0 0 0 2.5px var(--border-focus), 0 14px 28px -6px rgba(37, 99, 235, 0.28) !important;
    }}

    .motion-dimmed {{
      opacity: 0.26 !important;
      filter: grayscale(45%);
      transform: scale(0.96);
      pointer-events: auto;
    }}

    /* Motion UI Connected Orchestration Conduit (Metro Timeline) */
    .stage-flow-section {{
      margin-top: 12px;
      padding-top: 14px;
      border-top: 1px solid var(--border-faint);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .stage-flow-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .stage-flow-title {{
      font-size: 0.76rem;
      font-weight: 700;
      color: var(--text-primary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .motion-pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 9999px;
      background: var(--accent-emerald);
      box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
      animation: pulseDot 1.8s infinite;
      display: inline-block;
    }}

    @keyframes pulseDot {{
      0% {{
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
      }}
      70% {{
        box-shadow: 0 0 0 6px rgba(52, 211, 153, 0);
      }}
      100% {{
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0);
      }}
    }}

    .stage-flow-hint {{
      font-size: 0.68rem;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .flow-conduit-track {{
      position: relative;
      display: grid;
      grid-template-columns: repeat(var(--conduit-cols, 3), minmax(0, 1fr));
      gap: 12px;
      padding-top: 4px;
    }}

    @media (max-width: 900px) {{
      .flow-conduit-track {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 600px) {{
      .flow-conduit-track {{
        grid-template-columns: 1fr;
      }}
    }}

    .conduit-rail-line {{
      position: absolute;
      top: 21px;
      left: 24px;
      right: 24px;
      height: 4px;
      background: var(--border-color);
      border-radius: 9999px;
      z-index: 1;
    }}

    .conduit-rail-fill {{
      height: 100%;
      width: 100%;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-indigo));
      border-radius: 9999px;
      transform-origin: left;
    }}

    .conduit-node {{
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      gap: 8px;
      cursor: pointer;
    }}

    .conduit-medallion-row {{
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      height: 38px;
    }}

    .conduit-medallion {{
      width: 36px;
      height: 36px;
      border-radius: 9999px;
      background: var(--bg-card);
      border: 2px solid var(--accent-blue);
      color: var(--accent-blue);
      font-family: 'JetBrains Mono', monospace;
      font-weight: 800;
      font-size: 0.78rem;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
      transition: all 0.2s ease;
      z-index: 3;
    }}

    .conduit-node:hover .conduit-medallion,
    .conduit-node.active-step .conduit-medallion,
    .conduit-medallion.motion-spotlight {{
      background: var(--accent-blue);
      color: #0f172a;
      transform: scale(1.12);
      border-color: #ffffff;
      box-shadow: 0 0 0 3px var(--border-focus), 0 8px 16px rgba(0, 0, 0, 0.25);
    }}

    .conduit-arrow {{
      position: absolute;
      right: -8px;
      font-size: 0.82rem;
      font-weight: 800;
      color: var(--accent-emerald);
      z-index: 3;
    }}

    .conduit-step-card {{
      background: var(--bg-card);
      border: 1.5px solid var(--border-color);
      border-radius: 10px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      flex: 1;
    }}

    .conduit-step-card:hover,
    .conduit-step-card.active-step,
    .conduit-node.active-step .conduit-step-card {{
      background: var(--bg-surface);
      border-color: var(--border-focus);
      transform: translateY(-2px);
      box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.22);
    }}

    .conduit-linked-badge {{
      display: none;
      font-size: 0.62rem;
      font-weight: 800;
      color: var(--accent-emerald);
      background: var(--kpi-bg);
      border: 1px solid var(--kpi-border);
      padding: 2px 5px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .conduit-node.active-step .conduit-linked-badge {{
      display: inline-flex;
    }}

    .flow-bento-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
    }}

    .flow-step-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 9px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }}

    .flow-step-card:hover,
    .flow-step-card.active-step {{
      background: var(--bg-surface);
      border-color: var(--border-focus);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.2);
    }}

    .flow-step-card.active-step {{
      box-shadow: 0 0 0 2px var(--border-focus), 0 6px 14px -2px rgba(0, 0, 0, 0.25);
    }}

    .flow-step-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 4px;
    }}

    .flow-step-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.66rem;
      font-weight: 800;
      color: var(--accent-blue);
      letter-spacing: 0.04em;
    }}

    .flow-demo-pill {{
      font-size: 0.64rem;
      font-weight: 700;
      color: var(--text-muted);
      display: inline-flex;
      align-items: center;
      gap: 2px;
    }}

    .flow-step-action {{
      font-size: 0.74rem;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.3;
    }}

    .flow-connector-tag {{
      color: var(--accent-emerald);
      font-weight: 800;
      font-size: 0.76rem;
    }}

    .flow-step-agent {{
      font-size: 0.71rem;
      font-weight: 500;
      color: var(--text-secondary);
      line-height: 1.32;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .conduit-demo-btn {{
      margin-top: auto;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 6px 8px;
      border-radius: 7px;
      background: var(--bg-surface);
      border: 1.5px solid var(--border-color);
      color: var(--text-primary);
      font-size: 0.70rem;
      font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.15s ease;
      width: 100%;
    }}

    .conduit-demo-btn:hover {{
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #0f172a;
      transform: translateY(-1px);
    }}

    /* Full-Screen Stage Theater Modal */
    .stage-theater-backdrop {{
      z-index: 60;
    }}

    .stage-theater-dialog {{
      max-width: 1440px !important;
      width: 96vw !important;
      max-height: 94vh !important;
      overflow-y: auto;
      background: var(--bg-card);
      border: 1.5px solid var(--border-focus);
      border-radius: 18px;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.45);
      display: flex;
      flex-direction: column;
    }}

    .stage-theater-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
      padding: 16px 24px;
      border-bottom: 1px solid var(--border-color);
      background: var(--bg-secondary);
      position: sticky;
      top: 0;
      z-index: 10;
    }}

    .stage-theater-tabs {{
      display: flex;
      gap: 6px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .theater-stage-tab {{
      padding: 6px 12px;
      border-radius: 8px;
      border: 1.5px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-secondary);
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      white-space: nowrap;
      transition: all 0.15s ease;
    }}

    .theater-stage-tab:hover {{
      color: var(--text-primary);
      border-color: var(--border-focus);
    }}

    .theater-stage-tab.active {{
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #0f172a;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }}

    .stage-theater-body {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    /* Results Header */
    .results-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding: 0 4px;
    }}

    .results-count {{
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .results-count strong {{
      color: var(--text-primary);
    }}

    /* Agent Grid */
    .agent-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(390px, 1fr));
      gap: 20px;
    }}

    .agent-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 14px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-card);
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
      position: relative;
    }}

    .agent-card:hover {{
      transform: translateY(-3px);
      border-color: var(--border-focus);
      box-shadow: 0 14px 30px -8px rgba(0, 0, 0, 0.35);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      gap: 8px;
    }}

    .card-badges {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .badge-domain {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--badge-text);
    }}

    .badge-region {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--region-bg);
      border: 1px solid var(--region-border);
      color: var(--region-text);
      font-family: 'JetBrains Mono', monospace;
    }}

    .card-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 8px;
      line-height: 1.35;
    }}

    .card-desc {{
      font-size: 0.88rem;
      color: var(--text-secondary);
      line-height: 1.5;
      margin-bottom: 16px;
      flex: 1;
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    /* Persona Row & Chips on Agent Card */
    .persona-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 12px;
    }}

    .persona-chip {{
      background: var(--persona-pill-bg);
      border: 1px solid var(--persona-pill-border);
      color: var(--persona-pill-text);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: inherit;
    }}

    .persona-chip:hover {{
      transform: translateY(-1px);
      filter: brightness(1.15);
    }}

    /* Target Persona Spotlight & Transformation Box on Agent Card */
    .card-persona-spotlight {{
      background: var(--bg-surface);
      border: 1px solid var(--persona-pill-border);
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 12px;
    }}

    .card-persona-spotlight-title {{
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--persona-pill-text);
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 6px;
    }}

    .card-persona-spotlight-roles {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 0.78rem;
      color: var(--text-secondary);
      line-height: 1.4;
    }}

    .card-persona-spotlight-roles strong {{
      color: var(--text-primary);
    }}

    .card-transform-box {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .card-transform-without {{
      background: var(--without-bg);
      border: 1px solid var(--without-border);
      color: var(--without-text);
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 0.76rem;
      line-height: 1.4;
    }}

    .card-transform-with {{
      background: var(--with-bg);
      border: 1px solid var(--with-border);
      color: var(--with-text);
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 0.76rem;
      line-height: 1.4;
    }}

    .card-transform-split {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }}

    .card-split-tag {{
      padding: 6px 8px;
      border-radius: 6px;
      font-size: 0.72rem;
      line-height: 1.35;
    }}

    .card-split-tag.auto {{
      background: var(--with-bg);
      border: 1px solid var(--with-border);
      color: var(--with-text);
    }}

    .card-split-tag.aug {{
      background: var(--aug-bg);
      border: 1px solid var(--aug-border);
      color: var(--aug-text);
    }}

    /* KPI Tags */
    .kpi-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 16px;
    }}

    .kpi-pill {{
      font-size: 0.72rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--kpi-bg);
      border: 1px solid var(--kpi-border);
      color: var(--kpi-text);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    /* Prompts Collapsible */
    .prompts-container {{
      border-top: 1px solid var(--border-color);
      padding-top: 12px;
      margin-bottom: 16px;
    }}

    .prompts-toggle {{
      background: none;
      border: none;
      color: var(--text-secondary);
      font-size: 0.78rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      cursor: pointer;
      padding: 2px 0;
    }}

    .prompts-toggle:hover {{
      color: var(--accent-blue);
    }}

    .prompts-list {{
      margin-top: 8px;
      display: none;
      flex-direction: column;
      gap: 6px;
    }}

    .prompts-list.open {{
      display: flex;
    }}

    .prompt-item {{
      font-size: 0.78rem;
      color: var(--text-secondary);
      background: var(--bg-surface);
      padding: 6px 10px;
      border-radius: 6px;
      border-left: 3px solid var(--accent-indigo);
      line-height: 1.4;
      font-style: italic;
    }}

    /* Card Actions */
    .card-actions {{
      display: flex;
      gap: 8px;
      align-items: center;
      margin-top: auto;
      padding-top: 14px;
      border-top: 1px solid var(--border-color);
    }}

    .btn-watch {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: var(--accent-blue);
      color: #0f172a;
      padding: 9px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 700;
      border: none;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .btn-watch:hover {{
      background: var(--accent-blue-hover);
      color: #ffffff;
      transform: translateY(-1px);
    }}

    .btn-showcase {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      background: var(--bg-surface);
      color: var(--text-primary);
      padding: 9px 12px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      text-decoration: none;
      border: 1px solid var(--border-color);
      transition: all 0.15s ease;
    }}

    .btn-showcase:hover {{
      border-color: var(--border-focus);
      color: var(--accent-blue);
    }}

    .btn-doc {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: none;
      color: var(--text-muted);
      padding: 8px;
      border-radius: 8px;
      font-size: 1rem;
      text-decoration: none;
      border: 1px solid transparent;
      transition: all 0.15s ease;
    }}

    .btn-doc:hover {{
      color: var(--text-primary);
      border-color: var(--border-color);
      background: var(--bg-surface);
    }}

    /* No Results State */
    .no-results {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 60px 20px;
      background: var(--bg-card);
      border: 1px dashed var(--border-color);
      border-radius: 14px;
      display: none;
    }}

    .no-results-icon {{
      font-size: 3rem;
      margin-bottom: 12px;
    }}

    .no-results-title {{
      font-size: 1.2rem;
      font-weight: 700;
      margin-bottom: 6px;
      color: var(--text-primary);
    }}

    .no-results-desc {{
      color: var(--text-secondary);
      font-size: 0.9rem;
      margin-bottom: 16px;
    }}

    /* Modals */
    .modal-backdrop {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: var(--modal-overlay);
      backdrop-filter: blur(6px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      opacity: 0;
      transition: opacity 0.2s ease;
    }}

    .modal-backdrop.open {{
      display: flex;
      opacity: 1;
    }}

    .modal-dialog {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      width: 100%;
      max-width: 960px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: var(--shadow-modal);
      position: relative;
      display: flex;
      flex-direction: column;
    }}

    .modal-header {{
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .modal-title-wrap {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .modal-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.3rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .modal-close {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      border-radius: 8px;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.2rem;
      transition: all 0.15s ease;
    }}

    .modal-close:hover {{
      color: var(--text-primary);
      border-color: var(--border-focus);
    }}

    .modal-body {{
      padding: 24px;
      flex: 1;
    }}

    .video-container {{
      position: relative;
      width: 100%;
      background: #000;
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 20px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }}

    .video-container video {{
      width: 100%;
      display: block;
      max-height: 520px;
    }}

    .modal-meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 20px;
    }}

    .modal-meta-item {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .modal-meta-label {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }}

    .modal-meta-value {{
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--text-primary);
    }}

    .modal-turns {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 20px;
    }}

    .modal-turns h3 {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--accent-indigo);
      margin-bottom: 10px;
    }}

    .modal-turns-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .modal-turns-list li {{
      font-size: 0.84rem;
      color: var(--text-secondary);
      line-height: 1.45;
    }}

    .modal-turns-list strong {{
      color: var(--text-primary);
    }}

    .modal-footer {{
      padding: 16px 24px;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }}

    /* Architecture Blueprint Visual Component */
    .arch-flow-container {{
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-bottom: 20px;
    }}

    .arch-layer-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-faint);
      border-radius: 12px;
      padding: 16px 18px;
    }}

    .arch-layer-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .arch-layer-title {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .arch-layer-pill {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 9999px;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--accent-blue);
      font-family: 'JetBrains Mono', monospace;
    }}

    .arch-layer-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
    }}

    .arch-item {{
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 0.8rem;
      color: var(--text-secondary);
      line-height: 1.45;
    }}

    .arch-item strong {{
      display: block;
      color: var(--text-primary);
      margin-bottom: 3px;
      font-size: 0.84rem;
    }}

    .arch-subagents-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}

    @media (max-width: 640px) {{
      .arch-subagents-row {{
        grid-template-columns: 1fr;
      }}
    }}

    .arch-arrow {{
      text-align: center;
      color: var(--accent-blue);
      font-size: 1.1rem;
      line-height: 1;
      margin: -6px 0;
      opacity: 0.85;
    }}

    /* Footer */
    .site-footer {{
      background: var(--bg-secondary);
      border-top: 1px solid var(--border-color);
      padding: 32px 24px;
      margin-top: 48px;
      text-align: center;
    }}

    .footer-inner {{
      max-width: 1360px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }}

    .footer-text {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .footer-links {{
      display: flex;
      gap: 18px;
      flex-wrap: wrap;
    }}

    .footer-link {{
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
      transition: color 0.15s ease;
    }}

    .footer-link:hover {{
      color: var(--accent-blue);
      text-decoration: underline;
    }}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
      .hero-title {{
        font-size: 1.85rem;
      }}
      .agent-grid {{
        grid-template-columns: 1fr;
      }}
      .stat-row {{
        grid-template-columns: repeat(2, 1fr);
      }}
      .header-inner {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .header-actions {{
        width: 100%;
        justify-content: space-between;
      }}
      .persona-overview-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <!-- Global Header -->
  <header class="site-header">
    <div class="header-inner">
      <a href="index.html" class="brand-logo">
        <span class="brand-icon">🏬</span>
        <div class="brand-text">
          <span class="brand-title">Gemini Enterprise Agents for Retail</span>
          <span class="brand-subtitle">Google ADK & Gemini Enterprise Multi-Agent Swarm</span>
        </div>
      </a>
      <div class="header-actions">
        <button id="archBtn" class="btn-header" aria-label="View Architecture Blueprint">
          <span>📐</span> Architecture Blueprint
        </button>
        <button id="themeToggleBtn" class="btn-header" aria-label="Toggle Light/Dark Theme">
          <span id="themeIcon">☀️</span> <span id="themeText">Light</span>
        </button>
        <a href="https://github.com/rajanm/retail-enterprise-agents" target="_blank" rel="noopener noreferrer" class="btn-header btn-primary-header">
          <span>⭐</span> GitHub Repository
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-pill">
      <span>🚀</span> 100 Enterprise Agents Fully Deployed (9 Retail Domains)
    </div>
    <h1 class="hero-title">
      Gemini Enterprise Agents for <span>Retail</span>
    </h1>
    <p class="hero-desc">
      A declarative, multi-agent platform powered by Google Agent Development Kit (ADK), Gemini Enterprise, and BigQuery Conversational Analytics. Real-time quantitative querying against 300+ enterprise retail datasets, grounded with external Google Search market intelligence.
    </p>

    <!-- Platform Stats -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-number">100</div>
        <div class="stat-label">Gemini Enterprise Agents</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">9</div>
        <div class="stat-label">Retail Domains</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">300+</div>
        <div class="stat-label">BigQuery Tables</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">2</div>
        <div class="stat-label">GCP Hosting Regions</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">100%</div>
        <div class="stat-label">Agents Demos Ready</div>
      </div>
    </div>
  </section>

  <!-- Main Content Area -->
  <main class="main-container">
    
    <!-- Toolbar: Search, View Mode, Domain & Persona Filters -->
    <section class="toolbar">
      <div class="search-row">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" placeholder="Search 100 agents by name, KPI (e.g. TRIR, OTIF, ROAS), business question, or BigQuery table..." autocomplete="off">
          <button id="searchClear" class="search-clear" aria-label="Clear search">✕</button>
        </div>
      </div>

      <!-- View Mode Selector -->
      <div class="view-mode-bar" id="viewModeBar" role="tablist" aria-label="Catalog View Mode">
        <div class="view-mode-toggle">
          <button class="view-mode-btn active" data-view="domain" role="tab" aria-selected="true">
            <span>🏢</span> Browse by Domain <span class="domain-count">9</span>
          </button>
          <button class="view-mode-btn" data-view="persona" role="tab" aria-selected="false">
            <span>👤</span> Browse by Persona <span class="domain-count">10</span>
          </button>
        </div>
        <div class="view-mode-hint" id="viewModeHint">
          Organized by 9 enterprise retail business functions
        </div>
      </div>

      <!-- Domain Pills -->
      <div class="domain-pills" id="domainPills">
        <button class="domain-btn active" data-domain="all">
          <span>🌐</span> All Domains <span class="domain-count">{total_agents}</span>
        </button>
        {"".join([f'''<button class="domain-btn" data-domain="{d}">
          <span>{DOMAIN_ICONS[d]}</span> {DOMAIN_DISPLAY_NAMES[d]} <span class="domain-count">{domain_counts.get(d, 0)}</span>
        </button>''' for d in DOMAIN_ORDER])}
      </div>

      <!-- Persona Pills -->
      <div class="domain-pills" id="personaPills" style="display: none;">
        <button class="domain-btn persona-btn active" data-persona="all">
          <span>👥</span> All Personas <span class="domain-count">{total_agents}</span>
        </button>
        {"".join([f'''<button class="domain-btn persona-btn" data-persona="{p['id']}">
          <span>{p['icon']}</span> {html.escape(p['title'])} <span class="domain-count">{persona_counts.get(p['id'], 0)}</span>
        </button>''' for p in PERSONA_ARCHETYPES])}
      </div>
    </section>

    <!-- Persona Experience Container (Overview Grid or Day-in-the-Life Storyboard) -->
    <section id="personaExperienceContainer" style="display: none;"></section>

    <!-- Results Header -->
    <div class="results-bar">
      <div class="results-count" id="resultsCount">
        Showing <strong>{total_agents}</strong> of {total_agents} enterprise agents
      </div>
    </div>

    <!-- Agent Grid -->
    <div class="agent-grid" id="agentGrid">
      <!-- Injected via JavaScript -->
    </div>

    <!-- No Results Fallback -->
    <div class="no-results" id="noResults">
      <div class="no-results-icon">🔎</div>
      <div class="no-results-title">No Matching Enterprise Agents Found</div>
      <p class="no-results-desc">Try refining your search keyword or switching filter tabs.</p>
      <button class="btn-header" onclick="resetFilters()">Reset All Filters</button>
    </div>

  </main>

  <!-- Video Player Modal -->
  <div class="modal-backdrop" id="videoModal">
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title-wrap">
          <div style="display:flex; gap:8px; align-items:center; margin-bottom:4px;">
            <span id="modalDomainBadge" class="badge-domain">Domain</span>
            <span id="modalRegionBadge" class="badge-region">us-central1</span>
          </div>
          <h2 id="modalAgentTitle" class="modal-title">Agent Title</h2>
        </div>
        <button class="modal-close" id="modalCloseBtn" aria-label="Close modal">✕</button>
      </div>
      <div class="modal-body">
        <div class="video-container">
          <video id="modalVideo" src="" controls playsinline preload="auto">
            Your browser does not support HTML5 video.
          </video>
        </div>

        <div class="modal-meta-grid">
          <div class="modal-meta-item">
            <span class="modal-meta-label">Resolution</span>
            <span class="modal-meta-value">1080p Full HD (1920×1080)</span>
          </div>
          <div class="modal-meta-item">
            <span class="modal-meta-label">Model Reasoning</span>
            <span class="modal-meta-value">Gemini 3.5 Flash (Global)</span>
          </div>
          <div class="modal-meta-item">
            <span class="modal-meta-label">Platform UI</span>
            <span class="modal-meta-value">Gemini Enterprise</span>
          </div>
          <div class="modal-meta-item">
            <span class="modal-meta-label">Data Execution</span>
            <span class="modal-meta-value">BigQuery Conversational Analytics</span>
          </div>
        </div>

        <div class="modal-turns">
          <h3>🎬 Demonstration Workflow Sequence</h3>
          <ul class="modal-turns-list" id="modalTurnsList">
            <li><strong>Turn 1 (Data Insights):</strong> BigQuery Conversational Analytics natural language to SQL quantitative execution.</li>
            <li><strong>Turn 2 (Market Grounding):</strong> Live Google Search grounding against external industry benchmarks and regulatory statistics.</li>
            <li><strong>Turn 3 (Visual Analytics):</strong> Python Matplotlib visual chart generation with KPI callouts.</li>
            <li><strong>Turn 4 (Canvas Presentation):</strong> Executive 4-slide slide deck generated in Gemini Enterprise Canvas.</li>
          </ul>
        </div>
      </div>
      <div class="modal-footer">
        <a id="modalDownloadBtn" href="#" download class="btn-header">
          <span>⬇️</span> Download MP4
        </a>
        <a id="modalShowcaseBtn" href="#" target="_blank" class="btn-header btn-primary-header">
          <span>🚀</span> Open Full Showcase Player
        </a>
      </div>
    </div>
  </div>

  <!-- Architecture Blueprint Modal -->
  <div class="modal-backdrop" id="archModal">
    <div class="modal-dialog" style="max-width: 1020px;">
      <div class="modal-header">
        <div class="modal-title-wrap">
          <h2 class="modal-title">📐 Retail Enterprise Multi-Agent Architecture</h2>
          <span style="font-size:0.8rem; color:var(--text-secondary);">Enterprise 4-Tier Google ADK & Gemini Enterprise Topology</span>
        </div>
        <button class="modal-close" id="archCloseBtn" aria-label="Close architecture modal">✕</button>
      </div>
      <div class="modal-body">

        <div class="arch-flow-container">
          <!-- Tier 1 -->
          <div class="arch-layer-card">
            <div class="arch-layer-header">
              <div class="arch-layer-title">
                <span>💬</span> Tier 1: Client & Presentation Layer
              </div>
              <span class="arch-layer-pill">Gemini Enterprise</span>
            </div>
            <div class="arch-layer-grid">
              <div class="arch-item">
                <strong>Discovery Engine Assistant</strong>
                100 Registered Enterprise Agents searchable via natural language chat
              </div>
              <div class="arch-item">
                <strong>Real-Time SSE Streaming</strong>
                Live multi-turn token streaming & dynamic markdown formatting
              </div>
              <div class="arch-item">
                <strong>Gemini Canvas Presentations</strong>
                Automated 4-slide executive decks generated directly from queries
              </div>
            </div>
          </div>

          <div class="arch-arrow">▼</div>

          <!-- Tier 2 -->
          <div class="arch-layer-card">
            <div class="arch-layer-header">
              <div class="arch-layer-title">
                <span>🧠</span> Tier 2: Orchestration & Multi-Agent Reasoning
              </div>
              <span class="arch-layer-pill">Gemini Enterprise Agent Platform</span>
            </div>
            <div class="arch-layer-grid">
              <div class="arch-item">
                <strong>Declarative ADK Framework</strong>
                Zero-boilerplate root orchestrators (`root_agent.yaml`)
              </div>
              <div class="arch-item">
                <strong>Multi-Region Hosting</strong>
                `us-central1` & `us-east4` hosting containers with auto-scaling
              </div>
              <div class="arch-item">
                <strong>Global Model Inference</strong>
                `gemini-3.5-flash` with low latency via global inference endpoint
              </div>
              <div class="arch-item">
                <strong>Lifecycle Callbacks</strong>
                IAM token scoping, date injection & dataset context binding
              </div>
            </div>
          </div>

          <div class="arch-arrow">▼</div>

          <!-- Tier 3: Parallel Sub-Agents -->
          <div class="arch-subagents-row">
            <div class="arch-layer-card" style="border-top: 3px solid var(--accent-emerald);">
              <div class="arch-layer-header">
                <div class="arch-layer-title" style="font-size:0.95rem;">
                  <span>📊</span> Sub-Agent 3A: BigQuery Data Insights
                </div>
                <span class="arch-layer-pill" style="color:var(--accent-emerald); background:var(--kpi-bg); border-color:var(--kpi-border);">Conversational Analytics</span>
              </div>
              <div style="display:flex; flex-direction:column; gap:8px;">
                <div class="arch-item">
                  <strong>Natural Language to SQL Engine</strong>
                  Conversational Analytics API executes parameterized SQL directly
                </div>
                <div class="arch-item">
                  <strong>Built-in ML Models</strong>
                  BigQuery forecasting, anomaly detection & contribution analysis
                </div>
                <div class="arch-item">
                  <strong>Matplotlib Chart Generator</strong>
                  Serverless visual chart rendering (`render_chart`)
                </div>
              </div>
            </div>

            <div class="arch-layer-card" style="border-top: 3px solid var(--accent-blue);">
              <div class="arch-layer-header">
                <div class="arch-layer-title" style="font-size:0.95rem;">
                  <span>🌐</span> Sub-Agent 3B: Market Context & Grounding
                </div>
                <span class="arch-layer-pill">Google Search Grounding</span>
              </div>
              <div style="display:flex; flex-direction:column; gap:8px;">
                <div class="arch-item">
                  <strong>Real-Time Web Grounding</strong>
                  Live Google Search verification for fresh industry trends
                </div>
                <div class="arch-item">
                  <strong>External Benchmarks</strong>
                  BLS labor, OSHA safety, FDA compliance & NRF retail statistics
                </div>
                <div class="arch-item">
                  <strong>Competitor Intelligence</strong>
                  Live market pricing, promotional tracking & consumer sentiment
                </div>
              </div>
            </div>
          </div>

          <div class="arch-arrow">▼</div>

          <!-- Tier 4 -->
          <div class="arch-layer-card" style="border-top: 3px solid var(--accent-indigo);">
            <div class="arch-layer-header">
              <div class="arch-layer-title">
                <span>🗄️</span> Tier 4: Enterprise Retail Data Lakehouse
              </div>
              <span class="arch-layer-pill" style="color:var(--region-text); background:var(--region-bg); border-color:var(--region-border);">Google Cloud BigQuery</span>
            </div>
            <div class="arch-layer-grid">
              <div class="arch-item">
                <strong>Enterprise Dataset</strong>
                `retail_ent_agents` multi-tenant retail schema
              </div>
              <div class="arch-item">
                <strong>300+ Partitioned Tables</strong>
                Structured namespace: `&lt;domain_id&gt;_&lt;agent_id&gt;_&lt;table_name&gt;`
              </div>
              <div class="arch-item">
                <strong>IAM Table Allowlisting</strong>
                Strict per-agent service account dataset authorization
              </div>
            </div>
          </div>
        </div>

        <div class="modal-turns">
          <h3>🚀 Key Architectural Pillars</h3>
          <ul class="modal-turns-list">
            <li><strong>Declarative ADK Architecture:</strong> Zero-code orchestrator models bind BigQuery tools and Google Search tools with strict domain separation.</li>
            <li><strong>Global Low-Latency Inference:</strong> `gemini-3.5-flash` global routing delivers ~30% faster time-to-first-token than regional clusters.</li>
            <li><strong>Dual Sub-Agent Pattern:</strong> Quantitative BigQuery queries and qualitative market grounding execute in specialized sub-agent contexts for hallucination-free answers.</li>
          </ul>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-header btn-primary-header" id="archOkBtn">Close Blueprint</button>
      </div>
    </div>
  </div>

  <!-- Full-Screen Stage Focus Theater Modal -->
  <div class="modal-backdrop stage-theater-backdrop" id="stageTheaterModal">
    <div class="modal-dialog stage-theater-dialog" id="stageTheaterDialog">
      <div class="stage-theater-header">
        <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span id="theaterPersonaIcon" style="font-size:1.4rem;">👤</span>
            <span id="theaterPersonaTitle" style="font-family:'Google Sans',sans-serif; font-size:1.05rem; font-weight:700; color:var(--text-primary);">Persona Focus Theater</span>
          </div>
          <div class="stage-theater-tabs" id="theaterStageTabs">
            <!-- Injected via JavaScript -->
          </div>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <div class="ditl-state-switcher" id="theaterStateSwitcher">
            <!-- Injected via JavaScript -->
          </div>
          <button class="btn-header" onclick="closeStageTheater()" style="padding:6px 12px; font-weight:700;">
            ✕ Exit Full Screen (Esc)
          </button>
        </div>
      </div>
      <div class="stage-theater-body" id="stageTheaterBody">
        <!-- Injected via JavaScript -->
      </div>
    </div>
  </div>

  <!-- Site Footer -->
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="brand-logo" style="justify-content: center;">
        <span class="brand-icon">🏬</span>
        <span class="brand-title">Gemini Enterprise Agents for Retail</span>
      </div>
      <p class="footer-text">
        100 Enterprise Agents across 9 Strategic Retail Domains. Powered by Google ADK, Gemini Enterprise, and BigQuery.
      </p>
      <div class="footer-links">
        <a href="https://github.com/rajanm/retail-enterprise-agents" target="_blank" rel="noopener noreferrer" class="footer-link">GitHub Repository</a>
        <a href="https://github.com/rajanm/retail-enterprise-agents/blob/master/README.md" target="_blank" rel="noopener noreferrer" class="footer-link">Project Documentation</a>
        <a href="https://github.com/rajanm/retail-enterprise-agents/blob/master/ARCHITECTURE.md" target="_blank" rel="noopener noreferrer" class="footer-link">Architecture Reference</a>
      </div>
    </div>
  </footer>

  <!-- Motion Animation Library (ES Module with Web Animations API Fallback) -->
  <script type="module">
    try {{
      const {{ animate, stagger }} = await import('https://cdn.jsdelivr.net/npm/motion@11.11.13/+esm');
      window.Motion = {{ animate, stagger }};
    }} catch (e) {{
      console.warn('Motion CDN unavailable; using Web Animations API fallback', e);
    }}
  </script>

  <!-- Embedded JSON Data & Client Application Script -->
  <script>
    const AGENTS_DATA = {agents_json};

    let activeDomain = 'all';
    const PERSONA_ARCHETYPES = {personas_json};
    const PERSONA_MAP = Object.fromEntries(PERSONA_ARCHETYPES.map(p => [p.id, p]));
    let viewMode = 'domain';
    let activePersona = 'all';
    let ditlCollapsed = false;
    let ditlStateMode = 'after';
    let activeTaskStateFilter = null; // null or 'unchanged' | 'augmented' | 'automated' | 'new' | 'retired'
    let hoveredTaskStateFilter = null;
    let maximizedStageIdx = 0;
    let searchQuery = '';

    function setDitlStateMode(mode) {{
      ditlStateMode = mode;
      renderPersonaExperience();
      if (stageTheaterModal && stageTheaterModal.classList.contains('open')) {{
        renderStageTheater();
      }}
    }}

    function previewTaskStateFilter(state) {{
      hoveredTaskStateFilter = state;
      applyProminentSpotlight();
    }}

    function clearPreviewTaskStateFilter() {{
      hoveredTaskStateFilter = null;
      applyProminentSpotlight();
    }}

    function toggleTaskStateFilter(state) {{
      if (activeTaskStateFilter === state) {{
        activeTaskStateFilter = null;
      }} else {{
        activeTaskStateFilter = state;
      }}
      applyProminentSpotlight();
      // Update UI active filter pills
      document.querySelectorAll('.ditl-state-filter-pill').forEach(pill => {{
        const pState = pill.getAttribute('data-filter-state');
        const isActive = pState === activeTaskStateFilter;
        pill.classList.toggle('active-filter', isActive);
        const ind = pill.querySelector('.pill-check-ind');
        if (ind) ind.textContent = isActive ? '✓' : '○';
      }});
      // Show/hide reset pills
      document.querySelectorAll('.filter-reset-pill').forEach(btn => {{
        btn.style.display = activeTaskStateFilter ? 'inline-flex' : 'none';
      }});
    }}

    function resetTaskStateFilter() {{
      activeTaskStateFilter = null;
      hoveredTaskStateFilter = null;
      document.querySelectorAll('.task-tile.is-pinned, .conduit-node.is-pinned').forEach(el => {{
        el.classList.remove('is-pinned');
        const chip = el.querySelector('.task-pin-chip');
        if (chip) chip.textContent = 'Click to pin focus';
      }});
      applyProminentSpotlight();
      document.querySelectorAll('.ditl-state-filter-pill').forEach(pill => {{
        pill.classList.remove('active-filter');
        const ind = pill.querySelector('.pill-check-ind');
        if (ind) ind.textContent = '○';
      }});
      document.querySelectorAll('.filter-reset-pill').forEach(btn => {{
        btn.style.display = 'none';
      }});
    }}

    // Elements
    const searchInput = document.getElementById('searchInput');
    const searchClear = document.getElementById('searchClear');
    const domainPills = document.getElementById('domainPills');
    const personaPills = document.getElementById('personaPills');
    const viewModeBar = document.getElementById('viewModeBar');
    const viewModeHint = document.getElementById('viewModeHint');
    const personaExperienceContainer = document.getElementById('personaExperienceContainer');
    const agentGrid = document.getElementById('agentGrid');
    const resultsBar = document.querySelector('.results-bar');
    const noResults = document.getElementById('noResults');
    const resultsCount = document.getElementById('resultsCount');
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    // Video Modal Elements
    const videoModal = document.getElementById('videoModal');
    const modalVideo = document.getElementById('modalVideo');
    const modalAgentTitle = document.getElementById('modalAgentTitle');
    const modalDomainBadge = document.getElementById('modalDomainBadge');
    const modalRegionBadge = document.getElementById('modalRegionBadge');
    const modalTurnsList = document.getElementById('modalTurnsList');
    const modalDownloadBtn = document.getElementById('modalDownloadBtn');
    const modalShowcaseBtn = document.getElementById('modalShowcaseBtn');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    // Architecture Modal Elements
    const archModal = document.getElementById('archModal');
    const archBtn = document.getElementById('archBtn');
    const archCloseBtn = document.getElementById('archCloseBtn');
    const archOkBtn = document.getElementById('archOkBtn');

    // Full-Screen Stage Focus Theater Modal Elements
    const stageTheaterModal = document.getElementById('stageTheaterModal');
    const stageTheaterDialog = document.getElementById('stageTheaterDialog');
    const theaterPersonaIcon = document.getElementById('theaterPersonaIcon');
    const theaterPersonaTitle = document.getElementById('theaterPersonaTitle');
    const theaterStageTabs = document.getElementById('theaterStageTabs');
    const theaterStateSwitcher = document.getElementById('theaterStateSwitcher');
    const stageTheaterBody = document.getElementById('stageTheaterBody');

    // Theme Management
    function initTheme() {{
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      updateThemeUI(current);
    }}

    function updateThemeUI(theme) {{
      if (theme === 'light') {{
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark';
      }} else {{
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light';
      }}
    }}

    themeToggleBtn.addEventListener('click', () => {{
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('retail_agents_theme', next);
      updateThemeUI(next);
    }});

    // Motion Animation Choreography (Motion library + native Web Animations API fallback)
    function runMotionChoreography(container) {{
      if (!container) return;
      const cards = container.querySelectorAll('.persona-overview-card, .ditl-stage-card, .agent-card');
      const taskTiles = container.querySelectorAll('.task-tile');
      const flowSteps = container.querySelectorAll('.flow-step-card');
      const railFills = container.querySelectorAll('.motion-rail-fill');

      if (window.Motion && typeof window.Motion.animate === 'function') {{
        try {{
          if (cards.length) {{
            const staggerFn = window.Motion.stagger ? window.Motion.stagger(0.04) : 0.04;
            window.Motion.animate(
              cards,
              {{ opacity: [0, 1], y: [16, 0] }},
              {{ delay: staggerFn, duration: 0.35, easing: 'ease-out' }}
            );
          }}

          if (taskTiles.length) {{
            const tileStagger = window.Motion.stagger ? window.Motion.stagger(0.025) : 0.025;
            window.Motion.animate(
              taskTiles,
              {{ opacity: [0, 1], scale: [0.96, 1] }},
              {{ delay: tileStagger, duration: 0.30, easing: 'ease-out' }}
            );
          }}

          if (flowSteps.length) {{
            const flowStagger = window.Motion.stagger ? window.Motion.stagger(0.045) : 0.045;
            window.Motion.animate(
              flowSteps,
              {{ opacity: [0, 1], y: [10, 0] }},
              {{ delay: flowStagger, duration: 0.32, easing: 'ease-out' }}
            );
          }}

          if (railFills.length) {{
            window.Motion.animate(
              railFills,
              {{ width: ['0%', '100%'] }},
              {{ duration: 0.65, easing: 'ease-out' }}
            );
          }}

          const fillBars = container.querySelectorAll('.auto-fill-bar');
          fillBars.forEach(bar => {{
            const targetW = bar.getAttribute('data-target-width') || bar.style.width;
            bar.style.width = '0%';
            window.Motion.animate(bar, {{ width: targetW }}, {{ duration: 0.6, easing: 'ease-out' }});
          }});
          return;
        }} catch (e) {{
          // Fall through to native Web Animations API fallback
        }}
      }}

      // Native Web Animations API fallback
      cards.forEach((card, idx) => {{
        card.animate(
          [
            {{ opacity: 0, transform: 'translateY(16px)' }},
            {{ opacity: 1, transform: 'translateY(0)' }}
          ],
          {{
            duration: 350,
            delay: Math.min(idx * 40, 400),
            easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
            fill: 'forwards'
          }}
        );
      }});

      taskTiles.forEach((tile, idx) => {{
        tile.animate(
          [
            {{ opacity: 0, transform: 'scale(0.96)' }},
            {{ opacity: 1, transform: 'scale(1)' }}
          ],
          {{
            duration: 300,
            delay: Math.min(idx * 25, 300),
            easing: 'ease-out',
            fill: 'forwards'
          }}
        );
      }});

      flowSteps.forEach((step, idx) => {{
        step.animate(
          [
            {{ opacity: 0, transform: 'translateY(10px)' }},
            {{ opacity: 1, transform: 'translateY(0)' }}
          ],
          {{
            duration: 320,
            delay: Math.min(idx * 45, 350),
            easing: 'ease-out',
            fill: 'forwards'
          }}
        );
      }});

      railFills.forEach(rail => {{
        rail.animate(
          [
            {{ width: '0%' }},
            {{ width: '100%' }}
          ],
          {{
            duration: 650,
            easing: 'ease-out',
            fill: 'forwards'
          }}
        );
      }});

      const fillBars = container.querySelectorAll('.auto-fill-bar');
      fillBars.forEach(bar => {{
        const targetW = bar.getAttribute('data-target-width') || bar.style.width;
        bar.animate(
          [
            {{ width: '0%' }},
            {{ width: targetW }}
          ],
          {{
            duration: 600,
            easing: 'ease-out',
            fill: 'forwards'
          }}
        );
      }});
    }}

    // Prominent Motion Spotlighting & Dimming Controller
    function applyProminentSpotlight(pinnedTile = null) {{
      const effectiveStateFilter = hoveredTaskStateFilter || activeTaskStateFilter;
      const stageCards = document.querySelectorAll('.ditl-stage-card');
      stageCards.forEach(stageCard => {{
        const taskTiles = stageCard.querySelectorAll('.task-tile');
        const conduitNodes = stageCard.querySelectorAll('.conduit-node');
        const flowStepCards = stageCard.querySelectorAll('.flow-step-card');
        const stagePinnedTile = pinnedTile && stageCard.contains(pinnedTile)
          ? pinnedTile
          : stageCard.querySelector('.task-tile.is-pinned');
        const stagePinnedStep = stageCard.querySelector('.conduit-node.is-pinned');

        const hasFilter = !!effectiveStateFilter;
        const hasPinTile = !!stagePinnedTile;
        const hasPinStep = !!stagePinnedStep;

        if (!hasFilter && !hasPinTile && !hasPinStep) {{
          taskTiles.forEach(tile => {{
            tile.classList.remove('motion-dimmed', 'motion-spotlight');
          }});
          conduitNodes.forEach(node => {{
            node.classList.remove('motion-dimmed', 'motion-spotlight', 'active-step');
          }});
          flowStepCards.forEach(card => {{
            card.classList.remove('motion-dimmed', 'motion-spotlight', 'active-step');
          }});
          return;
        }}

        if (hasFilter) {{
          const newlySpotlit = [];
          taskTiles.forEach(tile => {{
            const tileState = tile.getAttribute('data-task-state');
            const isMatch = tileState === effectiveStateFilter;
            const wasSpotlit = tile.classList.contains('motion-spotlight');
            tile.classList.toggle('motion-spotlight', isMatch);
            tile.classList.toggle('motion-dimmed', !isMatch);
            if (isMatch && !wasSpotlit) newlySpotlit.push(tile);
          }});
          // Also highlight conduit nodes that execute tasks with this state
          const activeStepIndices = new Set();
          taskTiles.forEach(tile => {{
            if (tile.getAttribute('data-task-state') === effectiveStateFilter) {{
              const stepsAttr = tile.getAttribute('data-steps') || '';
              stepsAttr.split(',').map(s => s.trim()).filter(Boolean).forEach(s => activeStepIndices.add(s));
            }}
          }});
          conduitNodes.forEach(node => {{
            const stepVal = node.getAttribute('data-step');
            const isMatch = activeStepIndices.has(stepVal);
            node.classList.toggle('active-step', isMatch);
            node.classList.toggle('motion-dimmed', !isMatch);
            node.classList.remove('motion-spotlight');
          }});
          flowStepCards.forEach(card => {{
            const stepVal = card.getAttribute('data-step');
            const isMatch = activeStepIndices.has(stepVal);
            const wasSpotlit = card.classList.contains('motion-spotlight');
            card.classList.toggle('motion-spotlight', isMatch);
            card.classList.toggle('active-step', isMatch);
            card.classList.toggle('motion-dimmed', !isMatch);
            if (isMatch && !wasSpotlit) newlySpotlit.push(card);
          }});
          if (newlySpotlit.length && window.Motion && typeof window.Motion.animate === 'function') {{
            try {{
              window.Motion.animate(newlySpotlit, {{ scale: [0.97, 1.03] }}, {{ duration: 0.24, easing: 'ease-out' }});
            }} catch (e) {{}}
          }}
        }} else if (hasPinTile) {{
          const stepsAttr = stagePinnedTile.getAttribute('data-steps') || '';
          const indices = stepsAttr.split(',').map(s => s.trim()).filter(Boolean);

          taskTiles.forEach(tile => {{
            const isTarget = tile === stagePinnedTile;
            tile.classList.toggle('motion-spotlight', isTarget);
            tile.classList.toggle('motion-dimmed', !isTarget);
          }});

          conduitNodes.forEach(node => {{
            const stepVal = node.getAttribute('data-step');
            const isMatch = indices.includes(stepVal);
            node.classList.toggle('active-step', isMatch);
            node.classList.toggle('motion-dimmed', !isMatch);
            node.classList.remove('motion-spotlight');
          }});

          flowStepCards.forEach(card => {{
            const stepVal = card.getAttribute('data-step');
            const isMatch = indices.includes(stepVal);
            card.classList.toggle('motion-spotlight', isMatch);
            card.classList.toggle('active-step', isMatch);
            card.classList.toggle('motion-dimmed', !isMatch);
          }});
        }} else if (hasPinStep) {{
          const targetStepVal = stagePinnedStep.getAttribute('data-step');
          taskTiles.forEach(tile => {{
            const stepsAttr = tile.getAttribute('data-steps') || '';
            const indices = stepsAttr.split(',').map(s => s.trim()).filter(Boolean);
            const isMatch = indices.includes(targetStepVal);
            tile.classList.toggle('motion-spotlight', isMatch);
            tile.classList.toggle('motion-dimmed', !isMatch);
          }});
          conduitNodes.forEach(node => {{
            const isTarget = node === stagePinnedStep;
            node.classList.toggle('active-step', isTarget);
            node.classList.toggle('motion-dimmed', !isTarget);
            node.classList.remove('motion-spotlight');
          }});
          flowStepCards.forEach(card => {{
            const isTarget = card.getAttribute('data-step') === targetStepVal;
            card.classList.toggle('motion-spotlight', isTarget);
            card.classList.toggle('active-step', isTarget);
            card.classList.toggle('motion-dimmed', !isTarget);
          }});
        }}
      }});
    }}

    // Interactive Bidirectional Pipeline Spotlight Tracing with Pinning Support
    function bindPipelineSpotlightEvents(container) {{
      if (!container) return;
      const stageCards = container.querySelectorAll('.ditl-stage-card');

      stageCards.forEach(stageCard => {{
        const conduitNodes = stageCard.querySelectorAll('.conduit-node');
        const flowStepCards = stageCard.querySelectorAll('.flow-step-card');
        const taskTiles = stageCard.querySelectorAll('.task-tile');

        const stepElements = conduitNodes.length ? conduitNodes : flowStepCards;

        stepElements.forEach(stepElem => {{
          const stepVal = stepElem.getAttribute('data-step');
          if (!stepVal) return;

          const onEnter = () => {{
            if (activeTaskStateFilter || hoveredTaskStateFilter) return;
            stepElements.forEach(se => {{
              const isSelf = se === stepElem;
              se.classList.toggle('active-step', isSelf);
              se.classList.toggle('motion-dimmed', !isSelf);
              const innerCard = se.classList.contains('flow-step-card') ? se : se.querySelector('.flow-step-card');
              if (innerCard) {{
                innerCard.classList.toggle('motion-spotlight', isSelf);
                innerCard.classList.toggle('active-step', isSelf);
              }}
            }});
            taskTiles.forEach(tile => {{
              const stepsAttr = tile.getAttribute('data-steps') || '';
              const indices = stepsAttr.split(',').map(s => s.trim()).filter(Boolean);
              if (indices.includes(stepVal)) {{
                tile.classList.add('motion-spotlight');
                tile.classList.remove('motion-dimmed');
                if (window.Motion && typeof window.Motion.animate === 'function') {{
                  try {{
                    window.Motion.animate(tile, {{ scale: [0.98, 1.03] }}, {{ duration: 0.24, easing: 'ease-out' }});
                  }} catch (e) {{}}
                }}
              }} else {{
                tile.classList.remove('motion-spotlight');
                tile.classList.add('motion-dimmed');
              }}
            }});
          }};

          const onLeave = () => {{
            if (activeTaskStateFilter || hoveredTaskStateFilter) return;
            applyProminentSpotlight();
          }};

          stepElem.addEventListener('mouseenter', onEnter);
          stepElem.addEventListener('mouseleave', onLeave);
          stepElem.addEventListener('focus', onEnter);
          stepElem.addEventListener('blur', onLeave);

          stepElem.addEventListener('click', (e) => {{
            if (e.target.closest('.conduit-demo-btn')) return;
            const wasPinned = stepElem.classList.contains('is-pinned');
            stageCard.querySelectorAll('.task-tile.is-pinned, .conduit-node.is-pinned').forEach(el => {{
              el.classList.remove('is-pinned');
              const chip = el.querySelector('.task-pin-chip');
              if (chip) chip.textContent = 'Click to pin focus';
            }});
            if (!wasPinned) {{
              stepElem.classList.add('is-pinned');
            }}
            applyProminentSpotlight();
          }});
        }});

        taskTiles.forEach(tile => {{
          const stepsAttr = tile.getAttribute('data-steps') || '';
          const indices = stepsAttr.split(',').map(s => s.trim()).filter(Boolean);

          tile.addEventListener('mouseenter', () => {{
            if (activeTaskStateFilter || hoveredTaskStateFilter) return;
            taskTiles.forEach(t => {{
              const isSelf = t === tile;
              t.classList.toggle('motion-spotlight', isSelf);
              t.classList.toggle('motion-dimmed', !isSelf);
            }});
            const matchedSteps = [];
            stepElements.forEach(stepElem => {{
              const stepVal = stepElem.getAttribute('data-step');
              const isMatch = indices.includes(stepVal);
              const innerCard = stepElem.classList.contains('flow-step-card') ? stepElem : stepElem.querySelector('.flow-step-card');
              stepElem.classList.toggle('active-step', isMatch);
              stepElem.classList.toggle('motion-dimmed', !isMatch);
              if (innerCard) {{
                innerCard.classList.toggle('motion-spotlight', isMatch);
                innerCard.classList.toggle('active-step', isMatch);
                if (isMatch) matchedSteps.push(innerCard);
              }}
            }});
            if (matchedSteps.length && window.Motion && typeof window.Motion.animate === 'function') {{
              try {{
                window.Motion.animate(matchedSteps, {{ scale: [0.98, 1.03] }}, {{ duration: 0.24, easing: 'ease-out' }});
              }} catch (e) {{}}
            }}
          }});

          tile.addEventListener('mouseleave', () => {{
            if (activeTaskStateFilter || hoveredTaskStateFilter) return;
            applyProminentSpotlight();
          }});

          // Click to Pin Focus
          tile.addEventListener('click', (e) => {{
            if (e.target.closest('button')) return;
            const wasPinned = tile.classList.contains('is-pinned');
            stageCard.querySelectorAll('.task-tile.is-pinned, .conduit-node.is-pinned').forEach(el => {{
              el.classList.remove('is-pinned');
              const chip = el.querySelector('.task-pin-chip');
              if (chip) chip.textContent = 'Click to pin focus';
            }});
            if (!wasPinned) {{
              tile.classList.add('is-pinned');
              const chip = tile.querySelector('.task-pin-chip');
              if (chip) chip.textContent = '📌 Pinned Focus';
              applyProminentSpotlight(tile);
            }} else {{
              applyProminentSpotlight(null);
            }}
          }});
        }});
      }});
    }}

    // Full-Screen Stage Focus Theater Modal Handlers
    function openStageTheater(stageIdx) {{
      const p = PERSONA_MAP[activePersona];
      if (!p) return;
      maximizedStageIdx = stageIdx;

      theaterPersonaIcon.textContent = p.icon || '👤';
      theaterPersonaTitle.textContent = `${{p.title}} — Stage Focus Theater`;

      renderStageTheater();
      stageTheaterModal.classList.add('open');
      document.body.style.overflow = 'hidden';

      if (stageTheaterDialog && window.Motion && typeof window.Motion.animate === 'function') {{
        try {{
          window.Motion.animate(
            stageTheaterDialog,
            {{ opacity: [0, 1], scale: [0.94, 1], y: [18, 0] }},
            {{ duration: 0.28, easing: 'ease-out' }}
          );
        }} catch (e) {{}}
      }}
    }}

    function closeStageTheater() {{
      stageTheaterModal.classList.remove('open');
      document.body.style.overflow = '';
    }}

    function switchTheaterStage(stageIdx) {{
      maximizedStageIdx = stageIdx;
      renderStageTheater();
      if (stageTheaterBody && window.Motion && typeof window.Motion.animate === 'function') {{
        try {{
          window.Motion.animate(
            stageTheaterBody,
            {{ opacity: [0, 1], x: [14, 0] }},
            {{ duration: 0.24, easing: 'ease-out' }}
          );
        }} catch (e) {{}}
      }}
    }}

    function renderStageTheater() {{
      const p = PERSONA_MAP[activePersona];
      if (!p || !p.day_in_the_life) return;

      const stages = p.day_in_the_life;
      const stageIdx = Math.max(0, Math.min(maximizedStageIdx, stages.length - 1));
      const stage = stages[stageIdx];

      // 1. Render Stage Navigation Tabs
      theaterStageTabs.innerHTML = stages.map((s, idx) => `
        <button type="button" class="theater-stage-tab ${{idx === stageIdx ? 'active' : ''}}" onclick="switchTheaterStage(${{idx}})" title="Stage ${{idx + 1}}: ${{htmlEscape(s.stage)}}">
          ${{idx === stageIdx ? '● ' : '○ '}}${{htmlEscape(s.time)}}
        </button>
      `).join('');

      // 2. Render Theater State Switcher
      theaterStateSwitcher.innerHTML = `
        <div class="ditl-state-switcher">
          <button type="button" class="ditl-state-btn ${{ditlStateMode === 'before' ? 'active-before' : ''}}" onclick="setDitlStateMode('before')" style="white-space:nowrap;">
            <span class="mode-radio-dot">${{ditlStateMode === 'before' ? '●' : '○'}}</span> Before Agents
          </button>
          <button type="button" class="ditl-state-btn ${{ditlStateMode === 'after' ? 'active-after' : ''}}" onclick="setDitlStateMode('after')" style="white-space:nowrap;">
            <span class="mode-radio-dot">${{ditlStateMode === 'after' ? '●' : '○'}}</span> After Agents (5-State + Flow)
          </button>
        </div>
      `;

      // 3. Render Stage Body
      const bundle = stage.task_bundle || [];
      const taskTilesHtml = bundle.map((t, tileIdx) => {{
        if (ditlStateMode === 'before') {{
          const isNew = t.state === 'new';
          const stateClass = isNew ? 'state-dormant' : 'state-unchanged';
          const tagText = isNew ? '◌ NOT PERFORMED' : '🟫 MANUAL STEP';
          return `
            <div class="task-tile ${{stateClass}}" data-task-state="${{t.state}}" data-task-idx="${{tileIdx}}">
              <div class="task-tile-top">
                <span class="task-state-tag">${{tagText}}</span>
              </div>
              <div class="task-tile-label">${{htmlEscape(t.label)}}</div>
            </div>
          `;
        }} else {{
          let stateTag = '🟫 UNCHANGED';
          if (t.state === 'augmented') stateTag = '🟪 AUGMENTED';
          else if (t.state === 'automated') stateTag = '🟦 AUTOMATED';
          else if (t.state === 'new') stateTag = '🟨 NEW AI TASK';
          else if (t.state === 'retired') stateTag = '◌ RETIRED';

          const stepIndicesStr = (t.step_indices || []).join(',');
          const stepRefHtml = t.steps_label ? `<span class="task-step-ref">${{htmlEscape(t.steps_label)}}</span>` : '';

          return `
            <div class="task-tile state-${{t.state}}" data-task-state="${{t.state}}" data-task-idx="${{tileIdx}}" data-steps="${{stepIndicesStr}}" tabindex="0">
              <div class="task-tile-top">
                <span class="task-state-tag">${{stateTag}}</span>
                ${{stepRefHtml}}
              </div>
              <div class="task-tile-label">${{htmlEscape(t.label)}}</div>
              <div class="task-tile-footer">
                <span class="task-pin-chip">Click to pin focus</span>
              </div>
            </div>
          `;
        }}
      }}).join('');

      let flowHtml = '';
      if (ditlStateMode === 'after') {{
        let flow = stage.agent_flow || [];
        if (!flow.length && stage.featured_agents) {{
          flow = stage.featured_agents.map((slug, idx) => ({{
            step: idx + 1,
            step_code: String(idx + 1).padStart(2, '0'),
            slug: slug,
            action_tag: 'EXECUTES ANALYTICS'
          }}));
        }}

        const conduitNodesHtml = flow.map((f, idx) => {{
          const agent = AGENTS_DATA.find(a => a.name === f.slug);
          const agentLabel = agent ? agent.display_name : f.slug.replace(/_/g, ' ');
          const connector = idx < flow.length - 1 ? '→' : '✓';

          return `
            <div class="conduit-node" data-step="${{f.step}}">
              <div class="conduit-medallion-row">
                <div class="conduit-medallion">${{htmlEscape(f.step_code)}}</div>
                ${{idx < flow.length - 1 ? `<span class="conduit-arrow">${{connector}}</span>` : ''}}
              </div>
              <div class="conduit-step-card flow-step-card" data-step="${{f.step}}">
                <div class="flow-step-top">
                  <span class="flow-step-badge">STEP ${{htmlEscape(f.step_code)}}</span>
                  <span class="conduit-linked-badge">LINKED</span>
                </div>
                <div class="flow-step-action">
                  <span>${{htmlEscape(f.action_tag)}}</span>
                </div>
                <div class="flow-step-agent" title="${{htmlEscape(agentLabel)}}">${{htmlEscape(agentLabel)}}</div>
                <button type="button" class="conduit-demo-btn" onclick="openVideoModal('${{f.slug}}')" title="Watch 1080p Demo for ${{htmlEscape(agentLabel)}}">
                  <span>🎬</span> Watch Demo
                </button>
              </div>
            </div>
          `;
        }}).join('');

        flowHtml = `
          <div class="stage-flow-section">
            <div class="stage-flow-header">
              <span class="stage-flow-title">
                <span class="motion-pulse-dot"></span> Recommended Agent Execution Flow (${{flow.length}} Sequenced Steps)
              </span>
              <span class="stage-flow-hint">⚡ Hover or click any task, state pill, or step to spotlight linked agents · Click 🎬 Watch Demo for 1080p video</span>
            </div>
            <div class="flow-conduit-track" style="--conduit-cols: ${{flow.length}};">
              <div class="conduit-rail-line">
                <div class="conduit-rail-fill motion-rail-fill"></div>
              </div>
              ${{conduitNodesHtml}}
            </div>
            <div class="flow-bento-grid" style="display: none;">
              <!-- Maintained for bento grid compatibility -->
            </div>
          </div>
        `;
      }}

      const horizonBadge = ditlStateMode === 'before'
        ? `<span class="ditl-stage-horizon manual-mode">⏱️ Manual: ${{htmlEscape(stage.time_before)}}</span>`
        : `<span class="ditl-stage-horizon">⏱️ ${{htmlEscape(stage.time_before)}} → ⚡ ${{htmlEscape(stage.time_after)}}</span>`;

      stageTheaterBody.innerHTML = `
        <div class="ditl-stage-card" style="box-shadow: none; border: none; padding: 0; background: transparent;">
          <div class="ditl-stage-top">
            <span class="ditl-time-stage">📋 ${{htmlEscape(stage.time)}} · ${{htmlEscape(stage.stage)}}</span>
            <div class="ditl-stage-top-right">
              ${{horizonBadge}}
            </div>
          </div>

          <div class="task-bundle-key-bar" style="margin: 4px 0 8px; padding: 8px 12px;">
            <span class="task-bundle-key-title">Filter by Task State:</span>
            <div class="task-bundle-key-items">
              <button type="button" class="task-bundle-key-chip key-unchanged ditl-state-filter-pill ${{activeTaskStateFilter === 'unchanged' ? 'active-filter' : ''}}" data-filter-state="unchanged" onclick="toggleTaskStateFilter('unchanged')" onmouseenter="previewTaskStateFilter('unchanged')" onmouseleave="clearPreviewTaskStateFilter()">
                <span class="pill-check-ind">${{activeTaskStateFilter === 'unchanged' ? '✓' : '○'}}</span> 🟫 1. Tasks Unchanged
              </button>
              <button type="button" class="task-bundle-key-chip key-augmented ditl-state-filter-pill ${{activeTaskStateFilter === 'augmented' ? 'active-filter' : ''}}" data-filter-state="augmented" onclick="toggleTaskStateFilter('augmented')" onmouseenter="previewTaskStateFilter('augmented')" onmouseleave="clearPreviewTaskStateFilter()">
                <span class="pill-check-ind">${{activeTaskStateFilter === 'augmented' ? '✓' : '○'}}</span> 🟪 2. Tasks Augmented
              </button>
              <button type="button" class="task-bundle-key-chip key-automated ditl-state-filter-pill ${{activeTaskStateFilter === 'automated' ? 'active-filter' : ''}}" data-filter-state="automated" onclick="toggleTaskStateFilter('automated')" onmouseenter="previewTaskStateFilter('automated')" onmouseleave="clearPreviewTaskStateFilter()">
                <span class="pill-check-ind">${{activeTaskStateFilter === 'automated' ? '✓' : '○'}}</span> 🟦 3. Tasks Automated
              </button>
              <button type="button" class="task-bundle-key-chip key-new ditl-state-filter-pill ${{activeTaskStateFilter === 'new' ? 'active-filter' : ''}}" data-filter-state="new" onclick="toggleTaskStateFilter('new')" onmouseenter="previewTaskStateFilter('new')" onmouseleave="clearPreviewTaskStateFilter()">
                <span class="pill-check-ind">${{activeTaskStateFilter === 'new' ? '✓' : '○'}}</span> 🟨 4. New Tasks Created by AI
              </button>
              <button type="button" class="task-bundle-key-chip key-retired ditl-state-filter-pill ${{activeTaskStateFilter === 'retired' ? 'active-filter' : ''}}" data-filter-state="retired" onclick="toggleTaskStateFilter('retired')" onmouseenter="previewTaskStateFilter('retired')" onmouseleave="clearPreviewTaskStateFilter()">
                <span class="pill-check-ind">${{activeTaskStateFilter === 'retired' ? '✓' : '○'}}</span> ◌ 5. Retired Manual Tasks
              </button>
              <button type="button" class="filter-reset-pill" onclick="resetTaskStateFilter()" style="display: ${{activeTaskStateFilter ? 'inline-flex' : 'none'}};">
                ✕ Reset Filter
              </button>
            </div>
          </div>

          <div class="task-bundle-wrap">
            <div class="task-bundle-title">
              <span>${{ditlStateMode === 'before' ? 'Manual Task Bundle (Baseline)' : '5-State Task Transformation Bundle (6 Tasks)'}}</span>
              <span>${{ditlStateMode === 'before' ? '⏱️ Legacy Manual Effort' : '⚡ AI-Augmented Horizon'}}</span>
            </div>
            <div class="task-bundle-grid">
              ${{taskTilesHtml}}
            </div>
          </div>

          ${{flowHtml}}
        </div>
      `;

      bindPipelineSpotlightEvents(stageTheaterBody);
      runMotionChoreography(stageTheaterBody);
      if (activeTaskStateFilter) {{
        applyProminentSpotlight();
      }}
    }}

    // View Mode Management
    function setViewMode(mode) {{
      viewMode = mode;
      document.querySelectorAll('.view-mode-btn').forEach(btn => {{
        const isActive = btn.dataset.view === mode;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
      }});

      if (mode === 'domain') {{
        if (domainPills) domainPills.style.display = 'flex';
        if (personaPills) personaPills.style.display = 'none';
        if (personaExperienceContainer) personaExperienceContainer.style.display = 'none';
        if (resultsBar) resultsBar.style.display = 'flex';
        if (agentGrid) agentGrid.style.display = 'grid';
        if (viewModeHint) viewModeHint.textContent = 'Organized by 9 enterprise retail business functions';
      }} else {{
        if (domainPills) domainPills.style.display = 'none';
        if (personaPills) personaPills.style.display = 'flex';
        if (personaExperienceContainer) personaExperienceContainer.style.display = 'block';
        if (resultsBar) resultsBar.style.display = 'none';
        if (agentGrid) agentGrid.style.display = 'none';
        if (noResults) noResults.style.display = 'none';
        if (viewModeHint) viewModeHint.textContent = 'Organized by 10 retail leadership and operational roles with Day-in-the-Life workflows';
      }}

      renderPersonaExperience();
      renderAgents();
    }}

    // Persona Selection
    function selectPersona(personaId) {{
      activePersona = personaId;
      if (viewMode !== 'persona') {{
        setViewMode('persona');
      }}

      document.querySelectorAll('.persona-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.persona === personaId);
      }});

      renderPersonaExperience();
      renderAgents();
    }}

    // Switch to Persona Archetype from Domain View Card Chip
    function switchToPersonaArchetype(personaId) {{
      setViewMode('persona');
      selectPersona(personaId);
      if (viewModeBar) {{
        viewModeBar.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}
    }}

    // Day in the Life Collapsible Toggle
    function toggleDitlStoryboard() {{
      ditlCollapsed = !ditlCollapsed;
      const grid = document.getElementById('ditlGrid');
      const btn = document.getElementById('ditlToggleBtn');
      if (grid) {{
        grid.style.display = ditlCollapsed ? 'none' : 'grid';
      }}
      if (btn) {{
        btn.textContent = ditlCollapsed ? '▼ Show Storyboard' : '▲ Hide Storyboard';
      }}
    }}

    // Render Persona Experience Header & Day in the Life Storyboard
    function renderPersonaExperience() {{
      if (!personaExperienceContainer) return;

      if (viewMode !== 'persona') {{
        personaExperienceContainer.style.display = 'none';
        personaExperienceContainer.innerHTML = '';
        return;
      }}

      personaExperienceContainer.style.display = 'block';

      if (activePersona === 'all') {{
        // State A: 10-Persona Transformation Overview Grid
        const query = searchQuery.toLowerCase().trim();
        const filteredPersonas = PERSONA_ARCHETYPES.filter(p => {{
          if (!query) return true;
          const pool = [
            p.title,
            p.subtitle,
            p.roles_summary,
            p.hours_saved,
            p.decision_speed,
            p.automated_label || '',
            p.augmented_label || '',
            ...(p.day_in_the_life || []).map(s => [
              s.stage,
              s.without_agents,
              s.with_agents,
              s.automated_what,
              s.augmented_what,
              ...(s.task_bundle || []).map(t => t.label)
            ].join(' '))
          ].join(' ').toLowerCase();
          return pool.includes(query);
        }});

        if (filteredPersonas.length === 0) {{
          personaExperienceContainer.innerHTML = `
            <div class="persona-overview-header">
              <h2 class="persona-overview-title">
                <span>👤</span> 10 Retail Enterprise Persona Archetypes
              </h2>
              <p class="persona-overview-subtitle">
                Explore how Gemini Enterprise Agents transform daily workflows across retail leadership, merchandising, supply chain, store operations, and digital roles.
              </p>
            </div>
            <div class="no-results" style="display: block; padding: 48px 24px; text-align: center;">
              <div style="font-size: 2.5rem; margin-bottom: 12px;">🔍</div>
              <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 8px;">No matching persona archetypes found</h3>
              <p style="color: var(--text-secondary); margin-bottom: 16px;">Try adjusting your search terms or clearing the search filter.</p>
              <button class="btn-persona-cta" onclick="resetFilters()" style="margin: 0 auto;">Clear Search</button>
            </div>
          `;
          return;
        }}

        const cardsHtml = filteredPersonas.map(p => {{
          const count = AGENTS_DATA.filter(a => (a.persona_archetypes || []).includes(p.id)).length;
          const dist = p.task_distribution || {{
            unchanged_pct: 25,
            augmented_pct: p.augmented_pct || 35,
            automated_pct: p.automated_pct || 25,
            new_ai_pct: 10,
            retired_pct: 5
          }};
          return `
            <div class="persona-overview-card" data-persona-id="${{p.id}}">
              <div class="persona-card-header">
                <div class="persona-card-title-wrap">
                  <span class="persona-card-icon">${{p.icon}}</span>
                  <h3 class="persona-card-title">${{htmlEscape(p.title)}}</h3>
                </div>
                <span class="persona-agent-badge">${{count}} agents</span>
              </div>
              <div class="persona-card-subtitle">${{htmlEscape(p.subtitle)}}</div>
              <p class="persona-card-summary">${{htmlEscape(p.roles_summary)}}</p>

              <div class="persona-metrics-row">
                <span class="persona-metric-pill">⏱️ <strong>${{htmlEscape(p.hours_saved)}}</strong></span>
                <span class="persona-metric-pill">⚡ <strong>${{htmlEscape(p.decision_speed)}}</strong></span>
              </div>

              <div class="task-dist-container">
                <div class="task-dist-labels">
                  <span>🟫 Unchanged</span>
                  <span>🟪 Augmented</span>
                  <span>🟦 Automated</span>
                  <span>🟨 New AI</span>
                  <span>◌ Retired</span>
                </div>
                <div class="task-dist-bar">
                  <div class="seg-unchanged" style="width: ${{dist.unchanged_pct}}%;" title="Unchanged: ${{dist.unchanged_pct}}%"></div>
                  <div class="seg-augmented" style="width: ${{dist.augmented_pct}}%;" title="Augmented: ${{dist.augmented_pct}}%"></div>
                  <div class="seg-automated" style="width: ${{dist.automated_pct}}%;" title="Automated: ${{dist.automated_pct}}%"></div>
                  <div class="seg-new" style="width: ${{dist.new_ai_pct}}%;" title="New AI Tasks: ${{dist.new_ai_pct}}%"></div>
                  <div class="seg-retired" style="width: ${{dist.retired_pct}}%;" title="Retired Manual Tasks: ${{dist.retired_pct}}%"></div>
                </div>
              </div>

              <button class="btn-persona-cta" onclick="selectPersona('${{p.id}}')">
                <span>🌅</span> View Day in the Life →
              </button>
            </div>
          `;
        }}).join('');

        personaExperienceContainer.innerHTML = `
          <div class="persona-overview-header">
            <h2 class="persona-overview-title">
              <span>👤</span> 10 Retail Enterprise Persona Archetypes
            </h2>
            <p class="persona-overview-subtitle">
              Explore how Gemini Enterprise Agents transform daily workflows across retail leadership, merchandising, supply chain, store operations, and digital roles.
            </p>
            <div class="task-bundle-key-bar">
              <span class="task-bundle-key-title">5-State Task Bundle Key:</span>
              <div class="task-bundle-key-items">
                <span class="task-bundle-key-chip key-unchanged">🟫 1. Tasks Unchanged</span>
                <span class="task-bundle-key-chip key-augmented">🟪 2. Tasks Augmented</span>
                <span class="task-bundle-key-chip key-automated">🟦 3. Tasks Automated</span>
                <span class="task-bundle-key-chip key-new">🟨 4. New Tasks Created by AI</span>
                <span class="task-bundle-key-chip key-retired">◌ 5. Retired Manual Tasks</span>
              </div>
            </div>
          </div>
          <div class="persona-overview-grid" id="personaOverviewGrid">
            ${{cardsHtml}}
          </div>
        `;
        runMotionChoreography(personaExperienceContainer);
      }} else {{
        // State B: Day-in-the-Life Storyboard for specific archetype
        const p = PERSONA_MAP[activePersona];
        if (!p) return;

        const count = AGENTS_DATA.filter(a => (a.persona_archetypes || []).includes(p.id)).length;

        const stagesHtml = (p.day_in_the_life || []).map((stage, stageIdx) => {{
          // 1. Task Bundle (6 tiles)
          const bundle = stage.task_bundle || [];
          const taskTilesHtml = bundle.map((t, tileIdx) => {{
            if (ditlStateMode === 'before') {{
              const isNew = t.state === 'new';
              const stateClass = isNew ? 'state-dormant' : 'state-unchanged';
              const tagText = isNew ? '◌ NOT PERFORMED' : '🟫 MANUAL STEP';
              return `
                <div class="task-tile ${{stateClass}}" data-task-state="${{t.state}}" data-task-idx="${{tileIdx}}">
                  <div class="task-tile-top">
                    <span class="task-state-tag">${{tagText}}</span>
                  </div>
                  <div class="task-tile-label">${{htmlEscape(t.label)}}</div>
                </div>
              `;
            }} else {{
              let stateTag = '🟫 UNCHANGED';
              if (t.state === 'augmented') stateTag = '🟪 AUGMENTED';
              else if (t.state === 'automated') stateTag = '🟦 AUTOMATED';
              else if (t.state === 'new') stateTag = '🟨 NEW AI TASK';
              else if (t.state === 'retired') stateTag = '◌ RETIRED';

              const stepIndicesStr = (t.step_indices || []).join(',');
              const stepRefHtml = t.steps_label ? `<span class="task-step-ref">${{htmlEscape(t.steps_label)}}</span>` : '';

              return `
                <div class="task-tile state-${{t.state}}" data-task-state="${{t.state}}" data-task-idx="${{tileIdx}}" data-steps="${{stepIndicesStr}}" tabindex="0">
                  <div class="task-tile-top">
                    <span class="task-state-tag">${{stateTag}}</span>
                    ${{stepRefHtml}}
                  </div>
                  <div class="task-tile-label">${{htmlEscape(t.label)}}</div>
                  <div class="task-tile-footer">
                    <span class="task-pin-chip">Click to pin focus</span>
                  </div>
                </div>
              `;
            }}
          }}).join('');

          // 2. Option A — Connected Orchestration Conduit (Only when ditlStateMode === 'after')
          let bentoFlowHtml = '';
          if (ditlStateMode === 'after') {{
            let flow = stage.agent_flow || [];
            if (!flow.length && stage.featured_agents) {{
              flow = stage.featured_agents.map((slug, idx) => ({{
                step: idx + 1,
                step_code: String(idx + 1).padStart(2, '0'),
                slug: slug,
                action_tag: 'EXECUTES ANALYTICS'
              }}));
            }}

            const conduitNodesHtml = flow.map((f, idx) => {{
              const agent = AGENTS_DATA.find(a => a.name === f.slug);
              const agentLabel = agent ? agent.display_name : f.slug.replace(/_/g, ' ');
              const connector = idx < flow.length - 1 ? '→' : '✓';

              return `
                <div class="conduit-node" data-step="${{f.step}}">
                  <div class="conduit-medallion-row">
                    <div class="conduit-medallion">${{htmlEscape(f.step_code)}}</div>
                    ${{idx < flow.length - 1 ? `<span class="conduit-arrow">${{connector}}</span>` : ''}}
                  </div>
                  <div class="conduit-step-card flow-step-card" data-step="${{f.step}}">
                    <div class="flow-step-top">
                      <span class="flow-step-badge">STEP ${{htmlEscape(f.step_code)}}</span>
                      <span class="conduit-linked-badge">LINKED</span>
                    </div>
                    <div class="flow-step-action">
                      <span>${{htmlEscape(f.action_tag)}}</span>
                    </div>
                    <div class="flow-step-agent" title="${{htmlEscape(agentLabel)}}">${{htmlEscape(agentLabel)}}</div>
                    <button type="button" class="conduit-demo-btn" onclick="openVideoModal('${{f.slug}}')" title="Watch 1080p Demo for ${{htmlEscape(agentLabel)}}">
                      <span>🎬</span> Watch Demo
                    </button>
                  </div>
                </div>
              `;
            }}).join('');

            bentoFlowHtml = `
              <div class="stage-flow-section">
                <div class="stage-flow-header">
                  <span class="stage-flow-title">
                    <span class="motion-pulse-dot"></span> Recommended Agent Execution Flow (${{flow.length}} Sequenced Steps)
                  </span>
                  <span class="stage-flow-hint">⚡ Hover or click any task, state pill, or step to spotlight linked agents · Click 🎬 Watch Demo for 1080p video</span>
                </div>
                <div class="flow-conduit-track" style="--conduit-cols: ${{flow.length}};">
                  <div class="conduit-rail-line">
                    <div class="conduit-rail-fill motion-rail-fill"></div>
                  </div>
                  ${{conduitNodesHtml}}
                </div>
                <div class="flow-bento-grid" style="display: none;">
                  <!-- Maintained for bento grid selector compatibility -->
                </div>
              </div>
            `;
          }}

          // 3. Stage Header Horizon Badge & Maximize Stage Button
          const horizonBadge = ditlStateMode === 'before'
            ? `<span class="ditl-stage-horizon manual-mode">⏱️ Manual: ${{htmlEscape(stage.time_before)}}</span>`
            : `<span class="ditl-stage-horizon">⏱️ ${{htmlEscape(stage.time_before)}} → ⚡ ${{htmlEscape(stage.time_after)}}</span>`;

          return `
            <div class="ditl-stage-card">
              <div class="ditl-stage-top">
                <span class="ditl-time-stage">📋 ${{htmlEscape(stage.time)}} · ${{htmlEscape(stage.stage)}}</span>
                <div class="ditl-stage-top-right">
                  ${{horizonBadge}}
                  <button type="button" class="stage-maximize-btn" onclick="openStageTheater(${{stageIdx}})" title="Maximize stage in Full-Screen Focus Theater">
                    <span>⤢</span> Maximize Stage
                  </button>
                </div>
              </div>

              <div class="task-bundle-wrap">
                <div class="task-bundle-title">
                  <span>${{ditlStateMode === 'before' ? 'Manual Task Bundle (Baseline)' : '5-State Task Transformation Bundle (6 Tasks)'}}</span>
                  <span>${{ditlStateMode === 'before' ? '⏱️ Legacy Manual Effort' : '⚡ AI-Augmented Horizon'}}</span>
                </div>
                <div class="task-bundle-grid">
                  ${{taskTilesHtml}}
                </div>
              </div>

              ${{bentoFlowHtml}}
            </div>
          `;
        }}).join('');

        personaExperienceContainer.innerHTML = `
          <div class="ditl-banner">
            <div class="ditl-header">
              <div class="ditl-header-left">
                <h2 class="ditl-title">
                  <span>${{p.icon}}</span> ${{htmlEscape(p.title)}} — Day in the Life
                </h2>
                <div class="ditl-subtitle">${{htmlEscape(p.subtitle)}}</div>
                <div class="ditl-stat-pills">
                  <span class="ditl-stat-pill">⏱️ <strong>${{htmlEscape(p.hours_saved)}}</strong></span>
                  <span class="ditl-stat-pill">⚡ <strong>${{htmlEscape(p.decision_speed)}}</strong></span>
                  <span class="ditl-stat-pill">🤖 <strong>${{htmlEscape(p.automated_label || 'Automated: Data, SQL & Visuals')}}</strong></span>
                  <span class="ditl-stat-pill">✨ <strong>${{htmlEscape(p.augmented_label || 'Augmented: Strategy & Sign-Off')}}</strong></span>
                  <span class="ditl-stat-pill">👥 <strong>${{count}} Agents</strong></span>
                </div>
              </div>
              <div class="ditl-header-right">
                <button class="btn-header" id="backToAllPersonasBtn" onclick="selectPersona('all')">
                  <span>👥</span> ← All Personas Overview
                </button>
                <button class="btn-header" id="ditlToggleBtn" onclick="toggleDitlStoryboard()">
                  ${{ditlCollapsed ? '▼ Show Storyboard' : '▲ Hide Storyboard'}}
                </button>
              </div>
            </div>

            <div class="ditl-controls-row">
              <div class="ditl-state-switcher">
                <button type="button" class="ditl-state-btn ${{ditlStateMode === 'before' ? 'active-before' : ''}}" onclick="setDitlStateMode('before')">
                  <span class="mode-radio-dot">${{ditlStateMode === 'before' ? '●' : '○'}}</span> Before Agents (Manual Baseline)
                </button>
                <button type="button" class="ditl-state-btn ${{ditlStateMode === 'after' ? 'active-after' : ''}}" onclick="setDitlStateMode('after')">
                  <span class="mode-radio-dot">${{ditlStateMode === 'after' ? '●' : '○'}}</span> After Agents (5-State Task Bundle + Agent Flow)
                </button>
              </div>

              <div class="task-bundle-key-bar" style="margin: 0; padding: 6px 12px;">
                <span class="task-bundle-key-title">5-State Task Bundle Key:</span>
                <div class="task-bundle-key-items">
                  <button type="button" class="task-bundle-key-chip key-unchanged ditl-state-filter-pill ${{activeTaskStateFilter === 'unchanged' ? 'active-filter' : ''}}" data-filter-state="unchanged" onclick="toggleTaskStateFilter('unchanged')" onmouseenter="previewTaskStateFilter('unchanged')" onmouseleave="clearPreviewTaskStateFilter()">
                    <span class="pill-check-ind">${{activeTaskStateFilter === 'unchanged' ? '✓' : '○'}}</span> 🟫 1. Tasks Unchanged
                  </button>
                  <button type="button" class="task-bundle-key-chip key-augmented ditl-state-filter-pill ${{activeTaskStateFilter === 'augmented' ? 'active-filter' : ''}}" data-filter-state="augmented" onclick="toggleTaskStateFilter('augmented')" onmouseenter="previewTaskStateFilter('augmented')" onmouseleave="clearPreviewTaskStateFilter()">
                    <span class="pill-check-ind">${{activeTaskStateFilter === 'augmented' ? '✓' : '○'}}</span> 🟪 2. Tasks Augmented
                  </button>
                  <button type="button" class="task-bundle-key-chip key-automated ditl-state-filter-pill ${{activeTaskStateFilter === 'automated' ? 'active-filter' : ''}}" data-filter-state="automated" onclick="toggleTaskStateFilter('automated')" onmouseenter="previewTaskStateFilter('automated')" onmouseleave="clearPreviewTaskStateFilter()">
                    <span class="pill-check-ind">${{activeTaskStateFilter === 'automated' ? '✓' : '○'}}</span> 🟦 3. Tasks Automated
                  </button>
                  <button type="button" class="task-bundle-key-chip key-new ditl-state-filter-pill ${{activeTaskStateFilter === 'new' ? 'active-filter' : ''}}" data-filter-state="new" onclick="toggleTaskStateFilter('new')" onmouseenter="previewTaskStateFilter('new')" onmouseleave="clearPreviewTaskStateFilter()">
                    <span class="pill-check-ind">${{activeTaskStateFilter === 'new' ? '✓' : '○'}}</span> 🟨 4. New Tasks Created by AI
                  </button>
                  <button type="button" class="task-bundle-key-chip key-retired ditl-state-filter-pill ${{activeTaskStateFilter === 'retired' ? 'active-filter' : ''}}" data-filter-state="retired" onclick="toggleTaskStateFilter('retired')" onmouseenter="previewTaskStateFilter('retired')" onmouseleave="clearPreviewTaskStateFilter()">
                    <span class="pill-check-ind">${{activeTaskStateFilter === 'retired' ? '✓' : '○'}}</span> ◌ 5. Retired Manual Tasks
                  </button>
                  <button type="button" class="filter-reset-pill" onclick="resetTaskStateFilter()" style="display: ${{activeTaskStateFilter ? 'inline-flex' : 'none'}};">
                    ✕ Reset Filter
                  </button>
                </div>
              </div>
            </div>

            <div class="ditl-grid" id="ditlGrid" style="${{ditlCollapsed ? 'display: none;' : ''}}">
              ${{stagesHtml}}
            </div>
          </div>
        `;
        runMotionChoreography(personaExperienceContainer);
        if (activePersona !== 'all') {{
          bindPipelineSpotlightEvents(personaExperienceContainer);
          if (activeTaskStateFilter) {{
            applyProminentSpotlight();
          }}
        }}
      }}
    }}

    // Render Cards
    function renderAgents() {{
      if (viewMode === 'persona') {{
        if (agentGrid) agentGrid.style.display = 'none';
        if (resultsBar) resultsBar.style.display = 'none';
        if (noResults) noResults.style.display = 'none';
        return;
      }}

      if (resultsBar) resultsBar.style.display = 'flex';
      if (agentGrid) agentGrid.style.display = 'grid';

      const query = searchQuery.toLowerCase().trim();
      
      const filtered = AGENTS_DATA.filter(agent => {{
        const matchesDomain = activeDomain === 'all' || agent.domain === activeDomain;
        if (!matchesDomain) return false;

        if (!query) return true;

        const personaText = (agent.personas || []).map(p => p.title + ' ' + (p.description || '')).join(' ');
        const transformText = agent.transformation ? 
          [agent.transformation.without_agent, agent.transformation.with_agent, agent.transformation.automated, agent.transformation.augmented].join(' ') : '';

        const textPool = [
          agent.display_name,
          agent.name,
          agent.domain_display,
          agent.description,
          agent.location,
          personaText,
          transformText,
          ...(agent.kpis || []),
          ...(agent.prompts || []),
          ...(agent.tables || [])
        ].join(' ').toLowerCase();

        return textPool.includes(query);
      }});

      resultsCount.innerHTML = `Showing <strong>${{filtered.length}}</strong> of ${{AGENTS_DATA.length}} enterprise agents`;

      if (filtered.length === 0) {{
        agentGrid.innerHTML = '';
        noResults.style.display = 'block';
        return;
      }}

      noResults.style.display = 'none';

      agentGrid.innerHTML = filtered.map(agent => {{
        const kpiPills = (agent.kpis || []).map(kpi => 
          `<span class="kpi-pill">🎯 ${{htmlEscape(kpi)}}</span>`
        ).join('');

        const promptItems = (agent.prompts || []).map((prompt, idx) => 
          `<div class="prompt-item">"${{htmlEscape(prompt)}}"</div>`
        ).join('');

        // Persona Chips for Domain View
        const personaChips = (agent.personas || []).slice(0, 3).map(p => 
          `<button class="persona-chip" onclick="switchToPersonaArchetype('${{p.archetype}}')" title="${{htmlEscape(p.title)}}: ${{htmlEscape(p.description)}}">
            <span>👤</span> ${{htmlEscape(p.title)}}
          </button>`
        ).join('');

        return `
          <div class="agent-card" data-agent-id="${{agent.id}}">
            <div class="card-top">
              <div class="card-badges">
                <span class="badge-domain">${{agent.icon}} ${{htmlEscape(agent.domain_display)}}</span>
                <span class="badge-region">${{agent.location}}</span>
              </div>
            </div>
            <h3 class="card-title">${{htmlEscape(agent.display_name)}}</h3>
            <p class="card-desc">${{htmlEscape(agent.description)}}</p>

            ${{personaChips ? `<div class="persona-row">${{personaChips}}</div>` : ''}}

            ${{kpiPills ? `<div class="kpi-row">${{kpiPills}}</div>` : ''}}

            ${{promptItems ? `
              <div class="prompts-container">
                <button class="prompts-toggle" onclick="togglePrompts(this)">
                  <span>💬 Sample Business Questions (${{agent.prompts.length}})</span>
                  <span class="toggle-icon">▼</span>
                </button>
                <div class="prompts-list">
                  ${{promptItems}}
                </div>
              </div>
            ` : ''}}

            <div class="card-actions">
              <button class="btn-watch" onclick="openVideoModal('${{agent.name}}')">
                <span>🎬</span> Watch Demo
              </button>
              <a href="${{agent.demo_html}}" target="_blank" rel="noopener noreferrer" class="btn-showcase" title="Open Dedicated Showcase Player">
                <span>📄</span> Showcase
              </a>
              <a href="${{agent.readme}}" target="_blank" rel="noopener noreferrer" class="btn-doc" title="View Technical README">
                <span>📖</span>
              </a>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function togglePrompts(btn) {{
      const list = btn.nextElementSibling;
      const icon = btn.querySelector('.toggle-icon');
      if (list.classList.contains('open')) {{
        list.classList.remove('open');
        icon.textContent = '▼';
      }} else {{
        list.classList.add('open');
        icon.textContent = '▲';
      }}
    }}

    function htmlEscape(str) {{
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }}

    // Search input handler
    searchInput.addEventListener('input', (e) => {{
      searchQuery = e.target.value;
      searchClear.style.display = searchQuery ? 'block' : 'none';
      renderPersonaExperience();
      renderAgents();
    }});

    searchClear.addEventListener('click', () => {{
      searchInput.value = '';
      searchQuery = '';
      searchClear.style.display = 'none';
      renderPersonaExperience();
      renderAgents();
      searchInput.focus();
    }});

    // View Mode Bar Handler
    if (viewModeBar) {{
      viewModeBar.addEventListener('click', (e) => {{
        const btn = e.target.closest('.view-mode-btn');
        if (!btn || !btn.dataset.view) return;
        setViewMode(btn.dataset.view);
      }});
    }}

    // Domain Filter Handler
    domainPills.addEventListener('click', (e) => {{
      const btn = e.target.closest('.domain-btn');
      if (!btn || !btn.dataset.domain) return;

      document.querySelectorAll('#domainPills .domain-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      activeDomain = btn.dataset.domain;
      renderAgents();
    }});

    // Persona Filter Handler
    if (personaPills) {{
      personaPills.addEventListener('click', (e) => {{
        const btn = e.target.closest('.persona-btn');
        if (!btn || !btn.dataset.persona) return;

        selectPersona(btn.dataset.persona);
      }});
    }}

    function resetFilters() {{
      searchInput.value = '';
      searchQuery = '';
      searchClear.style.display = 'none';
      activeDomain = 'all';
      activePersona = 'all';
      document.querySelectorAll('#domainPills .domain-btn').forEach(b => {{
        b.classList.toggle('active', b.dataset.domain === 'all');
      }});
      document.querySelectorAll('#personaPills .persona-btn').forEach(b => {{
        b.classList.toggle('active', b.dataset.persona === 'all');
      }});
      setViewMode('domain');
    }}

    // Video Modal Handlers
    function openVideoModal(agentName) {{
      const agent = AGENTS_DATA.find(a => a.name === agentName);
      if (!agent) return;

      modalAgentTitle.textContent = agent.display_name;
      modalDomainBadge.innerHTML = `${{agent.icon}} ${{agent.domain_display}}`;
      modalRegionBadge.textContent = agent.location;
      modalVideo.src = `${{agent.demo_mp4}}#t=10`;
      modalDownloadBtn.href = agent.demo_mp4;
      modalShowcaseBtn.href = agent.demo_html;

      if (agent.prompts && agent.prompts.length >= 3) {{
        modalTurnsList.innerHTML = `
          <li><strong>Turn 1 (Data Insights):</strong> "${{htmlEscape(agent.prompts[0])}}"</li>
          <li><strong>Turn 2 (Market Grounding):</strong> "${{htmlEscape(agent.prompts[1])}}"</li>
          <li><strong>Turn 3 (Visual Analytics):</strong> "${{htmlEscape(agent.prompts[2])}}"</li>
          <li><strong>Turn 4 (Canvas Presentation):</strong> Executive 4-slide slide deck generated in Gemini Enterprise Canvas.</li>
        `;
      }}

      videoModal.classList.add('open');
      document.body.style.overflow = 'hidden';
      modalVideo.play().catch(() => {{}});
    }}

    function closeVideoModal() {{
      videoModal.classList.remove('open');
      document.body.style.overflow = '';
      modalVideo.pause();
      modalVideo.src = '';
    }}

    modalCloseBtn.addEventListener('click', closeVideoModal);
    videoModal.addEventListener('click', (e) => {{
      if (e.target === videoModal) closeVideoModal();
    }});

    // Architecture Modal Handlers
    function openArchModal() {{
      archModal.classList.add('open');
      document.body.style.overflow = 'hidden';
    }}

    function closeArchModal() {{
      archModal.classList.remove('open');
      document.body.style.overflow = '';
    }}

    archBtn.addEventListener('click', openArchModal);
    archCloseBtn.addEventListener('click', closeArchModal);
    archOkBtn.addEventListener('click', closeArchModal);
    archModal.addEventListener('click', (e) => {{
      if (e.target === archModal) closeArchModal();
    }});

    if (stageTheaterModal) {{
      stageTheaterModal.addEventListener('click', (e) => {{
        if (e.target === stageTheaterModal) closeStageTheater();
      }});
    }}

    // ESC key listener for modals
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') {{
        if (videoModal && videoModal.classList.contains('open')) {{
          closeVideoModal();
        }} else if (stageTheaterModal && stageTheaterModal.classList.contains('open')) {{
          closeStageTheater();
        }} else if (archModal && archModal.classList.contains('open')) {{
          closeArchModal();
        }}
      }}
    }});

    // Initial Load
    initTheme();
    renderPersonaExperience();
    renderAgents();
  </script>
</body>
</html>
"""


def main():
    print("=" * 70)
    print("🚀 GENERATING RETAIL ENTERPRISE AGENTS PORTAL (index.html)")
    print("=" * 70)
    
    registry_file = REPO_ROOT / "_shared" / "table_registry.yaml"
    if not registry_file.exists():
        print(f"❌ Error: {registry_file} not found!")
        sys.exit(1)
        
    registry = yaml.safe_load(registry_file.read_text(encoding="utf-8"))
    reg_agents = registry.get("agents", {})
    reg_domains = registry.get("domains", {})
    
    print(f"📋 Found {len(reg_agents)} registered agents across {len(reg_domains)} domains in table_registry.yaml.")
    
    agents_data = []
    for agent_name, agent_info in reg_agents.items():
        domain = agent_info.get("domain", "")
        if not domain:
            print(f"⚠️ Warning: Agent '{agent_name}' missing domain field in registry.")
            continue
        meta = extract_agent_metadata(agent_name, domain, agent_info, REPO_ROOT)
        agents_data.append(meta)
        
    # Sort agents by domain order, then display name
    domain_rank = {d: i for i, d in enumerate(DOMAIN_ORDER)}
    agents_data.sort(key=lambda a: (domain_rank.get(a["domain"], 99), a["display_name"]))
    
    print(f"✨ Compiled metadata for {len(agents_data)} agents.")
    
    portal_html = build_portal_html(agents_data, reg_domains)
    
    output_file = REPO_ROOT / "index.html"
    output_file.write_text(portal_html, encoding="utf-8")
    
    file_size_kb = output_file.stat().st_size / 1024
    print(f"✅ Successfully generated {output_file} ({file_size_kb:.1f} KB).")
    print("=" * 70)


if __name__ == "__main__":
    main()
