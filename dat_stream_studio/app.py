from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from PySide6.QtCore import QUrl, Qt
    from PySide6.QtGui import QAction, QCloseEvent, QFont, QIcon
    from PySide6.QtNetwork import QNetworkProxy
    from PySide6.QtWebEngineCore import QWebEngineProfile
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QStackedWidget,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    QT_BINDING = "PySide6"
except ImportError:
    try:
        from PyQt6.QtCore import QUrl, Qt
        from PyQt6.QtGui import QAction, QCloseEvent, QFont, QIcon
        from PyQt6.QtNetwork import QNetworkProxy
        from PyQt6.QtWebEngineCore import QWebEngineProfile
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtWidgets import (
            QApplication,
            QCheckBox,
            QFrame,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QStackedWidget,
            QStatusBar,
            QTabWidget,
            QTextEdit,
            QToolBar,
            QVBoxLayout,
            QWidget,
        )

        QT_BINDING = "PyQt6"
    except ImportError:
        try:
            from PyQt5.QtCore import QUrl, Qt
            from PyQt5.QtGui import QCloseEvent, QFont, QIcon
            from PyQt5.QtNetwork import QNetworkProxy
            from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
            from PyQt5.QtWidgets import (
                QAction,
                QApplication,
                QCheckBox,
                QFrame,
                QGridLayout,
                QGroupBox,
                QHBoxLayout,
                QLabel,
                QLineEdit,
                QMainWindow,
                QMessageBox,
                QPushButton,
                QStackedWidget,
                QStatusBar,
                QTabWidget,
                QTextEdit,
                QToolBar,
                QVBoxLayout,
                QWidget,
            )

            QT_BINDING = "PyQt5"
        except ImportError:
            from lite_app import main

            if __name__ == "__main__":
                raise SystemExit(main())
            raise RuntimeError("Qt bindings are not installed. Run lite_app.py instead.")


APP_NAME = "DAT Stream Studio"
APP_VERSION = "1.0.0"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def app_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent


def user_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    path = base / "DAT Stream Studio"
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class ProxyConfig:
    enabled: bool = False
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ProxyConfig":
        data = data or {}
        return cls(
            enabled=bool(data.get("enabled", False)),
            host=str(data.get("host", "")).strip(),
            port=int(data.get("port") or 0),
            username=str(data.get("username", "")),
            password=str(data.get("password", "")),
        )


@dataclass
class StreamConfig:
    id: str
    label: str
    url: str
    description: str = ""
    proxy: ProxyConfig | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StreamConfig":
        return cls(
            id=str(data.get("id") or data.get("label") or "stream").strip(),
            label=str(data.get("label") or "Stream").strip(),
            url=str(data.get("url") or "https://one.dat.com").strip(),
            description=str(data.get("description") or ""),
            proxy=ProxyConfig.from_dict(data.get("proxy")),
        )


@dataclass
class AppConfig:
    app_name: str
    version: str
    status_line: str
    streams: list[StreamConfig]

    @classmethod
    def load(cls) -> "AppConfig":
        root = app_root()
        local = root / "streams.local.json"
        source = local if local.exists() else root / "sample_streams.json"
        with source.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        streams = [StreamConfig.from_dict(item) for item in raw.get("streams", [])]
        if not streams:
            streams = [
                StreamConfig(
                    id="dat-one",
                    label="DAT One",
                    url="https://one.dat.com",
                    description="Open DAT One with normal login.",
                    proxy=ProxyConfig(),
                )
            ]
        return cls(
            app_name=str(raw.get("app_name") or APP_NAME),
            version=str(raw.get("version") or APP_VERSION),
            status_line=str(raw.get("status_line") or "Ready"),
            streams=streams,
        )


