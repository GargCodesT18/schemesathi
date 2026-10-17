"""Scheme Repository for loading and filtering curated government schemes"""
import json
from pathlib import Path
from typing import List, Optional
from app.config import SCHEMES_FILE
from app.models.scheme import Scheme


class SchemeRepository:
    """Manages curated government schemes from verified JSON storage."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or SCHEMES_FILE
        self._schemes: List[Scheme] = []
        self._load()

    def _load(self) -> None:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Scheme database not found at {self.data_path}")
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            self._schemes = [Scheme(**item) for item in raw_data]

    def get_all(self) -> List[Scheme]:
        """Returns all registered schemes."""
        return list(self._schemes)

    def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        """Lookup scheme by unique ID."""
        for s in self._schemes:
            if s.id.lower() == scheme_id.lower():
                return s
        return None

    def get_by_category(self, category: str) -> List[Scheme]:
        """Filter schemes by sector category."""
        return [s for s in self._schemes if s.category.lower() == category.lower()]

    def get_all_categories(self) -> List[str]:
        """Returns sorted unique category names."""
        categories = sorted(list({s.category for s in self._schemes}))
        return categories

    def count(self) -> int:
        return len(self._schemes)

