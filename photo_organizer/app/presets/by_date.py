"""
Preset: By Date
Reads EXIF DateTimeOriginal and classifies into YYYY/MM-MonthName.
Falls back to file modification date if EXIF is absent.
"""
import os
from datetime import datetime

import exifread


MONTHS = {
    1: "01-January", 2: "02-February", 3: "03-March",
    4: "04-April",   5: "05-May",      6: "06-June",
    7: "07-July",    8: "08-August",   9: "09-September",
    10: "10-October", 11: "11-November", 12: "12-December",
}


class ByDatePreset:
    id = "by_date"
    name = "By Date"
    icon = "📅"
    description = "Sorts photos into folders by the year and month they were taken."

    def classify(self, filepath: str) -> str:
        """Return a relative subfolder path like '2023/07-July'."""
        dt = self._get_datetime(filepath)
        return f"{dt.year}/{MONTHS[dt.month]}"

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_datetime(self, filepath: str) -> datetime:
        # Try EXIF first
        try:
            with open(filepath, "rb") as fh:
                tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal", details=False)
            raw = str(tags.get("EXIF DateTimeOriginal", ""))
            if raw:
                return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass

        # Fallback: file modification time
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime)
