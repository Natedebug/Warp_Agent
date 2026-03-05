"""
Core organizer logic.
Scans a source directory for supported image/video files,
classifies each using the chosen preset, and moves them
into the destination directory.
"""
import os
import shutil
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable


SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".heic", ".heif",
    ".gif", ".bmp", ".tiff", ".tif", ".webp",
    ".raw", ".cr2", ".nef", ".arw", ".dng", ".orf",
    ".mov", ".mp4", ".avi", ".mkv",
}


@dataclass
class OrganizerResult:
    moved: int = 0
    skipped: int = 0
    errors: int = 0
    folder_counts: dict = field(default_factory=dict)
    error_files: list = field(default_factory=list)


def collect_images(source_dir: str, exclude_dir: str | None = None) -> list[str]:
    """Return a list of absolute paths to all supported files in source_dir (recursive).

    exclude_dir: if set, any path at or below this directory is skipped.
    This prevents re-scanning files already moved into a destination that
    lives inside the source tree.
    """
    exclude = Path(exclude_dir).resolve() if exclude_dir else None
    files = []
    for root, dirs, filenames in os.walk(source_dir):
        root_resolved = Path(root).resolve()
        # Prune the walk if we've entered the excluded subtree
        if exclude and (root_resolved == exclude or exclude in root_resolved.parents):
            dirs.clear()
            continue
        for fname in filenames:
            if Path(fname).suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(os.path.join(root, fname))
    return sorted(files)


def _safe_dest_path(dest_folder: str, filename: str) -> str:
    """Return a destination path that won't overwrite an existing file."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_folder, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_folder, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def run_organizer(
    source_dir: str,
    dest_dir: str,
    preset,
    progress_callback: Callable[[int, int, str], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> OrganizerResult:
    """
    Move all supported images from source_dir into dest_dir/<preset_folder>.

    progress_callback(current, total, current_filename) is called AFTER each
    file is processed so the count reflects actual outcomes, not intent.
    cancel_event can be set to stop mid-run; remaining files are counted as skipped.
    """
    result = OrganizerResult()
    # Exclude dest_dir from the scan in case it lives inside source_dir
    files = collect_images(source_dir, exclude_dir=dest_dir)
    total = len(files)

    for i, filepath in enumerate(files, start=1):
        if cancel_event and cancel_event.is_set():
            # Count all unprocessed files as skipped
            result.skipped += total - i + 1
            break

        filename = os.path.basename(filepath)

        try:
            subfolder = preset.classify(filepath)
            folder_path = os.path.join(dest_dir, subfolder)
            os.makedirs(folder_path, exist_ok=True)

            dest_path = _safe_dest_path(folder_path, filename)
            shutil.move(filepath, dest_path)

            result.moved += 1
            result.folder_counts[subfolder] = result.folder_counts.get(subfolder, 0) + 1

        except Exception as exc:
            result.errors += 1
            result.error_files.append((filename, str(exc)))

        # Progress fires AFTER processing so UI reflects real outcome
        if progress_callback:
            progress_callback(i, total, filename)

    return result
