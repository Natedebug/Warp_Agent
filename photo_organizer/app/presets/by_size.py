"""
Preset: By Size
Classifies photos into Small (<1 MB), Medium (1–5 MB), or Large (>5 MB).
"""
import os


MB = 1024 * 1024


class BySizePreset:
    id = "by_size"
    name = "By File Size"
    icon = "📏"
    description = "Splits photos into Small (<1 MB), Medium (1–5 MB), and Large (>5 MB) folders."

    def classify(self, filepath: str) -> str:
        size = os.path.getsize(filepath)
        if size < 1 * MB:
            return "Small (under 1 MB)"
        elif size < 5 * MB:
            return "Medium (1–5 MB)"
        else:
            return "Large (over 5 MB)"
