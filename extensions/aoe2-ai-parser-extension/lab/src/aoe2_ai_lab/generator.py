from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GeneratedBlock:
    block_id: str
    body: str

    def with_markers(self) -> str:
        return "\n".join(
            [
                f"; <aoe2-ai-lab:block {self.block_id}>",
                self.body.rstrip(),
                f"; </aoe2-ai-lab:block {self.block_id}>",
            ]
        )


DEFAULT_SN_SETTINGS: tuple[tuple[str, str], ...] = (
    ("sn-cap-civilian-builders", "200"),
    ("sn-consecutive-idle-unit-limit", "1"),
    ("sn-do-not-scale-for-difficulty-level", "1"),
    ("sn-enable-boar-hunting", "1"),
    ("sn-enable-offensive-priority", "1"),
    ("sn-enable-patrol-attack", "1"),
    ("sn-initial-exploration-required", "0"),
    ("sn-maximum-fish-boat-drop-distance", "30"),
    ("sn-maximum-food-drop-distance", "20"),
    ("sn-maximum-gold-drop-distance", "20"),
    ("sn-maximum-hunt-drop-distance", "30"),
    ("sn-maximum-stone-drop-distance", "20"),
    ("sn-scale-minimum-attack-group-size", "0"),
    ("sn-task-ungrouped-soldiers", "0"),
    ("sn-zero-priority-distance", "255"),
    ("sn-dropsite-separation-distance", "3"),
)


def parse_assignment(value: str) -> tuple[str, str]:
    left, sep, right = value.partition("=")
    if not sep or not left.strip() or not right.strip():
        raise ValueError(f"expected NAME=VALUE assignment, got {value!r}")
    return left.strip(), right.strip()


def render_rule(
    facts: list[str],
    actions: list[str],
    *,
    disable_self: bool = False,
) -> str:
    lines = ["(defrule"]
    lines.extend(f"    {fact}" for fact in facts)
    lines.append("=>")
    lines.extend(f"    {action}" for action in actions)
    if disable_self:
        lines.append("    (disable-self)")
    lines.append(")")
    return "\n".join(lines)


def generate_sn_defaults(block_id: str = "init.sn-defaults") -> GeneratedBlock:
    actions = [f"(set-strategic-number {name} {value})" for name, value in DEFAULT_SN_SETTINGS]
    body = render_rule(["(true)"], actions, disable_self=True)
    return GeneratedBlock(block_id, body)


def generate_goal_batch(
    block_id: str,
    facts: list[str],
    assignments: list[tuple[str, str]],
    *,
    disable_self: bool = True,
) -> GeneratedBlock:
    actions = [f"(set-goal {goal} {value})" for goal, value in assignments]
    body = render_rule(facts or ["(true)"], actions, disable_self=disable_self)
    return GeneratedBlock(block_id, body)


def generate_state_transition(
    block_id: str,
    goal: str,
    from_value: str,
    to_value: str,
    facts: list[str],
    *,
    disable_self: bool = True,
) -> GeneratedBlock:
    all_facts = [*facts, f"(goal {goal} {from_value})"]
    actions = [f"(set-goal {goal} {to_value})"]
    body = render_rule(all_facts, actions, disable_self=disable_self)
    return GeneratedBlock(block_id, body)


def section_start(section: str) -> str:
    return f"; <aoe2-ai-lab:section {section}>"


def section_end(section: str) -> str:
    return f"; </aoe2-ai-lab:section {section}>"


def block_start(block_id: str) -> str:
    return f"; <aoe2-ai-lab:block {block_id}>"


def block_end(block_id: str) -> str:
    return f"; </aoe2-ai-lab:block {block_id}>"


def insert_block(source: str, section: str, block: GeneratedBlock) -> str:
    rendered = block.with_markers()
    start = block_start(block.block_id)
    end = block_end(block.block_id)

    block_start_index = source.find(start)
    if block_start_index >= 0:
        block_end_index = source.find(end, block_start_index)
        if block_end_index < 0:
            raise ValueError(f"found start marker for {block.block_id!r} without end marker")
        replace_end = block_end_index + len(end)
        return f"{source[:block_start_index]}{rendered}{source[replace_end:]}"

    start_marker = section_start(section)
    end_marker = section_end(section)
    section_start_index = source.find(start_marker)
    section_end_index = source.find(end_marker)

    if section_start_index < 0 and section_end_index < 0:
        suffix = "" if source.endswith("\n") else "\n"
        return (
            f"{source}{suffix}\n"
            f"{start_marker}\n"
            f"{rendered}\n"
            f"{end_marker}\n"
        )

    if section_start_index < 0 or section_end_index < 0 or section_end_index < section_start_index:
        raise ValueError(f"section {section!r} markers are incomplete or out of order")

    prefix = source[:section_end_index].rstrip()
    suffix = source[section_end_index:]
    return f"{prefix}\n\n{rendered}\n{suffix}"


def insert_block_into_file(path: str | Path, section: str, block: GeneratedBlock) -> None:
    file_path = Path(path)
    source = file_path.read_text(encoding="utf-8")
    file_path.write_text(insert_block(source, section, block), encoding="utf-8")

