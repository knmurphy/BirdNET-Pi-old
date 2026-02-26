"""Classifier management API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.models.classifier import ClassifierConfig, ClassifierToggleResponse
from api.config import settings

router = APIRouter()

# In-memory classifier state (will move to config file later)
# For now, just BirdNET as the default classifier
CLASSIFIERS = {
    "birdnet": ClassifierConfig(
        id="birdnet",
        name="BirdNET",
        enabled=True,
        model_path=str(settings.config_ini_path.parent / "model" / "BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite"),
        labels_path=str(settings.config_ini_path.parent / "model" / "labels.txt"),
        confidence_threshold=0.8,
        overlap=0.0,
        sensitivity=1.0,
    )
}


@router.get("/classifiers", response_model=list[ClassifierConfig])
async def get_classifiers():
    """Get list of configured classifiers."""
    return list(CLASSIFIERS.values())


@router.post("/classifiers/{classifier_id}/toggle", response_model=ClassifierToggleResponse)
async def toggle_classifier(classifier_id: str):
    """Enable or disable a classifier.

    Toggles the enabled state of the specified classifier.
    """
    if classifier_id not in CLASSIFIERS:
        raise HTTPException(status_code=404, detail=f"Classifier '{classifier_id}' not found")
    
    classifier = CLASSIFIERS[classifier_id]
    classifier.enabled = not classifier.enabled
    
    # TODO: Persist to config file
    
    status = "enabled" if classifier.enabled else "disabled"
    
    return ClassifierToggleResponse(
        id=classifier_id,
        enabled=classifier.enabled,
        message=f"Classifier '{classifier.name}' {status}",
    )
