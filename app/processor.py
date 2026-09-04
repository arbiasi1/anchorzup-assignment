import re
from collections.abc import Iterable
from .models import Rule
from .schemas import MatchInfo, ProcessResponse, TextSegment


def _pattern(rule: Rule) -> re.Pattern[str]:
    keyword = re.escape(rule.keyword)
    if rule.match_type == "exact":
        expression = rf"(?<!\w){keyword}(?!\w)"
    elif rule.match_type == "startsWith":
        expression = rf"(?<!\w){keyword}\w*"
    else:
        expression = keyword
    return re.compile(expression, 0 if rule.case_sensitive else re.IGNORECASE)


def process_text(text: str, rules: Iterable[Rule]) -> ProcessResponse:
    hits: list[tuple[int, int, Rule]] = []
    matched_ids: set[int] = set()
    for rule in rules:
        if not rule.enabled:
            continue
        for match in _pattern(rule).finditer(text):
            hits.append((match.start(), match.end(), rule))
            matched_ids.add(rule.id)

    if not hits:
        return ProcessResponse(segments=[TextSegment(text=text, matches=[])], match_count=0, matched_rule_count=0)

    boundaries = sorted({0, len(text), *(p for start, end, _ in hits for p in (start, end))})
    segments: list[TextSegment] = []
    for start, end in zip(boundaries, boundaries[1:]):
        active = sorted(
            (rule for hit_start, hit_end, rule in hits if hit_start <= start and end <= hit_end),
            key=lambda rule: (-rule.priority, rule.id),
        )
        matches = [
            MatchInfo(
                rule_id=rule.id, keyword=rule.keyword, action_type=rule.action_type,
                color=rule.color, label=rule.label, priority=rule.priority,
            )
            for rule in active
        ]
        piece = TextSegment(text=text[start:end], matches=matches)
        if segments and segments[-1].matches == piece.matches:
            segments[-1].text += piece.text
        else:
            segments.append(piece)

    return ProcessResponse(segments=segments, match_count=len(hits), matched_rule_count=len(matched_ids))

