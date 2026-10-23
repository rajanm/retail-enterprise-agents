"""Unit tests for the Retail Enterprise Agents Portal Site Generator."""

import json
from pathlib import Path
import re
import subprocess
import sys
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from _shared.scripts.generate_portal_site import (
    DOMAIN_ORDER,
    DOMAIN_DISPLAY_NAMES,
    DOMAIN_ICONS,
    PERSONA_ARCHETYPES,
    PERSONA_ORDER,
    classify_persona_archetype,
    build_portal_html,
    extract_agent_metadata,
)


@pytest.fixture
def table_registry_data():
    registry_file = REPO_ROOT / "_shared" / "table_registry.yaml"
    assert registry_file.exists(), f"Registry file not found at {registry_file}"
    return yaml.safe_load(registry_file.read_text(encoding="utf-8"))


def test_table_registry_contains_100_agents(table_registry_data):
    agents = table_registry_data.get("agents", {})
    assert len(agents) == 100, f"Expected 100 agents in table_registry.yaml, found {len(agents)}"


def test_extract_agent_metadata_for_sample_agents(table_registry_data):
    agents = table_registry_data.get("agents", {})
    
    # Test merchandising agent
    aspl = agents.get("assortment_planning")
    assert aspl is not None
    meta = extract_agent_metadata("assortment_planning", "merchandising", aspl, REPO_ROOT)
    assert meta["name"] == "assortment_planning"
    assert meta["domain"] == "merchandising"
    assert meta["location"] == "us-central1"
    assert len(meta["prompts"]) >= 3
    assert meta["demo_html"] == "demos/gemini-enterprise/merchandising/assortment_planning.html"
    assert meta["demo_mp4"] == "demos/gemini-enterprise/merchandising/assortment_planning.mp4"
    assert (REPO_ROOT / meta["demo_html"]).exists()
    assert (REPO_ROOT / meta["demo_mp4"]).exists()

    # Test HR agent in us-east4
    wmp = agents.get("workplace_safety_workers_comp")
    assert wmp is not None
    meta_hr = extract_agent_metadata("workplace_safety_workers_comp", "human_resources", wmp, REPO_ROOT)
    assert meta_hr["name"] == "workplace_safety_workers_comp"
    assert meta_hr["domain"] == "human_resources"
    assert meta_hr["location"] == "us-east4"
    assert len(meta_hr["prompts"]) >= 3


def test_generated_index_html_file_exists_and_is_valid():
    index_file = REPO_ROOT / "index.html"
    assert index_file.exists(), "index.html does not exist at repo root"
    
    content = index_file.read_text(encoding="utf-8")
    assert len(content) > 50_000, f"index.html is unexpectedly small ({len(content)} bytes)"
    
    # Verify core HTML structure
    assert "<!DOCTYPE html>" in content
    assert '<html lang="en" data-theme="dark">' in content
    assert "Gemini Enterprise Agents for Retail" in content
    assert "100 Enterprise Agents Fully Deployed (9 Retail Domains)" in content
    assert "Gemini Enterprise Agents" in content
    assert "Agents Demos Ready" in content
    
    # Verify dual-theme CSS variables
    assert '[data-theme="dark"]' in content
    assert '[data-theme="light"]' in content
    assert "retail_agents_theme" in content
    
    # Verify search and modal components
    assert 'id="searchInput"' in content
    assert 'id="domainPills"' in content
    assert 'id="videoModal"' in content
    assert 'id="archModal"' in content
    assert "Gemini Enterprise Agent Platform" in content
    assert "Gemini Enterprise" in content
    assert "Google ADK & Gemini Enterprise Multi-Agent Swarm" in content
    assert "https://github.com/rajanm/retail-enterprise-agents/blob/master/README.md" in content
    assert "https://github.com/rajanm/retail-enterprise-agents/blob/master/ARCHITECTURE.md" in content