class LoginPage(QWidget):
    def __init__(self, on_login, config: AppConfig) -> None:
        super().__init__()
        self.on_login = on_login
        self.config = config
        self.username = QLineEdit()
        self.username.setPlaceholderText("dispatcher-01")
        self.password = QLineEdit()
        self.password.setPlaceholderText("workspace key")
        self.password.setEchoMode(password_echo_mode())
        self.remember = QCheckBox("Remember profile name")
        self._build()
        self._load_profile()

    def _build(self) -> None:
        title = QLabel(APP_NAME)
        title.setObjectName("title")
        subtitle = QLabel("Dispatch workspace")
        subtitle.setObjectName("subtitle")

        metric_row = QHBoxLayout()
        for label, value in [
            ("Streams", str(len(self.config.streams))),
            ("Profile", "Local"),
            ("Mode", QT_BINDING),
        ]:
            tile = QFrame()
            tile.setObjectName("metricTile")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(14, 12, 14, 12)
            metric = QLabel(value)
            metric.setObjectName("metricValue")
            caption = QLabel(label)
            caption.setObjectName("metricLabel")
            tile_layout.addWidget(metric)
            tile_layout.addWidget(caption)
            metric_row.addWidget(tile)

        form = QGridLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)
        form.addWidget(QLabel("Profile"), 0, 0)
        form.addWidget(self.username, 0, 1)
        form.addWidget(QLabel("Unlock key"), 1, 0)
        form.addWidget(self.password, 1, 1)
        form.addWidget(self.remember, 2, 1)

        login = QPushButton("Continue")
        login.setObjectName("primary")
        login.clicked.connect(self._submit)
        self.password.returnPressed.connect(self._submit)

        panel = QFrame()
        panel.setObjectName("loginPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 28, 28, 28)
        panel_layout.setSpacing(14)
        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        panel_layout.addSpacing(8)
        panel_layout.addLayout(metric_row)
        panel_layout.addSpacing(10)
        panel_layout.addLayout(form)
        panel_layout.addSpacing(8)
        panel_layout.addWidget(login)

        side = QFrame()
        side.setObjectName("sidePanel")
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(28, 28, 28, 28)
        side_layout.setSpacing(16)
        side_title = QLabel("Live Board")
        side_title.setObjectName("sideTitle")
        side_layout.addWidget(side_title)
        for text in [
            "DAT One",
            "DAT Power",
            "Speed Check",
            "Local Profile",
        ]:
            chip = QLabel(text)
            chip.setObjectName("statusChip")
            side_layout.addWidget(chip)
        side_layout.addStretch(1)
        footer = QLabel("v" + APP_VERSION)
        footer.setObjectName("sideFooter")
        side_layout.addWidget(footer)

        wrapper = QVBoxLayout(self)
        wrapper.setContentsMargins(40, 40, 40, 40)
        wrapper.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.setSpacing(18)
        row.addWidget(side)
        row.addWidget(panel)
        row.addStretch(1)
        wrapper.addLayout(row)
        wrapper.addStretch(1)

    def _load_profile(self) -> None:
        profile = user_data_dir() / "profile.json"
        if profile.exists():
            try:
                data = json.loads(profile.read_text(encoding="utf-8"))
                self.username.setText(data.get("username", ""))
                self.remember.setChecked(bool(data.get("remember", False)))
            except (OSError, json.JSONDecodeError):
                pass

    def _submit(self) -> None:
        username = self.username.text().strip()
        password = self.password.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Missing Information", "Enter a profile and unlock key.")
            return

        if self.remember.isChecked():
            target = user_data_dir() / "profile.json"
            target.write_text(
                json.dumps({"username": username, "remember": True}, indent=2),
                encoding="utf-8",
            )

        self.on_login(username)


class StreamPage(QWidget):
    def __init__(self, on_open, on_logout) -> None:
        super().__init__()
        self.on_open = on_open
        self.on_logout = on_logout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 28, 32, 28)
        self.layout.setSpacing(18)

    def set_streams(self, username: str, config: AppConfig) -> None:
        self._clear()
        header_row = QHBoxLayout()
        title = QLabel(f"Workspace: {username}")
        title.setObjectName("sectionTitle")
        logout = QPushButton("Switch Profile")
        logout.clicked.connect(self.on_logout)
        header_row.addWidget(title)
        header_row.addStretch(1)
        header_row.addWidget(logout)
        self.layout.addLayout(header_row)

        hint = QLabel(config.status_line)
        hint.setObjectName("hint")
        self.layout.addWidget(hint)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(12)
        for title_text, detail in [
            ("Session", "Persistent local browser"),
            ("Network", "Direct or configured proxy"),
            ("Browser", QT_BINDING + " WebEngine"),
        ]:
            tile = QFrame()
            tile.setObjectName("summaryTile")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(16, 12, 16, 12)
            headline = QLabel(title_text)
            headline.setObjectName("summaryHeadline")
            sub = QLabel(detail)
            sub.setObjectName("summarySub")
            tile_layout.addWidget(headline)
            tile_layout.addWidget(sub)
            quick_row.addWidget(tile)
        self.layout.addLayout(quick_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for index, stream in enumerate(config.streams):
            card = self._stream_card(stream)
            grid.addWidget(card, index // 2, index % 2)
        self.layout.addLayout(grid)
        self.layout.addStretch(1)

    def _stream_card(self, stream: StreamConfig) -> QGroupBox:
        box = QGroupBox("")
        box.setObjectName("streamCard")
        body = QVBoxLayout(box)
        body.setContentsMargins(18, 18, 18, 18)
        body.setSpacing(10)
        title = QLabel(stream.label)
        title.setObjectName("cardTitle")
        desc = QLabel(stream.description or stream.url)
        desc.setWordWrap(True)
        desc.setObjectName("hint")
        url = QLabel(stream.url)
        url.setObjectName("mono")
        proxy_label = QLabel(self._proxy_summary(stream.proxy))
        proxy_label.setObjectName("hint")
        open_button = QPushButton("Open")
        open_button.setObjectName("primary")
        open_button.clicked.connect(lambda: self.on_open(stream))
        body.addWidget(title)
        body.addWidget(desc)
        body.addWidget(url)
        body.addWidget(proxy_label)
        body.addStretch(1)
        body.addWidget(open_button)
        return box

    @staticmethod
    def _proxy_summary(proxy: ProxyConfig | None) -> str:
        if not proxy or not proxy.enabled:
            return "Connection: direct"
        auth = "with auth" if proxy.username else "without auth"
        return f"Connection: {proxy.host}:{proxy.port} {auth}"

    def _clear(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.deleteLater()
            elif child_layout:
                while child_layout.count():
                    child = child_layout.takeAt(0).widget()
                    if child:
                        child.deleteLater()


class BrowserWorkspace(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.toolbar = QToolBar("Navigation")
        self.toolbar.setObjectName("mainToolbar")
        self.status = QLabel("No stream open")
        self.status.setObjectName("browserStatus")
        self._build()

    def _build(self) -> None:
        back = QAction("Back", self)
        forward = QAction("Forward", self)
        reload_action = QAction("Reload", self)
        home = QAction("Home", self)
        new_tab = QAction("New Tab", self)
        speed = QAction("Speed Test", self)
        clear_data = QAction("Clear Data", self)

        back.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        forward.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        reload_action.triggered.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        home.triggered.connect(self.reload_current_stream)
        new_tab.triggered.connect(self.open_current_stream)
        speed.triggered.connect(lambda: self.open_url("https://fast.com/", "Speed Test"))
        clear_data.triggered.connect(self.clear_browser_data)

        for action in [back, forward, reload_action, home, new_tab, speed, clear_data]:
            self.toolbar.addAction(action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.status)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tabs)

    def current_browser(self) -> QWebEngineView | None:
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, QWebEngineView) else None

    def open_stream(self, stream: StreamConfig) -> None:
        self.main_window.current_stream = stream
        self._apply_proxy(stream.proxy)
        self.open_url(stream.url, stream.label)

    def open_current_stream(self) -> None:
        if not self.main_window.current_stream:
            QMessageBox.information(self, "No Stream", "Choose a stream first.")
            return
        self.open_stream(self.main_window.current_stream)

    def reload_current_stream(self) -> None:
        if not self.main_window.current_stream:
            return
        browser = self.current_browser()
        if browser:
            browser.load(QUrl(self.main_window.current_stream.url))

    def open_url(self, url: str, label: str) -> None:
        browser = QWebEngineView()
        profile = browser.page().profile()
        profile.setHttpUserAgent(DEFAULT_USER_AGENT)
        browser.loadProgress.connect(self._on_progress)
        browser.loadFinished.connect(lambda ok, b=browser: self._on_finished(ok, b))
        browser.titleChanged.connect(lambda title, b=browser: self._rename_tab(b, title or label))
        browser.urlChanged.connect(lambda qurl: self.status.setText(qurl.toString()))
        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)
        browser.load(QUrl(url))

    def close_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget:
            widget.deleteLater()
        if self.tabs.count() == 0:
            self.main_window.show_streams()

    def clear_browser_data(self) -> None:
        answer = QMessageBox.question(
            self,
            "Clear Browser Data",
            "Clear cookies and cache for the embedded browser profile?",
        )
        if answer != message_box_yes():
            return
        profile = QWebEngineProfile.defaultProfile()
        profile.cookieStore().deleteAllCookies()
        profile.clearHttpCache()
        self.status.setText("Browser cookies and cache cleared")

    def _apply_proxy(self, proxy: ProxyConfig | None) -> None:
        if not proxy or not proxy.enabled:
            QNetworkProxy.setApplicationProxy(QNetworkProxy(no_proxy_type()))
            self.status.setText("Connection: direct")
            return

        qproxy = QNetworkProxy()
        qproxy.setType(http_proxy_type())
        qproxy.setHostName(proxy.host)
        qproxy.setPort(proxy.port)
        if proxy.username:
            qproxy.setUser(proxy.username)
        if proxy.password:
            qproxy.setPassword(proxy.password)
        QNetworkProxy.setApplicationProxy(qproxy)
        self.status.setText(f"Connection: {proxy.host}:{proxy.port}")

    def _on_progress(self, progress: int) -> None:
        self.status.setText(f"Loading {progress}%")

    def _on_finished(self, ok: bool, browser: QWebEngineView) -> None:
        if ok:
            self.status.setText(browser.url().toString())
            return
        self.status.setText("Page failed to load")

    def _rename_tab(self, browser: QWebEngineView, title: str) -> None:
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, title[:32])


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config = AppConfig.load()
        self.username = ""
        self.current_stream: StreamConfig | None = None
        self.stack = QStackedWidget()
        self.login_page = LoginPage(self.login, self.config)
        self.stream_page = StreamPage(self.open_stream, self.logout)
        self.workspace = BrowserWorkspace(self)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.stream_page)
        self.stack.addWidget(self.workspace)
        self.setCentralWidget(self.stack)
        self.setStatusBar(QStatusBar())
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1280, 820)
        self._prepare_profile()

    def _prepare_profile(self) -> None:
        profile_dir = user_data_dir() / "web_profile"
        cache_dir = user_data_dir() / "web_cache"
        profile_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentStoragePath(str(profile_dir))
        profile.setCachePath(str(cache_dir))
        profile.setHttpUserAgent(DEFAULT_USER_AGENT)

    def login(self, username: str) -> None:
        self.username = username
        self.show_streams()

    def logout(self) -> None:
        self.username = ""
        self.current_stream = None
        self.stack.setCurrentWidget(self.login_page)

    def show_streams(self) -> None:
        self.stream_page.set_streams(self.username or "local profile", self.config)
        self.stack.setCurrentWidget(self.stream_page)

    def open_stream(self, stream: StreamConfig) -> None:
        self.stack.setCurrentWidget(self.workspace)
        self.workspace.open_stream(stream)

    def closeEvent(self, event: QCloseEvent) -> None:
        QNetworkProxy.setApplicationProxy(QNetworkProxy(no_proxy_type()))
        event.accept()


