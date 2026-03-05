"""
Photo Organizer – entry point.
Run:  python main.py
  or:  bash run.sh   (auto-installs dependencies first)
"""
import sys
import os

# Ensure the project root is on the path so `app` imports work
sys.path.insert(0, os.path.dirname(__file__))

from app.gui import PhotoOrganizerApp


def main():
    app = PhotoOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
