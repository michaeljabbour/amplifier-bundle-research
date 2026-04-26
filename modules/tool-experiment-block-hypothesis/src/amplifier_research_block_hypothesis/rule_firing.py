"""
rule_firing.py — Per-rule heuristic firing analysis for reflection blocks.

Analyses which rules in a persistent reflection block appear to influence
critic outputs, using three heuristics:

  1. Token-level overlap of rule text with critic_output content
  2. Substring match of rule keywords in critic_output
  3. Per-rule citation ("rule N" or "[R1]" markers)

NOTE: All heuristics are approximations. Results should be interpreted as
indicative, not ground truth. Document honestly in reports.
"""

from __future__ import annotations

import re

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

# Common English words to exclude from keyword extraction.
_STOPWORDS = frozenset(
    {
        "about",
        "above",
        "after",
        "again",
        "against",
        "before",
        "below",
        "between",
        "check",
        "could",
        "doing",
        "during",
        "every",
        "final",
        "given",
        "going",
        "have",
        "their",
        "there",
        "these",
        "thing",
        "think",
        "those",
        "through",
        "under",
        "which",
        "while",
        "would",
        "first",
        "always",
        "never",
        "often",
        "other",
        "still",
        "them",
        "then",
        "when",
        "where",
        "with",
        "without",
        "make",
        "using",
    }
)

_MIN_KW_LEN = 5  # minimum character length for a keyword


def _extract_keywords(rule: dict) -> list[str]:
    """Extract distinctive keywords (≥5 chars, not in stopwords) from rule fields.

    Draws from trigger, action, token, and mechanism. Returns unique keywords.
    """
    text_parts = [
        rule.get("trigger", ""),
        rule.get("action", ""),
        rule.get("token", "").replace("_", " ").replace("RT ", ""),
        rule.get("mechanism", "").replace("_", " "),
    ]
    combined = " ".join(text_parts)
    words = re.findall(r"[a-zA-Z]+", combined)
    seen: set[str] = set()
    keywords: list[str] = []
    for w in words:
        lw = w.lower()
        if len(lw) >= _MIN_KW_LEN and lw not in _STOPWORDS and lw not in seen:
            seen.add(lw)
            keywords.append(lw)
    return keywords


def _rule_full_text(rule: dict) -> str:
    """Return combined text of all rule fields for token-overlap heuristic."""
    return " ".join(
        [
            rule.get("mechanism", ""),
            rule.get("token", ""),
            rule.get("trigger", ""),
            rule.get("action", ""),
        ]
    )


def _get_critic_output(trace: dict) -> str:
    """Extract critic output text from a stage-trace dict (may be None/absent)."""
    stages = trace.get("stages", {})
    critic = stages.get("critic")
    if isinstance(critic, dict):
        return critic.get("output", "") or ""
    return ""


