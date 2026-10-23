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


def test_persona_5state_task_bundle_and_agent_flow_schema(table_registry_data):
    from _shared.scripts.persona_catalog import AGENT_ACTION_TAGS

    all_agents = table_registry_data.get("agents", {})
    assert len(AGENT_ACTION_TAGS) == 100, (
        f"Expected 100 entries in AGENT_ACTION_TAGS, found {len(AGENT_ACTION_TAGS)}"
    )
    for slug in all_agents:
        assert slug in AGENT_ACTION_TAGS, f"Missing action tag for agent {slug}"
        tag = AGENT_ACTION_TAGS[slug]
        assert isinstance(tag, str) and 6 <= len(tag) <= 36, (
            f"Invalid action tag for {slug}: '{tag}'"
        )

    valid_states = {"unchanged", "augmented", "automated", "new", "retired"}

    for arch in PERSONA_ARCHETYPES:
        dist = arch.get("task_distribution", {})
        for k in ("unchanged_pct", "augmented_pct", "automated_pct", "new_ai_pct", "retired_pct"):
            assert k in dist and isinstance(dist[k], int) and dist[k] > 0, (
                f"Invalid {k} in {arch['id']} task_distribution: {dist}"
            )
        assert sum(dist.values()) == 100, (
            f"task_distribution in {arch['id']} must sum to 100, got {sum(dist.values())}"
        )

        for stage_idx, stage in enumerate(arch.get("day_in_the_life", [])):
            bundle = stage.get("task_bundle", [])
            assert isinstance(bundle, list) and len(bundle) == 6, (
                f"Stage {stage_idx} in {arch['id']} must have 6 tasks in task_bundle, found {len(bundle)}"
            )
            states_present = {t.get("state") for t in bundle}
            assert states_present == valid_states, (
                f"Stage {stage_idx} in {arch['id']} task_bundle must include all 5 states {valid_states}, got {states_present}"
            )
            for t in bundle:
                assert isinstance(t.get("label"), str) and 10 <= len(t["label"]) <= 68, (
                    f"Invalid task label in {arch['id']} stage {stage_idx}: {t}"
                )
                assert isinstance(t.get("step_indices"), list), (
                    f"Missing step_indices list in {arch['id']} stage {stage_idx}: {t}"
                )
                if t["state"] in ("automated", "augmented", "new"):
                    assert len(t["step_indices"]) >= 1 and len(t.get("steps_label", "")) > 0, (
                        f"Active AI task {t['label']} must reference at least 1 step index"
                    )
                else:
                    assert t.get("steps_label", "") == "", (
                        f"Unchanged/Retired task {t['label']} should have empty steps_label"
                    )

            flow = stage.get("agent_flow", [])
            featured = stage.get("featured_agents", [])
            assert len(flow) == len(featured), (
                f"Stage {stage_idx} in {arch['id']} agent_flow length {len(flow)} != featured_agents length {len(featured)}"
            )
            for idx, step_obj in enumerate(flow):
                assert step_obj["step"] == idx + 1
                assert step_obj["step_code"] == f"{idx + 1:02d}"
                assert step_obj["slug"] == featured[idx]
                assert step_obj["action_tag"] == AGENT_ACTION_TAGS[featured[idx]]


def test_generated_index_html_5state_task_bundle_and_motion_pipeline():
    index_file = REPO_ROOT / "index.html"
    content = index_file.read_text(encoding="utf-8")

    # 1. Verify 5-state CSS custom properties exist in index.html
    for token in [
        "--task-unchanged-bg",
        "--task-augmented-bg",
        "--task-automated-bg",
        "--task-new-bg",
        "--task-retired-bg",
    ]:
        assert token in content, f"Missing 5-state CSS token {token} in index.html"

    # 2. Verify 5-state legend labels exist and forbidden legend words are absent
    assert "5-State Task Bundle Key:" in content
    assert "1. Tasks Unchanged" in content
    assert "2. Tasks Augmented" in content
    assert "3. Tasks Automated" in content
    assert "4. New Tasks Created by AI" in content
    assert "5. Retired Manual Tasks" in content
    assert "AI Co-Pilot" not in content, "Legend must not contain 'AI Co-Pilot'"
    assert "2. Augmented (AI Co-Pilot)" not in content
    assert "3. Automated (Autonomous)" not in content

    # 3. Verify 2-state toggle and Motion Bento Pipeline classes/functions exist
    assert "setDitlStateMode" in content
    assert "Before Agents (Manual Baseline)" in content
    assert "After Agents (5-State Task Bundle + Agent Flow)" in content
    assert "flow-bento-grid" in content
    assert "flow-step-card" in content
    assert "motion-spotlight" in content
    assert "bindPipelineSpotlightEvents" in content

    # 4. Verify compare narrative DOM classes are not rendered in renderPersonaExperience
    render_fn_match = re.search(
        r"function renderPersonaExperience\(\)\s*\{(.*?)\n    function renderAgents\(\)",
        content,
        re.DOTALL,
    )
    assert render_fn_match is not None
    render_fn_body = render_fn_match.group(1)
    assert "ditl-compare-grid" not in render_fn_body, (
        "Compare narrative grid must be removed from renderPersonaExperience()"
    )


def test_v5_interactive_states_conduit_and_fullscreen_theater():
    index_file = REPO_ROOT / "index.html"
    content = index_file.read_text(encoding="utf-8")

    # 1. Interactive 5-State filter pills & handlers
    assert "ditl-state-filter-pill" in content
    assert "data-filter-state" in content
    assert "toggleTaskStateFilter" in content
    assert "resetTaskStateFilter" in content

    # 2. Prominent Motion spotlighting & dimming
    assert "motion-spotlight" in content
    assert "motion-dimmed" in content
    assert "applyProminentSpotlight" in content

    # 3. Option A — Connected Orchestration Conduit
    assert "flow-conduit-track" in content
    assert "conduit-rail-line" in content
    assert "conduit-rail-fill" in content
    assert "conduit-medallion" in content
    assert "conduit-step-card" in content
    assert "conduit-demo-btn" in content
    assert "flow-step-card" in content
    assert "flow-bento-grid" in content

    # 4. Full-Screen / Maximize Stage Focus Theater
    assert "stage-maximize-btn" in content
    assert "stageTheaterModal" in content
    assert "openStageTheater" in content
    assert "closeStageTheater" in content
    assert "switchTheaterStage" in content


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


