# 📷 Photo Organizer

A self-contained desktop app that organizes your photo library into folders using smart sorting presets — including an on-device nudity filter.

---

## ✨ Features

| Preset | What it does |
|--------|-------------|
| 📅 By Date | Sorts into `YYYY / MM-Month` folders using photo EXIF date |
| 🗂️ By File Type | Groups by format — JPEG, PNG, HEIC, RAW, GIF, Video… |
| 📏 By File Size | Splits into Small (<1 MB), Medium (1–5 MB), Large (>5 MB) |
| 🌍 By Location | Groups by country/city using GPS data embedded in the photo |
| 🔞 Nudity Filter | Separates flagged photos from safe ones using a local AI model |

- **Move-only** — photos are moved, not duplicated
- **Safe naming** — duplicate filenames get a numbered suffix automatically
- **Cancel anytime** — stop mid-run and already-moved files stay organised
- **No internet required** — all processing happens on your computer

---

## 🚀 How to Run

### Option 1 — One command (recommended)
```bash
bash /path/to/photo_organizer/run.sh
```
This will:
1. Check that Python 3 is installed
2. Create a virtual environment inside the project folder
3. Install all dependencies automatically
4. Launch the app

### Option 2 — Manual (if you already have the dependencies)
```bash
cd photo_organizer
pip install -r requirements.txt
python main.py
```

---

## 📋 Requirements

- **macOS** (also works on Linux/Windows with minor path adjustments)
- **Python 3.10+** — download from [python.org](https://python.org) if needed
- Internet connection on **first run only** — the Nudity Filter preset downloads its AI model weights (~90 MB) once

---

## 🗂️ Project Structure

```
photo_organizer/
├── run.sh               ← one-click launcher
├── main.py              ← app entry point
├── requirements.txt
├── app/
│   ├── gui.py           ← the full GUI
│   ├── organizer.py     ← move logic
│   └── presets/
│       ├── by_date.py
│       ├── by_type.py
│       ├── by_size.py
│       ├── by_location.py
│       └── nudity.py
└── tests/
    └── test_presets.py
```

---

## 🧪 Running Tests

```bash
cd photo_organizer
python -m pytest tests/ -v
```

---

## ⚠️ Important Notes

- Photos are **permanently moved**. Back up your library before running if you're unsure.
- The **Nudity Filter** uses [NudeNet](https://github.com/notAI-tech/NudeNet), an open-source local model. Nothing is sent to the internet.
- The **By Location** preset requires an internet connection to look up place names from GPS coordinates. Photos without GPS data go into an `Unknown Location` folder.
