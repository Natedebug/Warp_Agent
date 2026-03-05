"""
Preset: Nudity Filter
Uses NudeNet (local, offline model) to classify images.
  • Flagged_Nudity  – image contains nudity
  • Safe            – image is safe
Model weights (~90 MB) are downloaded automatically on first run.
"""

# NudeNet labels that indicate nudity content
NUDITY_LABELS = {
    "EXPOSED_ANUS",
    "EXPOSED_ARMPITS",
    "COVERED_BELLY",
    "EXPOSED_BELLY",
    "COVERED_BUTTOCKS",
    "EXPOSED_BUTTOCKS",
    "FACE_F",
    "FACE_M",
    "COVERED_FEET",
    "EXPOSED_FEET",
    "COVERED_BREAST_F",
    "EXPOSED_BREAST_F",
    "COVERED_GENITALIA_F",
    "EXPOSED_GENITALIA_F",
    "EXPOSED_GENITALIA_M",
    "EXPOSED_BREAST_M",
}

# Only these labels actually indicate explicit/nudity content we care about
EXPLICIT_LABELS = {
    "EXPOSED_ANUS",
    "EXPOSED_BUTTOCKS",
    "EXPOSED_BREAST_F",
    "EXPOSED_GENITALIA_F",
    "EXPOSED_GENITALIA_M",
    "COVERED_GENITALIA_F",
}

CONFIDENCE_THRESHOLD = 0.5


class NudityPreset:
    id = "nudity"
    name = "Nudity Filter"
    icon = "🔞"
    description = (
        "Scans each photo for nudity using an on-device AI model. "
        "Flagged photos go into 'Flagged_Nudity', clean photos into 'Safe'. "
        "No internet required — model runs fully on your computer."
    )

    def __init__(self):
        self._classifier = None

    def _get_classifier(self):
        if self._classifier is None:
            from nudenet import NudeDetector
            self._classifier = NudeDetector()
        return self._classifier

    def classify(self, filepath: str) -> str:
        """Return 'Flagged_Nudity', 'Safe', or 'Unscanned_Error'.

        Errors are surfaced as 'Unscanned_Error' rather than silently
        classified as 'Safe', preventing false-negatives when the model
        fails to load or process a file.
        """
        try:
            detector = self._get_classifier()
            detections = detector.detect(filepath)
            for det in detections:
                label = det.get("class", "")
                score = det.get("score", 0.0)
                if label in EXPLICIT_LABELS and score >= CONFIDENCE_THRESHOLD:
                    return "Flagged_Nudity"
            return "Safe"
        except Exception:
            # Detection failed — do NOT classify as Safe to avoid false-negatives.
            # Files go into a separate folder so the user can review them manually.
            return "Unscanned_Error"
