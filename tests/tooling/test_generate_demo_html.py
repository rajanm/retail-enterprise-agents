"""Unit tests for _shared/scripts/generate_demo_html.py."""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from _shared.scripts.generate_demo_html import (
    generate_html_showcase,
    get_agent_info,
    DOMAIN_ICONS,
    DOMAIN_TITLES,
)


def test_domain_constants():
    assert "merchandising" in DOMAIN_ICONS
    assert "e_commerce" in DOMAIN_ICONS
    assert DOMAIN_ICONS["merchandising"] == "🛍️"
    assert "Merchandising" in DOMAIN_TITLES["merchandising"]


def test_get_agent_info_existing_agent():
    info = get_agent_info("cart_checkout_analytics", "e_commerce")
    assert "Cart & Checkout Analytics" in info["display_name"]
    assert len(info["subtitle"]) > 10


def test_get_agent_info_strips_markdown_syntax():
    info = get_agent_info("assortment_planning", "merchandising")
    assert "**" not in info["subtitle"]
    assert "`" not in info["subtitle"]


def test_generate_html_showcase_output(tmp_path):
    output_dir = tmp_path / "demos"
    html_file = generate_html_showcase(
        agent_name="cart_checkout_analytics",
        domain="e_commerce",
        output_dir=output_dir,
        duration_text="5:11 (Normal Pacing)",
    )
    
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Cart & Checkout Analytics" in content
    assert "cart_checkout_analytics.mp4" in content
    assert "1080p Full HD" in content
    assert 'id="demoVideo"' in content
    assert "cart_checkout_analytics.mp4#t=10" in content
    assert "timeupdate" in content
    assert 'target="_blank"' not in content