def test_all_100_agents_present_in_embedded_json():
    index_file = REPO_ROOT / "index.html"
    content = index_file.read_text(encoding="utf-8")
    
    match = re.search(r"const AGENTS_DATA = (\[.*?\]);\s*\n\s*let activeDomain", content, re.DOTALL)
    assert match is not None, "Could not extract AGENTS_DATA JSON from index.html"
    
    agents = json.loads(match.group(1))
    assert len(agents) == 100, f"Expected 100 agents in AGENTS_DATA, found {len(agents)}"
    
    agent_names = {a["name"] for a in agents}
    assert len(agent_names) == 100, "Duplicate agent names found in AGENTS_DATA"
    
    # Check domain distribution
    domains = {a["domain"] for a in agents}
    assert len(domains) == 9
    assert set(DOMAIN_ORDER) == domains


def test_all_demo_mp4_and_html_files_exist_on_disk():
    index_file = REPO_ROOT / "index.html"
    content = index_file.read_text(encoding="utf-8")
    
    match = re.search(r"const AGENTS_DATA = (\[.*?\]);\s*\n\s*let activeDomain", content, re.DOTALL)
    agents = json.loads(match.group(1))
    
    missing_html = []
    missing_mp4 = []
    
    for agent in agents:
        html_path = REPO_ROOT / agent["demo_html"]
        mp4_path = REPO_ROOT / agent["demo_mp4"]
        readme_path = REPO_ROOT / agent["readme"]
        
        if not html_path.exists():
            missing_html.append(str(html_path))
        if not mp4_path.exists():
            missing_mp4.append(str(mp4_path))
        assert readme_path.exists(), f"README missing: {readme_path}"
        
    assert not missing_html, f"Missing HTML demo files: {missing_html[:5]}"
    assert not missing_mp4, f"Missing MP4 demo files: {missing_mp4[:5]}"


def test_all_100_agent_descriptions_are_clean_and_complete():
    index_file = REPO_ROOT / "index.html"
    content = index_file.read_text(encoding="utf-8")
    
    match = re.search(r"const AGENTS_DATA = (\[.*?\]);\s*\n\s*let activeDomain", content, re.DOTALL)
    agents = json.loads(match.group(1))
    
    bad_descriptions = []
    for a in agents:
        desc = a.get("description", "").strip()
        if desc.startswith("#") or "###" in desc or desc == "### Business Problem" or len(desc) < 40:
            bad_descriptions.append((a["name"], a["domain"], desc))
            
    assert not bad_descriptions, f"Found truncated or markdown-polluted agent descriptions: {bad_descriptions}"


