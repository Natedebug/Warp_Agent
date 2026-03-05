"""
Preset: By Type
Groups photos by their file extension/format.
"""
import os


TYPE_MAP = {
    ".jpg":  "JPEG",
    ".jpeg": "JPEG",
    ".png":  "PNG",
    ".heic": "HEIC",
    ".heif": "HEIF",
    ".gif":  "GIF",
    ".bmp":  "BMP",
    ".tiff": "TIFF",
    ".tif":  "TIFF",
    ".webp": "WebP",
    ".raw":  "RAW",
    ".cr2":  "RAW",
    ".nef":  "RAW",
    ".arw":  "RAW",
    ".dng":  "RAW",
    ".orf":  "RAW",
    ".mov":  "Video",
    ".mp4":  "Video",
    ".avi":  "Video",
    ".mkv":  "Video",
}


class ByTypePreset:
    id = "by_type"
    name = "By File Type"
    icon = "🗂️"
    description = "Groups photos by format — JPEG, PNG, HEIC, RAW, GIF, and more."

    def classify(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        return TYPE_MAP.get(ext, "Other")
