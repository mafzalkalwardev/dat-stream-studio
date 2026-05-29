from __future__ import annotations

import json
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk


APP_NAME = "DAT Stream Studio"
APP_VERSION = "1.0.0"


def load_config() -> dict:
    root = Path(__file__).resolve().parent
    local = root / "streams.local.json"
    source = local if local.exists() else root / "sample_streams.json"
    with source.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class DatStreamLite(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.config_data = load_config()
        self.username = tk.StringVar()
        self.unlock_key = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1120x720")
        self.minsize(920, 620)
        self.configure(bg="#f6f7fb")
        self._configure_style()
        self._build_shell()
        self._show_login()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f6f7fb")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background="#f6f7fb", foreground="#17202a", font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background="#ffffff", foreground="#17202a", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#ffffff", foreground="#152238", font=("Segoe UI", 26, "bold"))
        style.configure("Section.TLabel", background="#f6f7fb", foreground="#152238", font=("Segoe UI", 20, "bold"))
        style.configure("Hint.TLabel", background="#ffffff", foreground="#5b677a", font=("Segoe UI", 10))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        style.configure("TEntry", padding=8)

    def _build_shell(self) -> None:
        self.container = ttk.Frame(self, padding=24)
        self.container.pack(fill="both", expand=True)
        footer = ttk.Frame(self, padding=(18, 8))
        footer.pack(fill="x", side="bottom")
        ttk.Label(footer, textvariable=self.status).pack(side="left")
        ttk.Label(footer, text="Clean build: no shared cookies, no session import.").pack(side="right")

    def _clear(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()

    def _panel(self, parent: tk.Widget) -> ttk.Frame:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=24)
        panel.configure(borderwidth=1)
        return panel

    def _show_login(self) -> None:
        self._clear()
        outer = ttk.Frame(self.container)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(2, weight=1)
        outer.rowconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        panel = self._panel(outer)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(1, weight=1)

        ttk.Label(panel, text=APP_NAME, style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(panel, text="Authorized DAT workspace", style="Hint.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 20)
        )
        ttk.Label(panel, text="Profile", style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=8)
        ttk.Entry(panel, textvariable=self.username, width=38).grid(row=2, column=1, sticky="ew", pady=8)
        ttk.Label(panel, text="Unlock key", style="Panel.TLabel").grid(row=3, column=0, sticky="w", pady=8)
        ttk.Entry(panel, textvariable=self.unlock_key, show="*", width=38).grid(row=3, column=1, sticky="ew", pady=8)
        ttk.Button(panel, text="Continue", style="Primary.TButton", command=self._login).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(18, 12)
        )
        ttk.Label(
            panel,
            text="This runnable fallback opens DAT in your system browser. Install PySide6 to use the embedded-browser version.",
            style="Hint.TLabel",
            wraplength=520,
        ).grid(row=5, column=0, columnspan=2, sticky="w")

    def _login(self) -> None:
        if not self.username.get().strip() or not self.unlock_key.get().strip():
            messagebox.showwarning("Missing Information", "Enter a profile and unlock key.")
            return
        self.status.set(f"Profile active: {self.username.get().strip()}")
        self._show_streams()

    def _show_streams(self) -> None:
        self._clear()
        header = ttk.Frame(self.container)
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text=f"Streams for {self.username.get().strip()}", style="Section.TLabel").pack(side="left")
        ttk.Button(header, text="Switch Profile", command=self._show_login).pack(side="right")

        grid = ttk.Frame(self.container)
        grid.pack(fill="both", expand=True)
        streams = self.config_data.get("streams", [])
        for index, stream in enumerate(streams):
            self._stream_card(grid, stream).grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=8,
                pady=8,
            )
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        actions = ttk.Frame(self.container)
        actions.pack(fill="x", pady=(18, 0))
        ttk.Button(actions, text="Open DAT One", command=lambda: self._open("https://one.dat.com", "DAT One")).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions, text="Open DAT Power", command=lambda: self._open("https://power.dat.com", "DAT Power")).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions, text="Speed Test", command=lambda: self._open("https://fast.com/", "Speed Test")).pack(
            side="left"
        )

    def _stream_card(self, parent: tk.Widget, stream: dict) -> ttk.Frame:
        card = self._panel(parent)
        card.columnconfigure(0, weight=1)
        label = stream.get("label", "Stream")
        url = stream.get("url", "https://one.dat.com")
        description = stream.get("description", url)
        proxy = stream.get("proxy") or {}
        proxy_line = "Connection: direct"
        if proxy.get("enabled"):
            proxy_line = f"Connection: {proxy.get('host')}:{proxy.get('port')}"

        ttk.Label(card, text=label, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(card, text=description, style="Hint.TLabel", wraplength=420).grid(
            row=1, column=0, sticky="w", pady=(8, 4)
        )
        ttk.Label(card, text=url, style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(card, text=proxy_line, style="Hint.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 12))
        ttk.Button(card, text="Open", style="Primary.TButton", command=lambda: self._open(url, label)).grid(
            row=4, column=0, sticky="ew"
        )
        return card

    def _open(self, url: str, label: str) -> None:
        webbrowser.open_new_tab(url)
        self.status.set(f"Opened {label}: {url}")


def main() -> int:
    app = DatStreamLite()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