def _rule_fires(rule: dict, critic_text: str, rule_idx: int) -> bool:
    """Return True if ANY heuristic suggests this rule fired in critic_text.

    Heuristic 1 — token overlap: ≥25 % of rule tokens (≥5 chars) appear in critic.
    Heuristic 2 — keyword substring: ANY distinctive keyword appears in critic.
    Heuristic 3 — citation pattern: "rule N", "[RN]", or token literal present.
    """
    if not critic_text:
        return False

    critic_lower = critic_text.lower()

    # ── Heuristic 3: explicit citation patterns ────────────────────────────
    n = rule_idx + 1  # 1-indexed
    citation_patterns = [
        f"rule {n}",
        f"[r{n}]",
        f"r{n}:",
        f"(r{n})",
    ]
    for pat in citation_patterns:
        if pat in critic_lower:
            return True

    # Direct token literal match (e.g., "RT_CHECK_ARITHMETIC")
    token = rule.get("token", "").lower()
    if token and token in critic_lower:
        return True

    # ── Heuristic 2: keyword substring ────────────────────────────────────
    keywords = _extract_keywords(rule)
    for kw in keywords:
        # Use word-boundary regex to avoid matching sub-words
        if re.search(r"\b" + re.escape(kw) + r"\b", critic_lower):
            return True

    # ── Heuristic 1: token-level overlap ──────────────────────────────────
    rule_tokens = set(
        w.lower() for w in re.findall(r"[a-zA-Z]+", _rule_full_text(rule)) if len(w) >= _MIN_KW_LEN
    )
    critic_tokens = set(w for w in re.findall(r"[a-zA-Z]+", critic_lower) if len(w) >= _MIN_KW_LEN)
    if rule_tokens:
        overlap_ratio = len(rule_tokens & critic_tokens) / len(rule_tokens)
        if overlap_ratio >= 0.25:
            return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def analyze_rule_firing(block: dict, traces: list[dict]) -> dict[str, dict]:
    """Analyze per-rule firing statistics across stage traces.

    For each rule in *block*, counts how often it appears to influence the
    ``critic_output`` using three heuristics:

    1. Token-level overlap of rule text with critic_output
    2. Substring match of rule keywords in critic_output
    3. Citation markers ("Rule 1", "[R1]", etc.)

    Outcome classification when a rule fires:
    - **helped_count**: rule fires and ``final_is_empty`` is False *and* a
      ``revert_decision`` stage is present (critic cycle completed).
    - **hurt_count**: rule fires and ``final_is_empty`` is True.
    - **neutral_count**: rule fires but neither condition above holds.

    NOTE: These are approximations. Document honestly in reports.

    Args:
        block: Block dict with a ``"rules"`` list. Each rule must have at
            least one of: ``token``, ``mechanism``, ``trigger``, ``action``.
        traces: List of stage-trace dicts (e.g., from ``stage_traces.jsonl``).

    Returns:
        ``{rule_id: {fires_count, helped_count, hurt_count, neutral_count}}``
    """
    rules: list[dict] = block.get("rules", [])
    result: dict[str, dict] = {}

    for idx, rule in enumerate(rules):
        # Prefer "token" as the rule identifier; fall back to mechanism or positional.
        rule_id: str = rule.get("token") or rule.get("mechanism") or f"rule_{idx}"
        stats: dict[str, int] = {
            "fires_count": 0,
            "helped_count": 0,
            "hurt_count": 0,
            "neutral_count": 0,
        }

        for trace in traces:
            critic_text = _get_critic_output(trace)
            if not critic_text:
                continue  # no critic output — nothing to match

            if _rule_fires(rule, critic_text, idx):
                stats["fires_count"] += 1

                final_is_empty: bool = bool(trace.get("final_is_empty", False))
                has_revert = trace.get("stages", {}).get("revert_decision") is not None

                if final_is_empty:
                    stats["hurt_count"] += 1
                elif has_revert:
                    stats["helped_count"] += 1
                else:
                    stats["neutral_count"] += 1

        result[rule_id] = stats

    return result


def rule_firing_to_markdown(
    block: dict,
    analysis: dict[str, dict],
    output_path: str | None = None,
) -> str:
    """Render the rule-firing analysis as a Markdown report.

    Args:
        block: The original block dict (for metadata).
        analysis: Output of :func:`analyze_rule_firing`.
        output_path: If given, write the report to this file.

    Returns:
        The Markdown report string.
    """
    lines: list[str] = [
        f"# Rule-Firing Analysis — {block.get('name', 'block')}",
        "",
        "> **Approximation notice:** Rule-firing is detected via heuristics "
        "(keyword overlap, citation patterns). These are NOT ground truth; "
        "treat counts as indicative signals only.",
        "",
        "## Summary Table",
        "",
        "| Rule ID | Fires | Helped | Hurt | Neutral | Fire Rate |",
        "| ------- | -----:| ------:| ----:| -------:| --------: |",
    ]

    for rule_id, stats in analysis.items():
        fires = stats["fires_count"]
        helped = stats["helped_count"]
        hurt = stats["hurt_count"]
        neutral = stats["neutral_count"]
        fire_rate = "—"  # we don't have total here; shown per-rule in detail
        lines.append(f"| `{rule_id}` | {fires} | {helped} | {hurt} | {neutral} | {fire_rate} |")

    lines += [
        "",
        "## Per-Rule Detail",
        "",
    ]

    rules_by_id = {
        (r.get("token") or r.get("mechanism") or f"rule_{i}"): r
        for i, r in enumerate(block.get("rules", []))
    }

    for rule_id, stats in analysis.items():
        rule = rules_by_id.get(rule_id, {})
        lines += [
            f"### `{rule_id}`",
            "",
            f"**Mechanism:** {rule.get('mechanism', 'N/A')}",
            "",
            f"**Trigger:** {rule.get('trigger', 'N/A')}",
            "",
            f"**Action:** {rule.get('action', 'N/A')}",
            "",
            f"- Fires: **{stats['fires_count']}**",
            f"- Helped (fired, non-empty, revert_decision present): {stats['helped_count']}",
            f"- Hurt (fired, final response was empty): {stats['hurt_count']}",
            f"- Neutral (fired, outcome unclear): {stats['neutral_count']}",
            "",
        ]

    report = "\n".join(lines)

    if output_path:
        from pathlib import Path

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")

    return report