def load_stylesheet() -> str:
    return """
    QWidget {
        background: #f4f6f8;
        color: #17202a;
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 13px;
    }
    #title {
        font-size: 34px;
        font-weight: 700;
        color: #101828;
    }
    #subtitle {
        font-size: 15px;
        color: #667085;
    }
    #sectionTitle {
        font-size: 25px;
        font-weight: 700;
        color: #101828;
    }
    #hint {
        color: #667085;
    }
    #mono {
        font-family: Consolas, monospace;
        color: #344054;
        background: #f2f4f7;
        border-radius: 6px;
        padding: 7px;
    }
    #loginPanel {
        background: #ffffff;
        border: 1px solid #d0d5dd;
        border-radius: 8px;
        min-width: 520px;
        max-width: 620px;
    }
    #sidePanel {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        min-width: 260px;
        max-width: 300px;
    }
    #sideTitle {
        background: transparent;
        color: #ffffff;
        font-size: 24px;
        font-weight: 700;
    }
    #sideFooter {
        background: transparent;
        color: #9ca3af;
        font-weight: 700;
    }
    #statusChip {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 6px;
        color: #e5e7eb;
        padding: 10px 12px;
        font-weight: 700;
    }
    #metricTile, #summaryTile {
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        border-radius: 8px;
    }
    #metricValue {
        background: transparent;
        color: #175cd3;
        font-size: 20px;
        font-weight: 800;
    }
    #metricLabel {
        background: transparent;
        color: #667085;
        font-size: 12px;
        font-weight: 700;
    }
    #summaryHeadline {
        background: transparent;
        color: #101828;
        font-size: 15px;
        font-weight: 800;
    }
    #summarySub {
        background: transparent;
        color: #667085;
        font-size: 12px;
    }
    #cardTitle {
        background: transparent;
        color: #101828;
        font-size: 20px;
        font-weight: 800;
    }
    QGroupBox#streamCard {
        background: #ffffff;
        border: 1px solid #d0d5dd;
        border-radius: 8px;
        min-width: 360px;
        min-height: 180px;
    }
    QLineEdit, QTextEdit {
        background: #ffffff;
        border: 1px solid #d0d5dd;
        border-radius: 6px;
        padding: 10px;
        selection-background-color: #175cd3;
    }
    QLineEdit:focus {
        border: 1px solid #175cd3;
    }
    QPushButton {
        background: #ffffff;
        border: 1px solid #d0d5dd;
        border-radius: 6px;
        color: #344054;
        padding: 9px 14px;
        font-weight: 700;
    }
    QPushButton:hover {
        background: #f9fafb;
        border-color: #98a2b3;
    }
    QPushButton#primary {
        background: #175cd3;
        border-color: #175cd3;
        color: #ffffff;
    }
    QPushButton#primary:hover {
        background: #1849a9;
        border-color: #1849a9;
    }
    QToolBar#mainToolbar {
        background: #ffffff;
        border-bottom: 1px solid #d0d5dd;
        spacing: 6px;
        padding: 8px;
    }
    #browserStatus {
        background: #f2f4f7;
        color: #344054;
        border: 1px solid #e4e7ec;
        border-radius: 6px;
        padding: 7px 10px;
        font-weight: 700;
    }
    QTabWidget::pane {
        border: 0;
    }
    QTabBar::tab {
        background: #eaecf0;
        border: 1px solid #d0d5dd;
        border-bottom: 0;
        padding: 8px 14px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    QTabBar::tab:selected {
        background: #ffffff;
    }
    """


