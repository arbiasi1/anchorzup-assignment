from datetime import UTC, datetime
from app.models import Rule
from app.processor import process_text


def rule(rule_id: int, keyword: str, match_type="contains", action_type="highlight", **kwargs):
    defaults = dict(color="#ff0000" if action_type == "highlight" else None,
                    label="IMPORTANT" if action_type == "tooltip" else None,
                    priority=0, enabled=True, case_sensitive=False)
    defaults.update(kwargs)
    return Rule(id=rule_id, keyword=keyword, match_type=match_type,
                action_type=action_type, created_at=datetime.now(UTC), **defaults)


def matched_text(result):
    return "".join(segment.text for segment in result.segments if segment.matches)


def test_contains_finds_every_case_insensitive_occurrence():
    result = process_text("Urgent and urgent", [rule(1, "urgent")])
    assert result.match_count == 2
    assert result.matched_rule_count == 1
    assert matched_text(result) == "Urgenturgent"


def test_exact_does_not_match_inside_another_word():
    result = process_text("cat concatenate cat", [rule(1, "cat", match_type="exact")])
    assert result.match_count == 2
    assert matched_text(result) == "catcat"


def test_starts_with_matches_the_complete_word():
    result = process_text("deadlines dead deadline", [rule(1, "dead", match_type="startsWith")])
    assert result.match_count == 3
    assert matched_text(result) == "deadlinesdeaddeadline"


def test_disabled_rules_are_ignored():
    result = process_text("urgent", [rule(1, "urgent", enabled=False)])
    assert result.match_count == 0
    assert result.segments[0].matches == []


def test_case_sensitive_rule():
    result = process_text("Alert alert", [rule(1, "Alert", case_sensitive=True)])
    assert result.match_count == 1
    assert matched_text(result) == "Alert"


def test_overlapping_rules_share_segments_in_priority_order():
    rules = [rule(1, "deadline", priority=2), rule(2, "line", action_type="tooltip", priority=9)]
    result = process_text("deadline", rules)
    overlapping = next(segment for segment in result.segments if segment.text == "line")
    assert [match.rule_id for match in overlapping.matches] == [2, 1]
    assert result.match_count == 2


def test_no_match_preserves_original_text():
    text = "Nothing to see\nwith formatting intact."
    result = process_text(text, [rule(1, "urgent")])
    assert len(result.segments) == 1
    assert result.segments[0].text == text

