#!/usr/bin/env python3
"""
generate_demo_html.py — Standalone HTML Demo Video Showcase Generator

Generates high-fidelity, responsive HTML5 video showcase pages for recorded agent demo MP4s
matching the standard Gemini Enterprise demo player design (dual light/dark theme, navigation bar,
badge row, metadata grid, multi-turn conversation flow breakdown, and GitHub links).

Usage:
    uv run python _shared/scripts/generate_demo_html.py --name cart_checkout_analytics
    uv run python _shared/scripts/generate_demo_html.py --domain merchandising --all
    uv run python _shared/scripts/generate_demo_html.py --all
"""

import argparse
from pathlib import Path
import re
import sys
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from _shared.scripts.prompt_parser import parse_agent_prompts, resolve_agent_domain

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

DOMAIN_TITLES = {
    "merchandising": "Merchandising Domain",
    "supply_chain": "Supply Chain & Logistics Domain",
    "store_operations": "Store Operations Domain",
    "e_commerce": "E-Commerce Domain",
    "marketing": "Marketing & Retail Media Domain",
    "finance": "Finance, Real Estate & Accounting Domain",
    "customer_care": "Customer Care & Experience Domain",
    "sustainability_compliance": "Sustainability, ESG & Compliance Domain",
    "human_resources": "Human Resources & Workforce Domain",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
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
      --bg-card: #1e293b;
      --bg-surface: #0f172a;
      --border-color: #334155;
      --border-faint: rgba(255, 255, 255, 0.14);
      --border-subtle: #1e293b;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #94a3b8;
      --accent-blue: #38bdf8;
      --accent-indigo: #818cf8;
      --badge-bg: rgba(56, 189, 248, 0.12);
      --badge-border: rgba(56, 189, 248, 0.28);
      --badge-text: #38bdf8;
      --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
    }}

    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-card: #ffffff;
      --bg-surface: #f1f5f9;
      --border-color: #cbd5e1;
      --border-faint: #cbd5e1;
      --border-subtle: #e2e8f0;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #475569;
      --accent-blue: #0284c7;
      --accent-indigo: #6366f1;
      --badge-bg: #e0f2fe;
      --badge-border: #bae6fd;
      --badge-text: #0284c7;
      --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Google Sans', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px 40px;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    .container {{
      max-width: 1080px;
      width: 100%;
      background: var(--bg-card);
      border: 1px solid var(--border-faint);
      border-radius: 16px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}

    /* Top Nav Bar */
    .top-nav {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border-faint);
    }}

    .nav-back-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--accent-blue);
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 600;
      transition: color 0.15s ease;
    }}

    .nav-back-link:hover {{
      text-decoration: underline;
    }}

    .theme-toggle-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .theme-toggle-btn:hover {{
      border-color: var(--accent-blue);
      color: var(--accent-blue);
    }}

    header {{
      margin-bottom: 20px;
    }}

    .badge-row {{
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: 9999px;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--badge-text);
    }}

    h1 {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.65rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 10px;
      text-wrap: balance;
    }}

    p.subtitle {{
      color: var(--text-secondary);
      font-size: 0.95rem;
      line-height: 1.5;
      max-width: 68ch;
    }}

    .video-wrapper {{
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #000;
      border: 1px solid var(--border-faint);
      border-radius: 12px;
      overflow: hidden;
      margin: 20px 0;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }}

    .video-status-overlay {{
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      background: #0b1120;
      color: #e2e8f0;
      font-size: 0.9rem;
      z-index: 2;
    }}

    #videoLoadingState {{
      pointer-events: none;
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
      border-color: var(--accent-blue);
    }}

    video {{
      width: 100%;
      display: block;
      max-height: 620px;
    }}

    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      background: transparent;
      border-top: 1px solid var(--border-faint);
      border-bottom: 1px solid var(--border-faint);
      border-radius: 0;
      padding: 16px 0;
      margin-bottom: 24px;
    }}

    .meta-item {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .meta-label {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .meta-value {{
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-primary);
    }}

    .turns-section {{
      background: transparent;
      border-top: 1px solid var(--border-faint);
      border-bottom: 1px solid var(--border-faint);
      border-radius: 0;
      padding: 20px 0;
      margin-bottom: 24px;
    }}

    .turns-section h2 {{
      font-family: 'Google Sans', sans-serif;
      font-size: 1.1rem;
      margin-bottom: 12px;
      color: var(--accent-indigo);
      text-wrap: balance;
    }}

    .turn-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .turn-list li {{
      font-size: 0.9rem;
      line-height: 1.5;
      color: var(--text-secondary);
      max-width: 72ch;
    }}

    .turn-list strong {{
      color: var(--text-primary);
    }}

    footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding-top: 16px;
      border-top: 1px solid var(--border-color);
    }}

    .btn-link {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--accent-blue);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      transition: color 0.15s ease;
    }}

    .btn-link:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div class="container">
    <nav class="top-nav">
      <a class="nav-back-link" href="../../../index.html">
        <span>←</span> Back to All Enterprise Agents
      </a>
      <button id="themeToggleBtn" class="theme-toggle-btn" aria-label="Toggle light/dark theme" aria-pressed="false">
        <span id="themeIcon">☀️</span> <span id="themeText">Light</span>
      </button>
    </nav>

    <header>
      <div class="badge-row">
        <span class="badge">Retail Enterprise Agents</span>
        <span class="badge">{domain_badge}</span>
        <span class="badge">Gemini Enterprise</span>
      </div>
      <h1>{icon} {display_name}</h1>
      <p class="subtitle">
        {subtitle}
      </p>
    </header>

    <div class="video-wrapper">
      <div id="videoLoadingState" class="video-status-overlay">Loading 1080p walkthrough…</div>
      <div id="videoErrorState" class="video-status-overlay" style="display: none;">
        <span>Unable to stream video preview.</span>
        <a id="videoFallbackLink" href="{video_filename}" download class="btn-header">Download MP4</a>
      </div>
      <video id="demoVideo" controls autoplay muted playsinline preload="auto">
        <source src="{video_filename}#t=10" type="video/mp4">
        Your browser does not support HTML5 video.
      </video>
    </div>

    <script>
      (function() {{
        const video = document.getElementById('demoVideo');
        const loadingState = document.getElementById('videoLoadingState');
        const errorState = document.getElementById('videoErrorState');

        if (video) {{
          let hasSeeked = false;

          const seekToOffset = () => {{
            if (!hasSeeked && video.currentTime < 10) {{
              hasSeeked = true;
              video.currentTime = 10;
            }}
          }};

          const hideLoading = () => {{
            if (loadingState) loadingState.style.display = 'none';
          }};

          const showLoading = () => {{
            if (loadingState) loadingState.style.display = 'flex';
          }};

          const showError = () => {{
            if (loadingState) loadingState.style.display = 'none';
            if (errorState) errorState.style.display = 'flex';
          }};

          if (video.readyState >= 2) hideLoading();

          video.addEventListener('loadedmetadata', seekToOffset);
          video.addEventListener('loadeddata', () => {{
            hideLoading();
            seekToOffset();
          }});
          video.addEventListener('canplay', () => {{
            hideLoading();
            seekToOffset();
          }});
          video.addEventListener('waiting', showLoading);
          video.addEventListener('playing', hideLoading);
          video.addEventListener('timeupdate', function onFirstTick() {{
            if (!hasSeeked && video.currentTime < 10) {{
              seekToOffset();
            }}
          }});

          video.addEventListener('error', showError);
          const videoSource = video.querySelector('source');
          if (videoSource) {{
            videoSource.addEventListener('error', showError);
          }}
        }}

        // Theme Toggle Logic
        const themeToggleBtn = document.getElementById('themeToggleBtn');
        const themeIcon = document.getElementById('themeIcon');
        const themeText = document.getElementById('themeText');

        function updateThemeUI(theme) {{
          const isLight = theme === 'light';
          if (themeToggleBtn) {{
            themeToggleBtn.setAttribute('aria-pressed', isLight ? 'true' : 'false');
          }}
          if (isLight) {{
            themeIcon.textContent = '🌙';
            themeText.textContent = 'Dark';
          }} else {{
            themeIcon.textContent = '☀️';
            themeText.textContent = 'Light';
          }}
        }}

        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        updateThemeUI(currentTheme);

        if (themeToggleBtn) {{
          themeToggleBtn.addEventListener('click', () => {{
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('retail_agents_theme', next);
            updateThemeUI(next);
          }});
        }}
      }})();
    </script>

    <div class="meta-grid">
      <div class="meta-item">
        <span class="meta-label">Duration</span>
        <span class="meta-value">{duration_text}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Resolution</span>
        <span class="meta-value">1080p Full HD (1920×1080)</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">UI Scaling</span>
        <span class="meta-value">1.25x High-DPI Scaled Text</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Model Runtime</span>
        <span class="meta-value">gemini-3.5-flash (Vertex AI)</span>
      </div>
    </div>

    <div class="turns-section">
      <h2>📋 Multi-Turn Conversation Flow</h2>
      <ul class="turn-list">
{turn_items_html}
      </ul>
    </div>

    <footer>
      <a class="btn-link" href="https://github.com/rajanm/retail-enterprise-agents/tree/master/domains/{domain}/agents/{agent_name}">
        ← View Agent Code & Documentation on GitHub
      </a>
      <a class="btn-link" href="https://github.com/rajanm/retail-enterprise-agents">
        🏠 Retail Enterprise Agents Repository
      </a>
    </footer>
  </div>
