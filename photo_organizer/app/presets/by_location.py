"""
Preset: By Location
Reads GPS coordinates from EXIF and reverse-geocodes to a country/city string.
Falls back to 'Unknown Location' when GPS data is absent or offline.
"""
import exifread

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderUnavailable
    _GEOPY_AVAILABLE = True
except ImportError:
    _GEOPY_AVAILABLE = False


_geocoder = None


def _get_geocoder():
    global _geocoder
    if _geocoder is None and _GEOPY_AVAILABLE:
        _geocoder = Nominatim(user_agent="photo_organizer_app", timeout=5)
    return _geocoder


def _dms_to_decimal(dms_tag, ref_tag) -> float | None:
    """Convert degrees/minutes/seconds EXIF tag to decimal degrees."""
    try:
        dms = dms_tag.values
        ref = str(ref_tag.values)
        d = float(dms[0].num) / float(dms[0].den)
        m = float(dms[1].num) / float(dms[1].den)
        s = float(dms[2].num) / float(dms[2].den)
        decimal = d + m / 60 + s / 3600
        if ref in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return None


class ByLocationPreset:
    id = "by_location"
    name = "By Location"
    icon = "🌍"
    description = "Groups photos by where they were taken using GPS data embedded in the photo."

    def classify(self, filepath: str) -> str:
        lat, lon = self._get_gps(filepath)
        if lat is None or lon is None:
            return "Unknown Location"

        gc = _get_geocoder()
        if gc is None:
            return "Unknown Location"

        try:
            location = gc.reverse((lat, lon), language="en", zoom=8)
            if location and location.raw.get("address"):
                addr = location.raw["address"]
                city = (
                    addr.get("city")
                    or addr.get("town")
                    or addr.get("village")
                    or addr.get("county")
                    or ""
                )
                country = addr.get("country", "")
                parts = [p for p in [country, city] if p]
                return "/".join(parts) if parts else "Unknown Location"
        except Exception:
            pass

        return "Unknown Location"

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_gps(self, filepath: str):
        try:
            with open(filepath, "rb") as fh:
                tags = exifread.process_file(fh, details=False)
            lat = _dms_to_decimal(
                tags.get("GPS GPSLatitude"),
                tags.get("GPS GPSLatitudeRef"),
            )
            lon = _dms_to_decimal(
                tags.get("GPS GPSLongitude"),
                tags.get("GPS GPSLongitudeRef"),
            )
            return lat, lon
        except Exception:
            return None, None
