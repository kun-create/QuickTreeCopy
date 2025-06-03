import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk
import os
from pathlib import Path
import threading
from tkfontawesome import icon_to_image

class TreeViewerApp:
    def __init__(self):
        self.detect_gpu()

        self.root = tk.Tk()
        self.root.title("Quick Tree Copy")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        sv_ttk.set_theme("dark")

        self.tv_font = ("Segoe UI", 12)
        self.rowheight = self.compute_needed_rowheight(self.tv_font)

        self.load_icons()
        self.setup_styles()

        self.tree_structure = None
        self.current_path = None

        self.tree_style = tk.StringVar(value="modern")
        self.tree_style.trace_add("write", self.on_style_change)

        self.setup_ui()

    def detect_gpu(self):
        print("Renderer: CPU only (Tkinter does not support GPU acceleration)")

    def compute_needed_rowheight(self, font):
        temp = ttk.Label(self.root, text="Ay", font=font)
        temp.pack_forget()
        self.root.update_idletasks()
        needed = temp.winfo_reqheight() + 4
        temp.destroy()
        return needed

    def load_icons(self):
        scale = 0.13
        raw_folder = icon_to_image("folder", fill="#ffffff", scale=scale)
        raw_folder_o = icon_to_image("folder-open", fill="#ffffff", scale=scale)
        raw_file = icon_to_image("file", fill="#ffffff", scale=scale)
        raw_browse = icon_to_image("folder-open", fill="#ffffff", scale=scale)
        raw_gen = icon_to_image("sync-alt", fill="#ffffff", scale=scale)
        raw_copy = icon_to_image("copy", fill="#ffffff", scale=scale)
        raw_lock = icon_to_image("lock", fill="#ffffff", scale=scale)

        def shrink_to_fit(photo):
            max_h = self.rowheight - 2
            img = photo
            while img.height() > max_h:
                img = img.subsample(2, 2)
            return img

        self.fa_images = {
            "folder": shrink_to_fit(raw_folder),
            "folder_open": shrink_to_fit(raw_folder_o),
            "file": shrink_to_fit(raw_file),
            "browse": shrink_to_fit(raw_browse),
            "generate": shrink_to_fit(raw_gen),
            "copy": shrink_to_fit(raw_copy),
            "lock": shrink_to_fit(raw_lock),
        }

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Card.TFrame", relief="flat", borderwidth=1)
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Action.TButton", padding=(12, 8))
        style.configure("Primary.TButton", padding=(12, 8))
        style.configure(
            "Custom.Treeview",
            rowheight=self.rowheight,
            font=self.tv_font
        )
        style.configure("Custom.Treeview.Heading", font=("Segoe UI", 11, "bold"))

    def setup_ui(self):
        main_container = ttk.Frame(self.root, padding=(20, 20))
        main_container.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_container, style="Card.TFrame", padding=(20, 15))
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, text="Quick Tree Copy", style="Header.TLabel")
        title_label.pack(anchor="w", pady=(0, 10))

        path_frame = ttk.Frame(header_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))

        dir_label = ttk.Label(
            path_frame,
            image=self.fa_images["folder"],
            text="  Directory Path:",
            font=("Segoe UI", 10),
            compound="left"
        )
        dir_label.pack(anchor="w", pady=(0, 5))

        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(
            path_input_frame,
            textvariable=self.path_var,
            font=("Segoe UI", 10)
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        button_frame = ttk.Frame(path_input_frame)
        button_frame.pack(side=tk.RIGHT)

        self.btn_browse = ttk.Button(
            button_frame,
            image=self.fa_images["browse"],
            text=" Browse",
            command=self.browse_directory,
            style="Action.TButton",
            compound="left"
        )
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_generate = ttk.Button(
            button_frame,
            image=self.fa_images["generate"],
            text=" Generate",
            command=self.generate_tree,
            style="Primary.TButton",
            compound="left"
        )
        self.btn_generate.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_copy = ttk.Button(
            button_frame,
            image=self.fa_images["copy"],
            text=" Copy",
            command=self.copy_to_clipboard,
            style="Action.TButton",
            compound="left"
        )
        self.btn_copy.pack(side=tk.LEFT)

        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        pw = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(pw, style="Card.TFrame", padding=(15, 15))
        pw.add(left_panel, weight=1)

        tree_header = ttk.Frame(left_panel)
        tree_header.pack(fill=tk.X, pady=(0, 10))

        tree_label = ttk.Label(tree_header, text="Interactive Tree View", font=("Segoe UI", 11, "bold"))
        tree_label.pack(side=tk.LEFT)

        self.tree_stats = ttk.Label(tree_header, text="", font=("Segoe UI", 9), foreground="gray")
        self.tree_stats.pack(side=tk.RIGHT)

        tree_container = ttk.Frame(left_panel)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_container, show="tree", style="Custom.Treeview")
        self.tree.heading("#0", text="Directory Structure", anchor="w")
        self.tree.column("#0", anchor="w", minwidth=150)

        tree_v_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_v_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_v_scroll.grid(row=0, column=1, sticky="ns")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        right_panel = ttk.Frame(pw, style="Card.TFrame", padding=(15, 15))
        pw.add(right_panel, weight=1)

        output_header = ttk.Frame(right_panel)
        output_header.pack(fill=tk.X, pady=(0, 10))

        output_label = ttk.Label(output_header, text="Tree Text Output", font=("Segoe UI", 11, "bold"))
        output_label.pack(side=tk.LEFT)

        style_card = ttk.Frame(right_panel, style="Card.TFrame", padding=(10, 10))
        style_card.pack(fill=tk.X, pady=(0, 10))

        style_label = ttk.Label(style_card, text="Output Style:", font=("Segoe UI", 10, "bold"))
        style_label.pack(anchor="w", pady=(0, 5))

        style_buttons = ttk.Frame(style_card)
        style_buttons.pack(fill=tk.X)

        styles = [("Classic", "classic"), ("Modern", "modern"), ("Minimal", "minimal")]
        for txt, val in styles:
            rb = ttk.Radiobutton(style_buttons, text=txt, variable=self.tree_style, value=val, padding=(10, 5))
            rb.pack(side=tk.LEFT, padx=(0, 10))

        text_container = ttk.Frame(right_panel)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.tree_text = tk.Text(
            text_container,
            wrap=tk.NONE,
            font=("JetBrains Mono", 10),
            state=tk.DISABLED,
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#404040",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        text_v_scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.tree_text.yview)
        self.tree_text.configure(yscrollcommand=text_v_scroll.set)

        self.tree_text.grid(row=0, column=0, sticky="nsew")
        text_v_scroll.grid(row=0, column=1, sticky="ns")

        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        self.status_bar = ttk.Frame(main_container, style="Card.TFrame", padding=(10, 5))
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready to explore directories...",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.status_label.pack(side=tk.LEFT)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        vals = self.tree.item(item, "values")
        if not vals:
            return

        full_path_str = vals[0]
        path_obj = Path(full_path_str)

        if path_obj.exists():
            size_info = self.get_path_info(path_obj)
            if path_obj.is_file():
                text = f"{self.fa_images['lock']} Selected: {path_obj.name} {size_info}"
            else:
                text = f"Selected: {path_obj.name} {size_info}"
            self.status_label.config(text=text)
        else:
            self.status_label.config(text="Selected path no longer exists")

    def get_path_info(self, path_obj):
        try:
            if path_obj.is_file():
                size = path_obj.stat().st_size
                if size < 1024:
                    return f"({size} bytes)"
                elif size < 1024 * 1024:
                    return f"({size / 1024:.1f} KB)"
                else:
                    return f"({size / (1024 * 1024):.1f} MB)"
            else:
                count = len(list(path_obj.iterdir()))
                return f"({count} items)"
        except PermissionError:
            return "(access denied)"
        except Exception:
            return ""

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Explore")
        if directory:
            self.path_var.set(directory)
            self.status_label.config(text=f"Selected directory: {Path(directory).name}")

    def generate_tree(self):
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", "Please select a valid directory first")
            return

        self.current_path = path
        self.status_label.config(text="Scanning directory…")

        self.btn_browse.configure(state="disabled")
        self.btn_generate.configure(state="disabled")
        self.btn_copy.configure(state="disabled")
        self.path_entry.configure(state="disabled")

        threading.Thread(target=self._background_build_structure, args=(path,), daemon=True).start()

    def _background_build_structure(self, path):
        structure = self.build_tree_structure(Path(path))
        total_items = self.count_structure_items(structure)
        self.root.after(0, lambda: self._insert_tree_on_main(path, structure, total_items))

    def _insert_tree_on_main(self, path, structure, total_items):
        self.tree_structure = structure

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree_text.config(state=tk.NORMAL)
        self.tree_text.delete("1.0", tk.END)
        self.tree_text.config(state=tk.DISABLED)

        root_name = Path(path).name
        root_node = self.tree.insert(
            "", "end",
            text=f" {root_name}",
            image=self.fa_images["folder_open"],
            open=True,
            values=[path]
        )
        self.insert_from_structure(root_node, structure)

        self.tree_stats.config(text=f"{total_items} items")
        self.update_text_from_structure_async()

        self.status_label.config(text=f"✅ Tree generated – {total_items} items found")

        self.btn_browse.configure(state="normal")
        self.btn_generate.configure(state="normal")
        self.btn_copy.configure(state="normal")
        self.path_entry.configure(state="normal")

    def build_tree_structure(self, path_obj):
        structure = {}
        try:
            for entry in sorted(path_obj.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
                if entry.is_dir():
                    structure[entry.name] = self.build_tree_structure(entry)
                else:
                    structure[entry.name] = None
        except PermissionError:
            structure["Access Denied"] = None
        return structure

    def count_structure_items(self, structure):
        total = 0
        for name, subtree in structure.items():
            total += 1
            if isinstance(subtree, dict):
                total += self.count_structure_items(subtree)
        return total

    def insert_from_structure(self, parent, structure):
        for name, subtree in structure.items():
            display_text = f" {name}"
            if subtree is None:
                self.tree.insert(parent, "end", text=display_text, image=self.fa_images["file"], values=[""])
            else:
                node = self.tree.insert(parent, "end", text=display_text, image=self.fa_images["folder"], values=[""])
                self.insert_from_structure(node, subtree)

    def on_style_change(self, *_):
        if not self.tree_structure:
            return
        self.status_label.config(text="Re-rendering text output…")
        self.update_text_from_structure_async()

    def update_text_from_structure_async(self):
        threading.Thread(target=self._build_text_from_structure_worker, daemon=True).start()

    def _build_text_from_structure_worker(self):
        tree_str = self.create_tree_string_from_structure(self.tree_structure, self.tree_style.get())
        line_count = len(tree_str.split("\n"))
        self.root.after(0, lambda: self._insert_text_output(tree_str, line_count))

    def _insert_text_output(self, tree_str, line_count):
        self.tree_text.config(state=tk.NORMAL)
        self.tree_text.delete("1.0", tk.END)
        self.tree_text.insert(tk.END, tree_str)
        self.tree_text.config(state=tk.DISABLED)
        self.status_label.config(text=f"✅ Text output updated – {line_count} lines")

    def create_tree_string_from_structure(self, structure, style):
        lines = []

        def walk(subtree, prefix=""):
            items = list(subtree.items())
            for idx, (name, child) in enumerate(items):
                is_last = (idx == len(items) - 1)
                if style == "classic":
                    connector = "+-- "
                    next_prefix = prefix + ("   " if is_last else "|  ")
                elif style == "modern":
                    connector = "└─ " if is_last else "├─ "
                    next_prefix = prefix + ("   " if is_last else "│  ")
                else:
                    connector = "• "
                    next_prefix = prefix + "  "

                display_name = f"{name}/" if isinstance(child, dict) else name
                lines.append(f"{prefix}{connector}{display_name}")

                if isinstance(child, dict):
                    walk(child, next_prefix)

        lines.append(f"{Path(self.current_path).name}/")
        walk(structure, "")
        return "\n".join(lines)

    def copy_to_clipboard(self):
        content = self.tree_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Tree structure copied to clipboard!")
            self.status_label.config(text="📋 Tree copied to clipboard")
        else:
            messagebox.showwarning("Warning", "Nothing to copy. Generate a tree first.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("Threading: available")
    TreeViewerApp().run()
    print("Application exited")
