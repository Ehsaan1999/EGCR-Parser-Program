import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk  # pillow
from document_processor import DocumentProcessor
import time


class FileStagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gallo Parser")
        self.geometry("650x780") 
        self.resizable(False, False)
        
        # Initialize variables
        self.selected_folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")
        self.generated_pdf_path = None
        self.banner_height = 0 
        self._timer_running = False
        self._start_time = None
        self._processing_complete = False
        
        # Initialize progress state early to prevent KeyErrors
        self._progress_state = {
            "current": None,
            "total": None,
            "filename": None,
            "stage": "Waiting for folder...",
            "elapsed": "Elapsed: 00:00",
        }

        self._load_assets()
        self._build_ui()

    # ---------------- Assets ----------------

    def _load_assets(self):
        """Load logo and banner images"""
        # Handling for PyInstaller / Base Directory
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets")

        try:
            # App icon (top-left)
            logo_path = os.path.join(assets_dir, "logo.jpg")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path).resize((32, 32), Image.LANCZOS)
                self.logo_icon = ImageTk.PhotoImage(logo_img)
                self.iconphoto(False, self.logo_icon)
            
            # Banner load
            banner_path = os.path.join(assets_dir, "banner.jpg")
            if os.path.exists(banner_path):
                raw_banner = Image.open(banner_path)
                aspect_ratio = raw_banner.height / raw_banner.width
                self.banner_height = int((650 * aspect_ratio) * 0.5)
                banner_img = raw_banner.resize((650, self.banner_height), Image.LANCZOS)
                self.banner_photo = ImageTk.PhotoImage(banner_img)
            else:
                self.banner_photo = None
        except Exception as e:
            print(f"Asset warning: {e}")
            self.banner_photo = None

    # ---------------- UI ----------------

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}
        
        # Banner display
        current_y = 0
        if self.banner_photo:
            banner_label = tk.Label(self, image=self.banner_photo, bg=self["bg"])
            banner_label.place(x=0, y=0)
            current_y = self.banner_height + 10
        else:
            current_y = 20

        # -------- Input Folder --------
        frm = ttk.LabelFrame(self, text="Input Folder")
        frm.place(x=20, y=current_y, width=610, height=90)

        self.entry_folder = ttk.Entry(frm, textvariable=self.selected_folder_var, width=60, justify='right')
        self.entry_folder.grid(row=0, column=0, **pad)
        
        ttk.Button(frm, text="Browse...", command=self._choose_folder).grid(
            row=0, column=1, **pad
        )

        self.process_btn = ttk.Button(
            frm, text="Process Folder", command=self._stage_and_process
        )
        self.process_btn.grid(row=1, column=0, sticky="w", **pad)

        # -------- Begin Processing --------
        processing_frame_height = 155
        frm_actions = ttk.LabelFrame(self, text="Begin Processing")
        frm_actions.place(x=20, y=current_y + 100, width=610, height=processing_frame_height)

        self.view_btn = ttk.Button(
            frm_actions,
            text="View PDF",
            command=self._view_pdf,
            state="disabled",
        )
        self.view_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Label for multi-line status updates
        ttk.Label(frm_actions, textvariable=self.status_var, justify="left").grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )

        self.loader = ttk.Progressbar(
            frm_actions, mode="indeterminate", length=180
        )

        # -------- Executive Summary Area --------
        self.summary_container = ttk.Frame(self)
        summary_y = current_y + 100 + processing_frame_height + 10
        self.summary_container.place(x=20, y=summary_y, width=610, height=400)

    def _create_summary_table(self, parent, title, data_dict):
        frame = ttk.Frame(parent)
        frame.pack(pady=5, fill="x")

        ttk.Label(frame, text=f"Overall Status: {title}", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))

        table_frame = tk.Frame(frame, bg="black")
        table_frame.pack(fill="x")

        headers = ["Status", "Exact", "Partial", "No Match", "Missing"]
        cols = ["Exact", "Partial", "No Match", "Missing"]

        for i, h in enumerate(headers):
            lbl = tk.Label(table_frame, text=h, font=("Arial", 9, "bold"), bg="white", padx=10, pady=5, borderwidth=1, relief="flat")
            lbl.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        tk.Label(table_frame, text="REVIEW REQUIRED", fg="red", font=("Arial", 9, "bold"), bg="white", padx=10, pady=5).grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        
        for i, col_name in enumerate(cols):
            val = data_dict.get(col_name, 0)
            tk.Label(table_frame, text=str(val), bg="white", padx=10, pady=5).grid(row=1, column=i+1, sticky="nsew", padx=1, pady=1)

        for i in range(5):
            table_frame.grid_columnconfigure(i, weight=1)

    def _display_summary(self, file_name, notice_summary, rb_summary, plus_count):
        for widget in self.summary_container.winfo_children():
            widget.destroy()

        name_container = ttk.Frame(self.summary_container)
        name_container.pack(pady=(5, 10))
        
        if file_name:
            name_parts = [p.strip() for p in file_name.split('|')]
            for part in name_parts:
                lbl = tk.Label(name_container, text=part, font=("Arial", 10, "bold"), wraplength=580, justify="center")
                lbl.pack(anchor="center")

        canvas = tk.Canvas(self.summary_container, height=2, bg="black", highlightthickness=0)
        canvas.pack(fill="x", pady=5, padx=20)

        self._create_summary_table(self.summary_container, "Notice", notice_summary)
        self._create_summary_table(self.summary_container, "RB", rb_summary)

        if plus_count is not None and plus_count > 0:
            plus_lbl = tk.Label(self.summary_container, text=f"+{plus_count}", font=("Arial", 14, "bold"))
            plus_lbl.pack(pady=20, anchor="center")
    
    def _clear_summary(self):
        for widget in self.summary_container.winfo_children():
            widget.destroy()

    # ---------------- Helpers ----------------

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.selected_folder_var.set(folder)
            self.entry_folder.xview_moveto(1.0)

    def _stage_and_process(self):
        folder_path = self.selected_folder_var.get().strip()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        threading.Thread(
            target=self._run_processor, args=(folder_path,), daemon=True
        ).start()

    def _run_processor(self, folder_path):
        self.after(0, self._clear_summary)
        self.process_btn.config(state="disabled")
        self.view_btn.config(state="disabled")
        self.status_var.set("Processing documents...")
        self.loader.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.loader.start(10)
        
        self._start_time = time.time()
        self._timer_running = True
        self._processing_complete = False
        self._tick_timer()

        try:
            processor = DocumentProcessor(
                folder_path,
                progress_callback=self._update_progress
            )

            result = processor.process()
            path, name, notice_sum, rb_sum, p_count, *extra = result

            self.generated_pdf_path = path
            self.after(0, lambda: self._display_summary(name, notice_sum, rb_sum, p_count))

            self.view_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))
            self.status_var.set("Error occurred.")
        finally:
            self._stop_timer()
            self.after(0, self.loader.stop)
            self.after(0, self.loader.grid_forget)
            self.after(0, lambda: self.process_btn.config(state="normal"))

    def _update_progress(self, current=None, total=None, filename=None, stage=None):
        """Thread-safe UI progress update"""
        state = self._progress_state

        if current is not None: state["current"] = current
        if total is not None: state["total"] = total
        if filename is not None: state["filename"] = filename
        if stage is not None: state["stage"] = stage

        def _update():
            lines = []
            
            # Use 'is not None' to allow '0' (the first index) to pass
            if state.get("current") is not None and state.get("total") is not None:
                lines.append(f"Processing {state['current']}/{state['total']}")

            if state.get("filename"):
                lines.append(f"Current file: {state['filename']}")

            if self._processing_complete:
                lines.append("Processing complete.")
            elif state.get("stage"):
                lines.append(state["stage"])

            if state.get("elapsed"):
                lines.append(state["elapsed"])

            self.status_var.set("\n".join(lines))

        self.after(0, _update)

    def _view_pdf(self):
        if not self.generated_pdf_path or not os.path.exists(self.generated_pdf_path):
            messagebox.showerror("Error", "PDF not found.")
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(self.generated_pdf_path)
            elif sys.platform.startswith("darwin"):
                os.system(f"open '{self.generated_pdf_path}'")
            else:
                os.system(f"xdg-open '{self.generated_pdf_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")

    def _tick_timer(self):
        if not self._timer_running:
            return

        elapsed = int(time.time() - self._start_time)
        mins, secs = divmod(elapsed, 60)
        self._progress_state["elapsed"] = f"Elapsed: {mins:02d}:{secs:02d}"
        self._update_progress()
        self.after(1000, self._tick_timer)

    def _stop_timer(self):
        self._timer_running = False
        self._processing_complete = True
        
        if self._start_time:
            elapsed = int(time.time() - self._start_time)
            mins, secs = divmod(elapsed, 60)
            self._progress_state["elapsed"] = f"Elapsed: {mins:02d}:{secs:02d}"
        self._update_progress()


if __name__ == "__main__":
    app = FileStagerApp()
    app.mainloop()