def password_echo_mode():
    if hasattr(QLineEdit, "Password"):
        return QLineEdit.Password
    return QLineEdit.EchoMode.Password


def message_box_yes():
    if hasattr(QMessageBox, "Yes"):
        return QMessageBox.Yes
    return QMessageBox.StandardButton.Yes


def no_proxy_type():
    if hasattr(QNetworkProxy, "NoProxy"):
        return QNetworkProxy.NoProxy
    return QNetworkProxy.ProxyType.NoProxy


def http_proxy_type():
    if hasattr(QNetworkProxy, "HttpProxy"):
        return QNetworkProxy.HttpProxy
    return QNetworkProxy.ProxyType.HttpProxy


def high_dpi_attribute(name: str):
    if hasattr(Qt, name):
        return getattr(Qt, name)
    application_attribute = getattr(Qt, "ApplicationAttribute", None)
    if application_attribute and hasattr(application_attribute, name):
        return getattr(application_attribute, name)
    return None


def main() -> int:
    for attribute_name in ("AA_EnableHighDpiScaling", "AA_UseHighDpiPixmaps"):
        attribute = high_dpi_attribute(attribute_name)
        if attribute is not None:
            QApplication.setAttribute(attribute)
    app = QApplication(sys.argv)
    app.setApplicationName(f"{APP_NAME} ({QT_BINDING})")
    app.setStyleSheet(load_stylesheet())
    window = MainWindow()
    window.show()
    if hasattr(app, "exec"):
        return app.exec()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