def test_persona_archetypes_and_day_in_the_life_schema(table_registry_data):
    all_agents = table_registry_data.get("agents", {})
    assert len(PERSONA_ORDER) == 10, f"Expected 10 persona IDs in PERSONA_ORDER, got {len(PERSONA_ORDER)}"
    assert len(PERSONA_ARCHETYPES) == 10, f"Expected 10 persona archetypes, got {len(PERSONA_ARCHETYPES)}"

    expected_times = ["Stage 1", "Stage 2", "Stage 3", "Stage 4"]

    all_featured_agents = set()
    for i, arch in enumerate(PERSONA_ARCHETYPES):
        assert arch["id"] == PERSONA_ORDER[i], (
            f"Archetype {i} id {arch.get('id')} does not match PERSONA_ORDER {PERSONA_ORDER[i]}"
        )
        for key in ["id", "icon", "title", "subtitle", "roles_summary", "hours_saved", "decision_speed", "automated_label", "augmented_label"]:
            assert key in arch and isinstance(arch[key], str) and len(arch[key]) > 0, (
                f"Missing or empty {key} in archetype {arch.get('id')}"
            )

        # Assert qualitative labels do not contain specific % numbers
        assert "%" not in arch["automated_label"], f"automated_label should not contain '%': {arch['automated_label']}"
        assert "%" not in arch["augmented_label"], f"augmented_label should not contain '%': {arch['augmented_label']}"

        # Assert hours_saved and decision_speed do not contain specific numeric values
        assert not any(c.isdigit() for c in arch["hours_saved"]), (
            f"hours_saved should use high-level horizon strings without digits: {arch['hours_saved']}"
        )
        assert not any(c.isdigit() for c in arch["decision_speed"]), (
            f"decision_speed should use high-level horizon strings without digits: {arch['decision_speed']}"
        )

        assert "automated_pct" in arch and isinstance(arch["automated_pct"], int)
        assert "augmented_pct" in arch and isinstance(arch["augmented_pct"], int)
        assert arch["automated_pct"] + arch["augmented_pct"] == 100, (
            f"Archetype {arch['id']} split percentages must sum to 100, got {arch['automated_pct']} + {arch['augmented_pct']}"
        )

        stages = arch.get("day_in_the_life", [])
        assert len(stages) == 4, f"Archetype {arch['id']} must have exactly 4 day_in_the_life stages, found {len(stages)}"

        for stage_idx, stage in enumerate(stages):
            assert stage.get("time") == expected_times[stage_idx], (
                f"Stage {stage_idx} in {arch['id']} expected time {expected_times[stage_idx]}, got {stage.get('time')}"
            )
            assert stage.get("mode") in ("Automated", "Augmented"), (
                f"Stage mode in {arch['id']} must be 'Automated' or 'Augmented', got {stage.get('mode')}"
            )
            for str_key in ["stage", "time_before", "time_after"]:
                assert str_key in stage and isinstance(stage[str_key], str) and len(stage[str_key]) > 0

            # Assert time_before and time_after are high-level horizon units
            assert stage["time_before"] in ("Weeks", "Days", "Hours"), (
                f"Stage {stage_idx} in {arch['id']} time_before must be in ('Weeks', 'Days', 'Hours'), got {stage['time_before']}"
            )
            assert stage["time_after"] in ("Hours", "Minutes"), (
                f"Stage {stage_idx} in {arch['id']} time_after must be in ('Hours', 'Minutes'), got {stage['time_after']}"
            )

            assert len(stage.get("without_agents", "")) >= 30, (
                f"Stage {stage_idx} in {arch['id']} 'without_agents' must be >= 30 chars: {stage.get('without_agents')}"
            )
            assert len(stage.get("with_agents", "")) >= 30, (
                f"Stage {stage_idx} in {arch['id']} 'with_agents' must be >= 30 chars: {stage.get('with_agents')}"
            )
            assert len(stage.get("automated_what", "")) >= 20, (
                f"Stage {stage_idx} in {arch['id']} 'automated_what' must be >= 20 chars: {stage.get('automated_what')}"
            )
            assert len(stage.get("augmented_what", "")) >= 20, (
                f"Stage {stage_idx} in {arch['id']} 'augmented_what' must be >= 20 chars: {stage.get('augmented_what')}"
            )

            featured = stage.get("featured_agents", [])
            assert isinstance(featured, list) and len(featured) >= 3, (
                f"Stage {stage_idx} in {arch['id']} must have featured_agents list with at least 3 agents"
            )
            for fa in featured:
                assert fa in all_agents, f"Featured agent '{fa}' in {arch['id']} not found in table_registry.yaml"
                all_featured_agents.add(fa)

    assert len(all_featured_agents) == len(all_agents) == 100, (
        f"Expected all 100 registry agents covered across persona stages, got {len(all_featured_agents)}"
    )


