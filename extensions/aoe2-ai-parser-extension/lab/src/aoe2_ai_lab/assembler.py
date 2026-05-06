from __future__ import annotations

from pathlib import Path
import re


LOAD_RE = re.compile(r'^\s*#load\s+"([^"]+)"\s*(?:;.*)?$')


def resolve_load_path(base_dir: Path, include_name: str) -> Path:
    include = include_name.replace("/", "\\")
    path = base_dir / include
    if path.suffix.lower() != ".per":
        path = path.with_suffix(".per")
    return path


def assemble_per(path: str | Path, seen: set[Path] | None = None) -> str:
    source_path = Path(path).resolve()
    active = seen or set()
    if source_path in active:
        raise ValueError(f"recursive #load detected for {source_path}")

    active.add(source_path)
    output: list[str] = []
    for raw_line in source_path.read_text(encoding="utf-8").splitlines():
        match = LOAD_RE.match(raw_line)
        if not match:
            output.append(raw_line)
            continue

        include_path = resolve_load_path(source_path.parent, match.group(1)).resolve()
        if not include_path.exists():
            raise FileNotFoundError(f"#load target not found: {include_path}")
        output.append(f"; <assembled {match.group(1)}>")
        output.append(assemble_per(include_path, active))
        output.append(f"; </assembled {match.group(1)}>")

    active.remove(source_path)
    return "\n".join(output).rstrip() + "\n"
