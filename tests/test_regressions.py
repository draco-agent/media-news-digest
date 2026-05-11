#!/usr/bin/env python3
"""Regression checks for media-news-digest pipeline migration issues."""

import importlib.util
import json
import re
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = REPO / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_run_pipeline_does_not_reference_missing_github_fetcher():
    source = (REPO / "scripts" / "run-pipeline.py").read_text(encoding="utf-8")
    assert "fetch-github.py" not in source
    assert "github trending" not in source.lower()


def test_group_by_topics_uses_media_priority_order():
    merge = load_script("merge-sources.py")
    grouped = merge.group_by_topics([
        {
            "title": "Weekend box office milestone",
            "link": "https://example.com/a",
            "quality_score": 1,
            "topics": ["production", "box-office", "streaming"],
        }
    ])
    assert list(grouped.keys()) == ["box-office"]
    assert grouped["box-office"][0]["primary_topic"] == "box-office"


def test_group_by_topics_reclassifies_broad_source_tags_from_content():
    merge = load_script("merge-sources.py")
    grouped = merge.group_by_topics([
        {
            "title": "China Box Office: Local Comedy Leads Weekend Frame",
            "snippet": "mainland China theatrical market update",
            "link": "https://example.com/china-box-office",
            "quality_score": 1,
            "topics": ["production", "awards", "deals", "box-office", "streaming", "upcoming"],
        }
    ])
    assert list(grouped.keys()) == ["china"]


def test_group_by_topics_filters_obvious_non_media_items_from_broad_tags():
    merge = load_script("merge-sources.py")
    grouped = merge.group_by_topics([
        {
            "title": "Is OpenAI making a ChatGPT phone?",
            "snippet": "AI hardware discussion unrelated to movies or television",
            "link": "https://example.com/openai-phone",
            "quality_score": 1,
            "topics": ["box-office", "reviews", "upcoming"],
        }
    ])
    assert grouped == {}


def test_media_classifier_does_not_match_deal_inside_ideal():
    merge = load_script("merge-sources.py")
    grouped = merge.group_by_topics([
        {
            "title": "Ideal Review: a sharp new studio drama",
            "snippet": "Critics review the theatrical premiere.",
            "link": "https://example.com/ideal-review",
            "quality_score": 1,
            "topics": ["reviews", "deals"],
        }
    ])
    assert list(grouped.keys()) == ["reviews"]


def test_media_classifier_does_not_match_max_inside_title_or_person_name():
    merge = load_script("merge-sources.py")
    grouped = merge.group_by_topics([
        {
            "title": "Maxxxine Review: Ti West closes the trilogy",
            "snippet": "Critics review the theatrical horror release.",
            "link": "https://example.com/maxxxine-review",
            "quality_score": 1,
            "topics": ["reviews", "streaming"],
        },
        {
            "title": "Max Minghella joins new indie film cast",
            "snippet": "The actor boards the production.",
            "link": "https://example.com/max-minghella-cast",
            "quality_score": 1,
            "topics": ["production", "streaming"],
        },
    ])
    assert set(grouped.keys()) == {"production", "reviews"}
    assert "streaming" not in grouped
    assert grouped["production"][0]["primary_topic"] == "production"
    assert grouped["reviews"][0]["primary_topic"] == "reviews"


def test_run_step_counts_merged_output_stats():
    run_pipeline = load_script("run-pipeline.py")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "merged.json"
        helper = Path(tmp) / "write_output.py"
        helper.write_text(
            "import json, sys; json.dump({'output_stats': {'total_articles': 42}}, open(sys.argv[sys.argv.index('--output') + 1], 'w'))",
            encoding="utf-8",
        )
        original_scripts_dir = run_pipeline.SCRIPTS_DIR
        try:
            run_pipeline.SCRIPTS_DIR = Path(tmp)
            result = run_pipeline.run_step("Merge", helper.name, [], out)
        finally:
            run_pipeline.SCRIPTS_DIR = original_scripts_dir
    assert result["status"] == "ok"
    assert result["count"] == 42


def test_public_docs_match_default_config_counts():
    sources = json.loads((REPO / "config/defaults/sources.json").read_text(encoding="utf-8"))["sources"]
    topics = json.loads((REPO / "config/defaults/topics.json").read_text(encoding="utf-8"))["topics"]
    total = len(sources)
    enabled = sum(1 for s in sources if s.get("enabled", True))
    enabled_by_type = {}
    for source in sources:
        if source.get("enabled", True):
            enabled_by_type[source["type"]] = enabled_by_type.get(source["type"], 0) + 1

    expected_fragments = [
        f"{total} total sources",
        f"{enabled} enabled",
        f"RSS {enabled_by_type.get('rss', 0)}",
        f"Twitter/X {enabled_by_type.get('twitter', 0)}",
        f"Reddit {enabled_by_type.get('reddit', 0)}",
        f"{len(topics)} topic sections",
    ]

    docs = "\n".join(
        (REPO / name).read_text(encoding="utf-8")
        for name in ["README.md", "README_CN.md", "SKILL.md"]
    )
    for fragment in expected_fragments:
        assert fragment in docs


def test_requirements_are_not_documented_as_stdlib_only():
    docs = (REPO / "README.md").read_text(encoding="utf-8") + "\n" + (REPO / "SKILL.md").read_text(encoding="utf-8")
    assert "standard library only" not in docs.lower()
    assert re.search(r"pip install -r requirements\.txt", docs)
