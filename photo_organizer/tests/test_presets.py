"""
Unit tests for all preset classify() methods.
Run:  python -m pytest tests/  (from photo_organizer/)
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Make sure app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.presets.by_type import ByTypePreset
from app.presets.by_size import BySizePreset, MB


class TestByTypePreset(unittest.TestCase):
    def setUp(self):
        self.preset = ByTypePreset()

    def test_jpeg(self):
        self.assertEqual(self.preset.classify("photo.jpg"), "JPEG")
        self.assertEqual(self.preset.classify("photo.JPEG"), "JPEG")

    def test_png(self):
        self.assertEqual(self.preset.classify("image.png"), "PNG")

    def test_raw(self):
        for ext in (".cr2", ".nef", ".arw", ".dng", ".raw"):
            self.assertEqual(self.preset.classify(f"photo{ext}"), "RAW")

    def test_heic(self):
        self.assertEqual(self.preset.classify("iphone.heic"), "HEIC")

    def test_unknown(self):
        self.assertEqual(self.preset.classify("document.pdf"), "Other")

    def test_video(self):
        self.assertEqual(self.preset.classify("clip.mp4"), "Video")
        self.assertEqual(self.preset.classify("clip.mov"), "Video")


class TestBySizePreset(unittest.TestCase):
    def setUp(self):
        self.preset = BySizePreset()

    def _make_file(self, size_bytes: int) -> str:
        """Create a temp file of a given size and return its path."""
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        f.write(b"\x00" * size_bytes)
        f.close()
        return f.name

    def test_small(self):
        path = self._make_file(512 * 1024)  # 0.5 MB
        try:
            self.assertEqual(self.preset.classify(path), "Small (under 1 MB)")
        finally:
            os.unlink(path)

    def test_medium(self):
        path = self._make_file(int(2.5 * MB))  # 2.5 MB
        try:
            self.assertEqual(self.preset.classify(path), "Medium (1–5 MB)")
        finally:
            os.unlink(path)

    def test_large(self):
        path = self._make_file(int(8 * MB))  # 8 MB
        try:
            self.assertEqual(self.preset.classify(path), "Large (over 5 MB)")
        finally:
            os.unlink(path)


class TestByDatePreset(unittest.TestCase):
    def test_fallback_to_mtime(self):
        """Without EXIF, should fall back to file mtime."""
        from app.presets.by_date import ByDatePreset
        preset = ByDatePreset()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(b"\xff\xd8\xff")  # minimal JPEG header
            path = f.name
        try:
            result = preset.classify(path)
            # Should return something like "2024/01-January"
            year, month_str = result.split("/")
            self.assertTrue(year.isdigit())
            self.assertRegex(month_str, r"^\d{2}-\w+$")
        finally:
            os.unlink(path)


class TestByLocationPreset(unittest.TestCase):
    def test_no_gps_returns_unknown(self):
        from app.presets.by_location import ByLocationPreset
        preset = ByLocationPreset()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(b"\xff\xd8\xff")
            path = f.name
        try:
            result = preset.classify(path)
            self.assertEqual(result, "Unknown Location")
        finally:
            os.unlink(path)


class TestNudityPreset(unittest.TestCase):
    def test_unscanned_error_on_exception(self):
        """If the detector raises an error, result must be 'Unscanned_Error', NOT 'Safe'."""
        from app.presets.nudity import NudityPreset
        preset = NudityPreset()
        preset._classifier = MagicMock()
        preset._classifier.detect.side_effect = RuntimeError("model error")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(b"\xff\xd8\xff")
            path = f.name
        try:
            self.assertEqual(preset.classify(path), "Unscanned_Error")
        finally:
            os.unlink(path)

    def test_flagged_when_explicit_label_detected(self):
        from app.presets.nudity import NudityPreset
        preset = NudityPreset()
        preset._classifier = MagicMock()
        preset._classifier.detect.return_value = [
            {"class": "EXPOSED_BREAST_F", "score": 0.95}
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            path = f.name
        try:
            self.assertEqual(preset.classify(path), "Flagged_Nudity")
        finally:
            os.unlink(path)

    def test_safe_when_score_below_threshold(self):
        from app.presets.nudity import NudityPreset
        preset = NudityPreset()
        preset._classifier = MagicMock()
        preset._classifier.detect.return_value = [
            {"class": "EXPOSED_BREAST_F", "score": 0.3}  # below 0.5 threshold
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            path = f.name
        try:
            self.assertEqual(preset.classify(path), "Safe")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
