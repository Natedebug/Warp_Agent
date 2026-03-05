"""
Photo Organizer – GUI
Built with customtkinter for a modern, user-friendly look.

Flow:
  Step 1 – Pick source folder
  Step 2 – Pick destination folder
  Step 3 – Choose a preset
  Step 4 – Running (progress bar + live counter)
  Step 5 – Results summary
"""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.organizer import run_organizer, collect_images
from app.presets import ALL_PRESETS


# ── Theme ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT   = "#4A9EFF"
CARD_BG  = "#2B2D31"
WIN_BG   = "#1E1F22"
TEXT_SEC = "#9B9DA0"


class PhotoOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📷  Photo Organizer")
        self.geometry("720x560")
        self.minsize(640, 500)
        self.configure(fg_color=WIN_BG)
        self.resizable(True, True)

        # State
        self.source_dir  = tk.StringVar()
        self.dest_dir    = tk.StringVar()
        self.selected_preset = None
        self._cancel_event   = threading.Event()

        # Container that holds all "pages"
        self.container = ctk.CTkFrame(self, fg_color=WIN_BG)
        self.container.pack(fill="both", expand=True, padx=24, pady=24)

        self._show_step1()

    # ══════════════════════════════════════════════════════════════════════════
    # Step 1 – Source folder
    # ══════════════════════════════════════════════════════════════════════════
    def _show_step1(self):
        self._clear()
        self._header("Step 1 of 3", "Where are your photos?")
        self._subtitle("Choose the folder that contains the photos you want to organise.")

        frame = ctk.CTkFrame(self.container, fg_color=CARD_BG, corner_radius=12)
        frame.pack(fill="x", pady=(20, 8))

        entry = ctk.CTkEntry(
            frame, textvariable=self.source_dir,
            placeholder_text="e.g.  /Users/you/Pictures",
            height=42, font=ctk.CTkFont(size=14),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(16, 8), pady=14)

        ctk.CTkButton(
            frame, text="Browse", width=100, height=42,
            command=self._browse_source,
        ).pack(side="right", padx=(0, 16), pady=14)

        self._nav_buttons(back=None, next_cmd=self._go_step2, next_label="Next →")

    def _browse_source(self):
        d = filedialog.askdirectory(title="Select your photo folder")
        if d:
            self.source_dir.set(d)

    def _go_step2(self):
        if not self.source_dir.get().strip():
            messagebox.showwarning("No folder selected", "Please choose a source folder first.")
            return
        self._show_step2()

    # ══════════════════════════════════════════════════════════════════════════
    # Step 2 – Destination folder
    # ══════════════════════════════════════════════════════════════════════════
    def _show_step2(self):
        self._clear()
        self._header("Step 2 of 3", "Where should the organised photos go?")
        self._subtitle("A new folder structure will be created here. Your originals will be moved.")

        frame = ctk.CTkFrame(self.container, fg_color=CARD_BG, corner_radius=12)
        frame.pack(fill="x", pady=(20, 8))

        entry = ctk.CTkEntry(
            frame, textvariable=self.dest_dir,
            placeholder_text="e.g.  /Users/you/Organised Photos",
            height=42, font=ctk.CTkFont(size=14),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(16, 8), pady=14)

        ctk.CTkButton(
            frame, text="Browse", width=100, height=42,
            command=self._browse_dest,
        ).pack(side="right", padx=(0, 16), pady=14)

        # Warning label
        ctk.CTkLabel(
            self.container,
            text="⚠️  Photos will be MOVED — not copied. Make sure you have a backup if needed.",
            text_color="#F0A500",
            font=ctk.CTkFont(size=12),
            wraplength=620,
        ).pack(pady=(4, 0))

        self._nav_buttons(back=self._show_step1, next_cmd=self._go_step3, next_label="Next →")

    def _browse_dest(self):
        d = filedialog.askdirectory(title="Select destination folder")
        if d:
            self.dest_dir.set(d)

    def _go_step3(self):
        if not self.dest_dir.get().strip():
            messagebox.showwarning("No folder selected", "Please choose a destination folder first.")
            return
        from pathlib import Path
        src = Path(self.source_dir.get().strip()).resolve()
        dst = Path(self.dest_dir.get().strip()).resolve()
        if dst == src:
            messagebox.showwarning("Same folder", "Source and destination cannot be the same folder.")
            return
        # Prevent dest nested inside source — collect_images would scan moved files
        if dst.is_relative_to(src):
            messagebox.showwarning(
                "Invalid destination",
                "The destination folder cannot be inside the source folder.\n\n"
                f"Choose a folder outside of:\n{src}",
            )
            return
        self._show_step3()

    # ══════════════════════════════════════════════════════════════════════════
    # Step 3 – Choose preset
    # ══════════════════════════════════════════════════════════════════════════
    def _show_step3(self):
        self._clear()
        self._header("Step 3 of 3", "How should your photos be organised?")
        self._subtitle("Pick one of the sorting methods below.")

        scroll = ctk.CTkScrollableFrame(self.container, fg_color=WIN_BG, height=320)
        scroll.pack(fill="both", expand=True, pady=(12, 0))

        self._preset_btns = {}
        for preset in ALL_PRESETS:
            self._preset_card(scroll, preset)

        self._organise_btn = ctk.CTkButton(
            self.container,
            text="Organise My Photos",
            height=48,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
            command=self._confirm_and_run,
        )
        self._organise_btn.pack(fill="x", pady=(14, 0))

        self._nav_buttons(back=self._show_step2, next_cmd=None)

    def _preset_card(self, parent, preset):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
        card.pack(fill="x", pady=6, padx=4)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=16, pady=14)

        ctk.CTkLabel(
            left,
            text=f"{preset.icon}  {preset.name}",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            left,
            text=preset.description,
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=12),
            anchor="w",
            wraplength=500,
            justify="left",
        ).pack(fill="x", pady=(4, 0))

        btn = ctk.CTkButton(
            card, text="Select", width=90,
            fg_color="transparent", border_width=2, border_color=ACCENT,
            command=lambda p=preset, c=card: self._select_preset(p, c),
        )
        btn.pack(side="right", padx=16, pady=14)
        self._preset_btns[preset.id] = (card, btn)

    def _select_preset(self, preset, card):
        # Reset all cards
        for pid, (c, b) in self._preset_btns.items():
            c.configure(border_width=0)
            b.configure(text="Select", fg_color="transparent", border_width=2, border_color=ACCENT)

        # Highlight selected
        card.configure(border_width=2, border_color=ACCENT)
        self._preset_btns[preset.id][1].configure(
            text="✓ Selected", fg_color=ACCENT, border_width=0
        )
        self.selected_preset = preset
        self._organise_btn.configure(state="normal")

    # ══════════════════════════════════════════════════════════════════════════
    # Confirmation dialog → Step 4 – Progress
    # ══════════════════════════════════════════════════════════════════════════
    def _confirm_and_run(self):
        src = self.source_dir.get().strip()
        files = collect_images(src)
        count = len(files)

        if count == 0:
            messagebox.showinfo("No photos found", f"No supported photo files were found in:\n{src}")
            return

        ok = messagebox.askyesno(
            "Ready to organise?",
            f"Found {count} photo(s) in:\n{src}\n\n"
            f"They will be MOVED into:\n{self.dest_dir.get().strip()}\n\n"
            f"Preset: {self.selected_preset.icon} {self.selected_preset.name}\n\n"
            "This cannot be undone. Continue?",
        )
        if ok:
            self._show_step4(count)

    # ══════════════════════════════════════════════════════════════════════════
    # Step 4 – Progress
    # ══════════════════════════════════════════════════════════════════════════
    def _show_step4(self, total: int):
        self._clear()
        self._cancel_event.clear()

        self._header("Organising…", f"Moving {total} photo(s) using  {self.selected_preset.icon} {self.selected_preset.name}")

        self._prog_bar = ctk.CTkProgressBar(self.container, height=18, corner_radius=9)
        self._prog_bar.set(0)
        self._prog_bar.pack(fill="x", pady=(24, 8))

        self._prog_label = ctk.CTkLabel(
            self.container, text="Starting…",
            text_color=TEXT_SEC, font=ctk.CTkFont(size=12),
        )
        self._prog_label.pack()

        self._counter_label = ctk.CTkLabel(
            self.container, text=f"0 / {total}",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self._counter_label.pack(pady=(16, 0))

        ctk.CTkButton(
            self.container, text="Cancel", width=120,
            fg_color="#C0392B", hover_color="#922B21",
            command=self._cancel_event.set,
        ).pack(pady=(24, 0))

        # Run in background thread
        threading.Thread(
            target=self._run_organizer_thread,
            args=(total,),
            daemon=True,
        ).start()

    def _run_organizer_thread(self, total: int):
        def on_progress(current, tot, filename):
            pct = current / tot if tot else 0
            self.after(0, self._update_progress, current, tot, pct, filename)

        result = run_organizer(
            source_dir=self.source_dir.get().strip(),
            dest_dir=self.dest_dir.get().strip(),
            preset=self.selected_preset,
            progress_callback=on_progress,
            cancel_event=self._cancel_event,
        )
        self.after(0, self._show_step5, result)

    def _update_progress(self, current, total, pct, filename):
        self._prog_bar.set(pct)
        self._prog_label.configure(text=filename)
        self._counter_label.configure(text=f"{current} / {total}")

    # ══════════════════════════════════════════════════════════════════════════
    # Step 5 – Results summary
    # ══════════════════════════════════════════════════════════════════════════
    def _show_step5(self, result):
        self._clear()

        cancelled = self._cancel_event.is_set()
        title = "Cancelled" if cancelled else "Done! 🎉"
        self._header(title, "Here's what happened:")

        # Summary cards row
        row = ctk.CTkFrame(self.container, fg_color="transparent")
        row.pack(fill="x", pady=(20, 0))
        row.columnconfigure((0, 1, 2), weight=1, uniform="col")

        self._stat_card(row, 0, "✅ Moved",   str(result.moved),  "#27AE60")
        self._stat_card(row, 1, "⏭️ Skipped", str(result.skipped), "#F39C12")
        self._stat_card(row, 2, "❌ Errors",  str(result.errors),  "#C0392B")

        # Folder breakdown
        if result.folder_counts:
            ctk.CTkLabel(
                self.container, text="Folders created:",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            ).pack(fill="x", pady=(20, 4))

            scroll = ctk.CTkScrollableFrame(self.container, fg_color=CARD_BG, corner_radius=12, height=160)
            scroll.pack(fill="x")

            for folder, count in sorted(result.folder_counts.items()):
                ctk.CTkLabel(
                    scroll,
                    text=f"  📁  {folder}  —  {count} file{'s' if count != 1 else ''}",
                    anchor="w", font=ctk.CTkFont(size=12),
                ).pack(fill="x", padx=12, pady=2)

        # Error details
        if result.error_files:
            ctk.CTkLabel(
                self.container,
                text=f"⚠️  {result.errors} file(s) could not be moved. They remain in the source folder.",
                text_color="#F0A500", font=ctk.CTkFont(size=12), wraplength=620,
            ).pack(pady=(12, 0))

        # Action buttons
        btn_row = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            btn_row, text="Organise More Photos",
            command=self._reset,
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Quit",
            fg_color="#3A3B3E", hover_color="#555",
            command=self.quit,
        ).pack(side="right", expand=True, fill="x", padx=(8, 0))

    def _stat_card(self, parent, col, label, value, color):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=col, padx=6, sticky="nsew")
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color=color).pack(pady=(16, 2))
        ctk.CTkLabel(card, text=label,  font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(pady=(0, 16))

    # ══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════════════════
    def _reset(self):
        self.source_dir.set("")
        self.dest_dir.set("")
        self.selected_preset = None
        self._show_step1()

    def _clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _header(self, step_text: str, title: str):
        ctk.CTkLabel(
            self.container, text=step_text,
            text_color=ACCENT, font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            self.container, text=title,
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

    def _subtitle(self, text: str):
        ctk.CTkLabel(
            self.container, text=text,
            text_color=TEXT_SEC, font=ctk.CTkFont(size=13),
            anchor="w", wraplength=640,
        ).pack(fill="x", pady=(4, 0))

    def _nav_buttons(self, back, next_cmd, next_label="Next →"):
        row = ctk.CTkFrame(self.container, fg_color="transparent")
        row.pack(fill="x", side="bottom", pady=(16, 0))

        if back:
            ctk.CTkButton(
                row, text="← Back", width=110,
                fg_color="#3A3B3E", hover_color="#555",
                command=back,
            ).pack(side="left")

        if next_cmd:
            ctk.CTkButton(
                row, text=next_label, width=110,
                command=next_cmd,
            ).pack(side="right")