def test_all_100_agents_extract_personas_and_transformations(table_registry_data):
    agents = table_registry_data.get("agents", {})
    assert len(agents) == 100

    archetype_agent_counts = {arch_id: 0 for arch_id in PERSONA_ORDER}

    for agent_name, agent_info in agents.items():
        domain = agent_info["domain"]
        meta = extract_agent_metadata(agent_name, domain, agent_info, REPO_ROOT)

        # Verify personas list
        personas = meta.get("personas", [])
        assert isinstance(personas, list) and len(personas) >= 3, (
            f"Agent {agent_name} has {len(personas)} personas, expected >= 3"
        )
        for p in personas:
            assert "title" in p and isinstance(p["title"], str) and len(p["title"]) > 0
            assert "description" in p and isinstance(p["description"], str) and len(p["description"]) > 0
            assert "archetype" in p and p["archetype"] in PERSONA_ORDER, (
                f"Agent {agent_name} persona '{p.get('title')}' has invalid archetype: {p.get('archetype')}"
            )

        # Verify persona_archetypes list
        archetypes = meta.get("persona_archetypes", [])
        assert isinstance(archetypes, list) and len(archetypes) >= 1, (
            f"Agent {agent_name} missing persona_archetypes"
        )
        for arch in archetypes:
            assert arch in PERSONA_ORDER, f"Agent {agent_name} has unknown archetype: {arch}"
            archetype_agent_counts[arch] += 1

        # Verify transformation dict
        transform = meta.get("transformation", {})
        assert isinstance(transform, dict), f"Agent {agent_name} transformation must be a dict"
        for field in ("without_agent", "with_agent", "automated", "augmented"):
            assert field in transform and isinstance(transform[field], str) and len(transform[field].strip()) > 0, (
                f"Agent {agent_name} transformation missing or empty field: {field}"
            )

    # Verify each of the 10 archetypes maps to >= 5 agents across the 100 agents
    for arch_id, count in archetype_agent_counts.items():
        assert count >= 5, f"Archetype {arch_id} maps to only {count} agents, expected >= 5"


def test_generated_index_html_contains_persona_view_and_dual_theme_tokens():
    index_file = REPO_ROOT / "index.html"
    assert index_file.exists(), "index.html does not exist at repo root"
    content = index_file.read_text(encoding="utf-8")

    # Dual-theme semantic CSS custom properties
    theme_tokens = [
        "--without-bg",
        "--without-border",
        "--without-text",
        "--with-bg",
        "--with-border",
        "--with-text",
        "--aug-bg",
        "--aug-border",
        "--aug-text",
        "--persona-pill-bg",
        "--persona-pill-border",
        "--persona-pill-text",
    ]
    for token in theme_tokens:
        assert token in content, f"Missing dual-theme token {token} in index.html"

    # View mode switcher toolbar
    assert 'data-view="domain"' in content
    assert 'data-view="persona"' in content

    # Persona pills filter
    assert 'id="personaPills"' in content
    assert 'data-persona="all"' in content
    for arch_id in PERSONA_ORDER:
        assert f'data-persona="{arch_id}"' in content

    # Persona experience container
    assert 'id="personaExperienceContainer"' in content

    # Embedded script ordering: AGENTS_DATA immediately followed by activeDomain = 'all', then PERSONA_ARCHETYPES
    match = re.search(r"const AGENTS_DATA = (\[.*?\]);\s*\n\s*let activeDomain = 'all';", content, re.DOTALL)
    assert match is not None, "const AGENTS_DATA must be immediately followed by let activeDomain = 'all';"

    assert "const PERSONA_ARCHETYPES =" in content, "const PERSONA_ARCHETYPES missing in index.html"

    # Motion animation library integration
    assert "motion" in content.lower()


def test_zero_modifications_to_scaffold_agents_and_demos():
    res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    allowed_files = {
        "_shared/scripts/persona_catalog.py",
        "_shared/scripts/generate_portal_site.py",
        "index.html",
        "tests/tooling/test_generate_portal_site.py",
    }
    unexpected_changes = []
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        file_path = line[3:].strip().strip('"')
        if " -> " in file_path:
            file_path = file_path.split(" -> ")[1].strip().strip('"')
        if file_path not in allowed_files:
            unexpected_changes.append((line[:2], file_path))

    assert not unexpected_changes, (
        f"Unexpected changes detected in git status outside allowed files: {unexpected_changes}"
    )