</body>
</html>
"""


def clean_subtitle_markdown(text: str) -> str:
    """Removes inline Markdown syntax (**bold**, `code`, links) from subtitle text."""
    cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    cleaned = cleaned.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", cleaned).strip()


def get_agent_info(agent_name: str, domain: str) -> dict:
    """Extracts agent metadata, display name, and subtitle description."""
    agent_dir = REPO_ROOT / "domains" / domain / "agents" / agent_name
    readme_path = agent_dir / "README.md"
    root_agent_path = agent_dir / "root_agent.yaml"
    
    display_name = agent_name.replace("_", " ").title()
    subtitle = "Authentic multi-turn interactive video recording showcasing agent @mention invocation, BigQuery conversational analytics SQL synthesis, Google Search market grounding, and visual chart artifact generation."
    
    if readme_path.exists():
        try:
            content = readme_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                if "**Gemini Enterprise display name:**" in line:
                    display_name = line.split("**Gemini Enterprise display name:**")[-1].strip()
                    break
                elif line.startswith("# ") and "Agent" in line:
                    display_name = line.replace("# ", "").replace(" Agent", "").strip()
            for line in content.splitlines():
                if line.startswith("Answers questions about"):
                    subtitle = clean_subtitle_markdown(line.strip())
                    break
        except Exception:
            pass
            
    if root_agent_path.exists() and display_name == agent_name.replace("_", " ").title():
        try:
            data = yaml.safe_load(root_agent_path.read_text(encoding="utf-8"))
            display_name = data.get("display_name", display_name)
        except Exception:
            pass
            
    return {
        "display_name": display_name,
        "subtitle": subtitle,
    }


def generate_html_showcase(
    agent_name: str,
    domain: str,
    output_dir: Path,
    duration_text: str = "5:45 (Normal Pacing)",
) -> Path:
    """Renders and writes the standalone HTML demo player file for an agent."""
    domain_output_dir = output_dir / domain
    domain_output_dir.mkdir(parents=True, exist_ok=True)
    html_target = domain_output_dir / f"{agent_name}.html"
    
    info = get_agent_info(agent_name, domain)
    display_name = info["display_name"]
    subtitle = info["subtitle"]
    
    domain_badge = DOMAIN_TITLES.get(domain, domain.replace("_", " ").title())
    icon = DOMAIN_ICONS.get(domain, "🤖")
    
    readme_path = REPO_ROOT / "domains" / domain / "agents" / agent_name / "README.md"
    prompts = parse_agent_prompts(readme_path) if readme_path.exists() else []
    
    # Format turns
    turn_1_prompt = prompts[0] if len(prompts) > 0 else "What are the key performance metrics for this category?"
    turn_2_prompt = prompts[1] if len(prompts) > 1 else "What are the latest industry benchmarks and market trends?"
    turn_3_prompt = prompts[2] if len(prompts) > 2 else "Can you render a chart visualizing these metrics?"
    
    agent_clean_title = display_name.split(":")[-1].strip() if ":" in display_name else display_name
    turn_4_prompt = f"Create a 4-slide executive presentation summarizing the {agent_clean_title} analysis and recommendations above."
    
    turn_items = [
        f'        <li><strong>Turn 1 (Data Insights / BigQuery):</strong> <em>"{turn_1_prompt}"</em> — Synthesizes internal BigQuery conversational analytics query and computes KPI summary.</li>',
        f'        <li><strong>Turn 2 (Market Context / Google Search):</strong> <em>"{turn_2_prompt}"</em> — Grounds analysis against external retail benchmarks and industry context.</li>',
        f'        <li><strong>Turn 3 (Visual Artifact / Matplotlib):</strong> <em>"{turn_3_prompt}"</em> — Generates and renders a custom chart visualization artifact inline.</li>',
        f'        <li><strong>Turn 4 (Executive Canvas Presentation):</strong> <em>"{turn_4_prompt}"</em> — Automatically creates a 4-slide deck and showcases each slide via the bottom thumbnail rail.</li>',
    ]
    
    html_content = HTML_TEMPLATE.format(
        page_title=f"{display_name} — Gemini Enterprise Demo Walkthrough",
        domain_badge=domain_badge,
        icon=icon,
        display_name=display_name,
        subtitle=subtitle,
        video_filename=f"{agent_name}.mp4",
        duration_text=duration_text,
        turn_items_html="\n".join(turn_items),
        domain=domain,
        agent_name=agent_name,
    )
    
    html_target.write_text(html_content, encoding="utf-8")
    print(f"✅ Generated HTML demo player: {html_target}", flush=True)
    return html_target


def main():
    parser = argparse.ArgumentParser(description="Generate HTML Demo Video Showcase Player for Gemini Enterprise Agents.")
    parser.add_argument("--name", type=str, help="Target agent directory name (e.g. cart_checkout_analytics)")
    parser.add_argument("--domain", type=str, help="Target retail domain (e.g. e_commerce)")
    parser.add_argument("--all", action="store_true", help="Generate HTML for all recorded videos or all agents in domain")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "demos" / "gemini-enterprise", help="Base output directory for HTML demo players")
    
    args = parser.parse_args()
    
    if not args.name and not args.all:
        parser.error("Must provide either --name <agent_name> or --all")
        
    agents_to_generate = []
    
    if args.name:
        domain = args.domain or resolve_agent_domain(args.name, REPO_ROOT)
        agents_to_generate.append((args.name, domain))
    elif args.all:
        if args.domain:
            agent_dirs = sorted((REPO_ROOT / "domains" / args.domain / "agents").glob("*"))
            for ad in agent_dirs:
                if ad.is_dir() and (ad / "README.md").exists():
                    agents_to_generate.append((ad.name, args.domain))
        else:
            agent_dirs = sorted(REPO_ROOT.glob("domains/*/agents/*"))
            for ad in agent_dirs:
                if ad.is_dir() and (ad / "README.md").exists():
                    domain = ad.parent.parent.name
                    agents_to_generate.append((ad.name, domain))
                    
    print(f"📋 Generating HTML demo players for {len(agents_to_generate)} agent(s)...", flush=True)
    for agent_name, domain in agents_to_generate:
        generate_html_showcase(agent_name, domain, args.output_dir)


if __name__ == "__main__":
    main()
