"""
Preset registry.
Each preset is loaded individually so a missing optional dependency
(e.g. nudenet, exifread, geopy) never breaks the import of unrelated presets.
"""


def _build_presets():
    presets = []

    try:
        from .by_date import ByDatePreset
        presets.append(ByDatePreset())
    except ImportError:
        pass

    try:
        from .by_type import ByTypePreset
        presets.append(ByTypePreset())
    except ImportError:
        pass

    try:
        from .by_size import BySizePreset
        presets.append(BySizePreset())
    except ImportError:
        pass

    try:
        from .by_location import ByLocationPreset
        presets.append(ByLocationPreset())
    except ImportError:
        pass

    try:
        from .nudity import NudityPreset
        presets.append(NudityPreset())
    except ImportError:
        pass

    return presets


ALL_PRESETS = _build_presets()
