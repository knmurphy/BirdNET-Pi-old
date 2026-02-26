"""Tests for the classifier plugin registry."""

import pytest

from api.services.classifier_registry import (
    BirdNETClassifier,
    ClassifierPlugin,
    ClassifierRegistry,
    registry,
)


class StubClassifier(ClassifierPlugin):
    """Minimal concrete classifier for testing."""

    @property
    def id(self) -> str:
        return "stub"

    @property
    def display_name(self) -> str:
        return "Stub"

    @property
    def color(self) -> str:
        return "#ff0000"

    def analyze(self, audio_path: str) -> list[dict]:
        return [{"com_name": "Test Bird", "confidence": 0.99}]


def _fresh_registry() -> ClassifierRegistry:
    """Create an isolated registry for tests that mutate state."""
    reg = ClassifierRegistry()
    reg.register(BirdNETClassifier())
    return reg


# ── Global registry ──────────────────────────────────────────────


def test_registry_has_birdnet():
    """Default global registry contains the built-in BirdNET classifier."""
    plugin = registry.get("birdnet")
    assert plugin is not None
    assert plugin.id == "birdnet"


# ── Registration ─────────────────────────────────────────────────


def test_registry_register_custom():
    """Can register a custom classifier and retrieve it."""
    reg = _fresh_registry()
    stub = StubClassifier()
    reg.register(stub)
    assert reg.get("stub") is stub
    assert stub in reg.list_all()


def test_registry_register_duplicate_overwrites():
    """Registering a duplicate ID silently overwrites the previous entry."""
    reg = ClassifierRegistry()
    first = StubClassifier()
    second = StubClassifier()
    reg.register(first)
    reg.register(second)
    assert reg.get("stub") is second
    assert len([p for p in reg.list_all() if p.id == "stub"]) == 1


# ── Unregistration ───────────────────────────────────────────────


def test_registry_unregister():
    """Can unregister a classifier by ID."""
    reg = _fresh_registry()
    reg.register(StubClassifier())
    reg.unregister("stub")
    assert reg.get("stub") is None


def test_registry_unregister_nonexistent():
    """Unregistering a non-existent ID is a no-op."""
    reg = ClassifierRegistry()
    reg.unregister("does-not-exist")  # must not raise


# ── Lookup ───────────────────────────────────────────────────────


def test_registry_get_not_found():
    """get() returns None for an unknown classifier ID."""
    reg = ClassifierRegistry()
    assert reg.get("nonexistent") is None


# ── Filtering ────────────────────────────────────────────────────


def test_registry_list_enabled():
    """list_enabled() filters out disabled classifiers."""
    reg = _fresh_registry()
    stub = StubClassifier()
    stub.enabled = False
    reg.register(stub)

    enabled = reg.list_enabled()
    enabled_ids = [p.id for p in enabled]
    assert "birdnet" in enabled_ids
    assert "stub" not in enabled_ids


def test_registry_list_enabled_after_toggle():
    """Toggling enabled state is reflected in list_enabled()."""
    reg = _fresh_registry()
    birdnet = reg.get("birdnet")
    assert birdnet is not None

    birdnet.enabled = False
    assert birdnet not in reg.list_enabled()

    birdnet.enabled = True
    assert birdnet in reg.list_enabled()


# ── ABC enforcement ──────────────────────────────────────────────


def test_classifier_abc_enforcement():
    """Cannot instantiate ClassifierPlugin directly — it's abstract."""
    with pytest.raises(TypeError):
        ClassifierPlugin()  # type: ignore[abstract]


def test_classifier_abc_partial_implementation():
    """A subclass missing required methods cannot be instantiated."""

    class Incomplete(ClassifierPlugin):
        @property
        def id(self) -> str:
            return "incomplete"

        # Missing display_name, color, analyze

    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]


# ── BirdNETClassifier defaults ───────────────────────────────────


def test_birdnet_defaults():
    """BirdNETClassifier has the correct default values."""
    b = BirdNETClassifier()
    assert b.id == "birdnet"
    assert b.display_name == "BirdNET"
    assert b.color == "#22c55e"
    assert b.enabled is True
    assert b.confidence_high == 0.85
    assert b.confidence_medium == 0.65


def test_birdnet_analyze_raises():
    """BirdNETClassifier.analyze() raises NotImplementedError."""
    b = BirdNETClassifier()
    with pytest.raises(NotImplementedError):
        b.analyze("/tmp/test.wav")
