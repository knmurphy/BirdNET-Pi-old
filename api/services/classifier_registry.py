"""ABC-based classifier plugin system for BirdNET-Pi."""

from abc import ABC, abstractmethod
from typing import Optional


class ClassifierPlugin(ABC):
    """Base class for all classifier plugins.

    Subclasses must implement id, display_name, color, and analyze().
    """

    _enabled: bool = True

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this classifier."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for UI display."""
        ...

    @property
    @abstractmethod
    def color(self) -> str:
        """Hex color for UI badges/overlays."""
        ...

    @abstractmethod
    def analyze(self, audio_path: str) -> list[dict]:
        """Run inference on an audio file.

        Args:
            audio_path: Path to the audio file to analyze.

        Returns:
            List of detection dicts with keys like com_name, sci_name, confidence.
        """
        ...

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def confidence_high(self) -> float:
        return 0.85

    @property
    def confidence_medium(self) -> float:
        return 0.65

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} enabled={self.enabled}>"


class ClassifierRegistry:
    """Registry of available classifier plugins.

    Manages registration, lookup, and filtering of classifiers.
    Duplicate IDs overwrite silently. Unregistering a missing ID is a no-op.
    """

    def __init__(self):
        self._plugins: dict[str, ClassifierPlugin] = {}

    def register(self, plugin: ClassifierPlugin) -> None:
        """Register a classifier plugin. Overwrites if ID already exists."""
        self._plugins[plugin.id] = plugin

    def unregister(self, classifier_id: str) -> None:
        """Remove a classifier by ID. No-op if not found."""
        self._plugins.pop(classifier_id, None)

    def get(self, classifier_id: str) -> Optional[ClassifierPlugin]:
        """Look up a classifier by ID. Returns None if not found."""
        return self._plugins.get(classifier_id)

    def list_all(self) -> list[ClassifierPlugin]:
        """Return all registered classifiers."""
        return list(self._plugins.values())

    def list_enabled(self) -> list[ClassifierPlugin]:
        """Return only enabled classifiers."""
        return [p for p in self._plugins.values() if p.enabled]


class BirdNETClassifier(ClassifierPlugin):
    """Built-in BirdNET classifier.

    Actual inference is handled by external scripts; this is the registry entry.
    """

    @property
    def id(self) -> str:
        return "birdnet"

    @property
    def display_name(self) -> str:
        return "BirdNET"

    @property
    def color(self) -> str:
        return "#22c55e"

    def analyze(self, audio_path: str) -> list[dict]:
        raise NotImplementedError(
            "BirdNET inference is handled by external scripts, not this plugin."
        )


# Global registry instance, pre-loaded with the built-in classifier.
registry = ClassifierRegistry()
registry.register(BirdNETClassifier())
