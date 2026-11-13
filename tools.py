import os
import sys
from pathlib import Path
import flet as ft

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
sys.path.insert(0, str(BASE_DIR))

import string
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import filedialog

import flet as ft
import pyautogui
import qrcode
from PIL import Image

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False
APP_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent


class ToolViews:
    def __init__(self, page: ft.Page, wrap_callback, notify_callback):
        self.page = page
        self.wrap = wrap_callback
        self.notify = notify_callback
        self.clicker_running = False
        notes_dir = Path(os.environ.get("APPDATA", Path.home())) / "delNikoNotes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        self.notes_path = notes_dir / "delniko_notes.txt"
    def password_gen(self):
        output = ft.TextField(value="", read_only=True, width=360, text_size=16)
        length_slider = ft.Slider(min=8, max=32, divisions=24, value=16, label="{value}", width=360)
        symbols_cb = ft.Checkbox(label="Include symbols (!@#$)", value=True)

        def generate(e):
            chars = string.ascii_letters + string.digits
            if symbols_cb.value:
                chars += "!@#$%^&*"
            output.value = "".join(secrets.choice(chars) for _ in range(int(length_slider.value)))
            self.page.update()

        def copy_pwd(e):
            if output.value:
                self.page.set_clipboard(output.value)
                self.notify("Copied to clipboard")

        generate(None)
        self.wrap(
            "Password Gen",
            [
                ft.Text("Length", size=14, color="#E5E7EB"),
                length_slider,
                symbols_cb,
                ft.Row([output, ft.IconButton(icon=ft.Icons.COPY, on_click=copy_pwd)]),
                ft.Button("Generate", bgcolor="#4F46E5", color="white", on_click=generate),
            ],
        )

    def auto_clicker(self):
        info_text = ft.Text("Fixed speed: 5 CPS (Press F6 anytime to stop)", size=14, color="#E5E7EB")
        status_text = ft.Text("Status: Stopped", size=14, color="#9CA3AF")
        toggle_btn = ft.Button("Start (5 CPS)", bgcolor="#0EA5E9", color="white", width=180)

        def stop_state():
            self.clicker_running = False
            toggle_btn.text = "Start (5 CPS)"
            toggle_btn.bgcolor = "#0EA5E9"
            status_text.value = "Status: Stopped"
            status_text.color = "#F43F5E"
            try:
                self.page.update()
            except Exception:
                pass

        def click_loop():
            for sec in (3, 2, 1):
                if not self.clicker_running:
                    return
                status_text.value = f"Starting in {sec}s... (Press F6 to abort)"
                self.page.update()
                time.sleep(1)

            status_text.value = "Status: Running at 5 CPS (Press F6 to stop)"
            status_text.color = "#10B981"
            self.page.update()

            while self.clicker_running:
                if ctypes.windll.user32.GetAsyncKeyState(0x75) & 0x8000:
                    stop_state()
                    break
                pyautogui.click()
                time.sleep(0.2)

        def toggle_clicker(e):
            if not self.clicker_running:
                self.clicker_running = True
                toggle_btn.text = "Stop"
                toggle_btn.bgcolor = "#F43F5E"
                status_text.color = "#F59E0B"
                self.page.update()
                threading.Thread(target=click_loop, daemon=True).start()
            else:
                stop_state()

        toggle_btn.on_click = toggle_clicker
        self.wrap("Auto Clicker", [info_text, status_text, toggle_btn])

    def shutdown_timer(self):
        mins_input = ft.TextField(label="Minutes", value="30", width=200)

        def set_timer(e):
            try:
                seconds = int(mins_input.value) * 60
                os.system(f"shutdown -s -t {seconds}")
                self.notify(f"PC will shut down in {mins_input.value} min")
            except ValueError:
                self.notify("Enter a valid number")

        def cancel_timer(e):
            os.system("shutdown -a")
            self.notify("Shutdown cancelled")

        self.wrap(
            "Shutdown Timer",
            [
                mins_input,
                ft.Row(
                    [
                        ft.Button("Schedule", bgcolor="#EC4899", color="white", on_click=set_timer),
                        ft.Button("Cancel Timer", bgcolor="#374151", color="white", on_click=cancel_timer),
                    ]
                ),
            ],
        )

    def qr_gen(self):
        url_input = ft.TextField(label="Text or URL", width=400)
        preview = ft.Image(src=b"", width=180, height=180, visible=False)
        save_btn = ft.Button("Save As...", bgcolor="#374151", color="white", visible=False)
        current_qr = {"img": None}

        def build_qr(e):
            if not url_input.value.strip():
                return
            img = qrcode.make(url_input.value.strip())
            current_qr["img"] = img

            buf = BytesIO()
            img.save(buf, format="PNG")
            preview.src = buf.getvalue()
            preview.visible = True
            save_btn.visible = True
            self.page.update()

        def save_qr(e):
            if not current_qr["img"]:
                return
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png")],
                initialfile="qr_code.png",
            )
            root.destroy()
            if file_path:
                current_qr["img"].save(file_path)
                self.notify(f"Saved: {Path(file_path).name}")

        save_btn.on_click = save_qr

        self.wrap(
            "QR Generator",
            [
                url_input,
                ft.Row(
                    [
                        ft.Button("Create QR", bgcolor="#10B981", color="white", on_click=build_qr),
                        save_btn,
                    ]
                ),
                preview,
            ],
        )

    def temp_cleaner(self):
        log_text = ft.Text("Ready to clean system temp directory", color="#E5E7EB")
        clean_btn = ft.Button("Run Cleaner", bgcolor="#F59E0B", color="white")

        def run_cleanup():
            clean_btn.disabled = True
            log_text.value = "Cleaning..."
            self.page.update()

            dirs = {Path(tempfile.gettempdir()).resolve()}
            for var in ("TEMP", "TMP"):
                if path := os.environ.get(var):
                    dirs.add(Path(path).resolve())

            removed = 0
            for base in dirs:
                if not base.exists():
                    continue
                for root, subdirs, files in os.walk(base, topdown=False):
                    root_p = Path(root)
                    for f in files:
                        try:
                            (root_p / f).unlink()
                            removed += 1
                        except OSError:
                            pass
                    for d in subdirs:
                        try:
                            (root_p / d).rmdir()
                            removed += 1
                        except OSError:
                            pass

            log_text.value = f"Cleaned {removed} items"
            clean_btn.disabled = False
            self.notify("Cleanup finished")
            self.page.update()

        clean_btn.on_click = lambda e: threading.Thread(target=run_cleanup, daemon=True).start()

        self.wrap(
            "Temp Cleaner",
            [log_text, clean_btn],
        )
    def quick_notes(self):
        initial_text = self.notes_path.read_text(encoding="utf-8") if self.notes_path.exists() else ""
        editor = ft.TextField(value=initial_text, multiline=True, min_lines=8, max_lines=10, width=600)

        def save_notes(e):
            self.notes_path.write_text(editor.value, encoding="utf-8")
            self.notify("Notes saved")

        self.wrap(
            "Quick Notes",
            [
                editor,
                ft.Button("Save", bgcolor="#8B5CF6", color="white", on_click=save_notes),
            ],
        )

    def net_ping(self):
        host_input = ft.TextField(label="Host", value="8.8.8.8", width=250)
        result_text = ft.Text("", font_family="Consolas", size=12, color="#A7F3D0")

        def run_ping(e):
            host = host_input.value.strip() or "8.8.8.8"
            result_text.value = "Pinging..."
            self.page.update()
            proc = subprocess.run(
                f"chcp 437 > nul && ping -n 2 {host}",
                shell=True,
                capture_output=True,
                text=True,
            )
            result_text.value = proc.stdout or proc.stderr
            self.page.update()

        self.wrap(
            "Net Ping",
            [
                ft.Row([host_input, ft.Button("Ping", bgcolor="#06B6D4", color="white", on_click=run_ping)]),
                result_text,
            ],
        )

    def img_converter(self):
        path_input = ft.TextField(label="Full image path (e.g. C:\\pic.png)", width=420)
        format_dd = ft.Dropdown(
            width=150,
            value="JPEG",
            options=[ft.dropdown.Option("JPEG"), ft.dropdown.Option("PNG"), ft.dropdown.Option("WEBP")],
        )

        def convert_img(e):
            src = Path(path_input.value.strip().strip('"'))
            if not src.exists():
                self.notify("File not found")
                return
            ext = format_dd.value.lower()
            dst = src.with_name(f"{src.stem}_converted.{ext}")
            img = Image.open(src).convert("RGB") if ext == "jpeg" else Image.open(src)
            img.save(dst, format_dd.value)
            self.notify(f"Saved: {dst.name}")

        self.wrap(
            "Img Converter",
            [
                path_input,
                ft.Row([format_dd, ft.Button("Convert", bgcolor="#F43F5E", color="white", on_click=convert_img)]),
            ],
        )

    def file_sorter(self):
        default_dir = Path.home() / "Downloads"
        if not default_dir.exists():
            default_dir = Path.home()

        path_input = ft.TextField(
            label="Target folder",
            value=str(default_dir),
            width=420,
        )
        status = ft.Text("Ready", color="#E5E7EB")

        def pick_folder(e):
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected = filedialog.askdirectory(initialdir=path_input.value)
            root.destroy()
            if selected:
                path_input.value = str(Path(selected))
                self.page.update()

        def sort_files(e):
            target_root = Path(path_input.value.strip().strip('"'))
            if not target_root.exists() or not target_root.is_dir():
                self.notify("Folder not found")
                return

            categories = {
                "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".ico"},
                "Videos": {".mp4", ".mkv", ".avi", ".mov", ".webm"},
                "Audio": {".mp3", ".wav", ".ogg", ".flac", ".m4a"},
                "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
                "Programs": {".exe", ".msi", ".bat", ".cmd"},
                "Docs": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"},
                "Torrents": {".torrent"},
            }

            moved = 0
            for item in list(target_root.iterdir()):
                if not item.is_file() or item.name.lower() == "desktop.ini":
                    continue

                ext = item.suffix.lower()
                dest_folder = "Other"
                for folder, exts in categories.items():
                    if ext in exts:
                        dest_folder = folder
                        break

                target_dir = target_root / dest_folder
                target_dir.mkdir(exist_ok=True)
                dest_path = target_dir / item.name

                counter = 1
                while dest_path.exists():
                    dest_path = target_dir / f"{item.stem}_{counter}{item.suffix}"
                    counter += 1

                try:
                    shutil.move(str(item), str(dest_path))
                    moved += 1
                except OSError:
                    pass

            status.value = f"Sorted {moved} files"
            self.notify(f"Sorted {moved} files")
            self.page.update()

        self.wrap(
            "File Sorter",
            [
                ft.Row(
                    [
                        path_input,
                        ft.Button("Browse", bgcolor="#374151", color="white", on_click=pick_folder),
                    ]
                ),
                status,
                ft.Button("Sort Folder", bgcolor="#14B8A6", color="white", on_click=sort_files),
            ],
        )

    def unit_calc(self):
        mb_input = ft.TextField(label="Megabytes (MB)", width=220)
        res_label = ft.Text("GB: 0.00 | TB: 0.0000", size=16, weight=ft.FontWeight.BOLD)

        def calc(e):
            try:
                mb = float(mb_input.value)
                res_label.value = f"GB: {mb / 1024:.2f} | TB: {mb / (1024 ** 2):.4f}"
            except ValueError:
                res_label.value = "Invalid input"
            self.page.update()

        mb_input.on_change = calc
        self.wrap("Unit Calc", [mb_input, res_label])