"""Template persistence for appointment and invoice defaults."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Template:
    name: str
    payload: Dict


class TemplateStore:
    """JSON-backed template storage."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save([])

    def load(self) -> List[Template]:
        with self.path.open() as fp:
            data = json.load(fp)
        return [Template(**item) for item in data]

    def save(self, templates: Iterable[Template]) -> None:
        serializable = [template.__dict__ for template in templates]
        with self.path.open("w") as fp:
            json.dump(serializable, fp, indent=2)

    def list(self) -> List[Template]:
        return self.load()

    def add(self, template: Template) -> None:
        templates = self.load()
        if any(t.name == template.name for t in templates):
            raise ValueError(f"Template '{template.name}' already exists")
        templates.append(template)
        self.save(templates)

    def remove(self, name: str) -> None:
        templates = [t for t in self.load() if t.name != name]
        self.save(templates)

    def get(self, name: str) -> Optional[Template]:
        for template in self.load():
            if template.name == name:
                return template
        return None
