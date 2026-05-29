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
    def __init__(self, on_login) -> None:
        super().__init__()
        self.on_login = on_login
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(password_echo_mode())
        self.remember = QCheckBox("Remember profile name")
        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setPlainText(
            "This app opens DAT inside an embedded browser. "
            "Sign in to DAT normally inside the browser tab. "
            "No shared cookies or external tokens are loaded."
        )
        self._build()
        self._load_profile()

    def _build(self) -> None:
        title = QLabel(APP_NAME)
        title.setObjectName("title")
        subtitle = QLabel("Authorized DAT workspace")
        subtitle.setObjectName("subtitle")

        form = QGridLayout()
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
        panel_layout.addWidget(title)
        panel_layout.addWidget(subtitle)
        panel_layout.addSpacing(18)
        panel_layout.addLayout(form)
        panel_layout.addSpacing(10)
        panel_layout.addWidget(login)
        panel_layout.addSpacing(12)
        panel_layout.addWidget(self.notes)

        wrapper = QVBoxLayout(self)
        wrapper.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
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
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

    def set_streams(self, username: str, config: AppConfig) -> None:
        self._clear()
        header_row = QHBoxLayout()
        title = QLabel(f"Streams for {username}")
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

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for index, stream in enumerate(config.streams):
            card = self._stream_card(stream)
            grid.addWidget(card, index // 2, index % 2)
        self.layout.addLayout(grid)
        self.layout.addStretch(1)

    def _stream_card(self, stream: StreamConfig) -> QGroupBox:
        box = QGroupBox(stream.label)
        box.setObjectName("streamCard")
        body = QVBoxLayout(box)
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
        self._build()

    def _build(self) -> None:
        back = QAction("Back", self)
        forward = QAction("Forward", self)
        reload_action = QAction("Reload", self)
        home = QAction("Home", self)
        new_tab = QAction("New Tab", self)
        speed = QAction("Speed Test", self)
        clear_data = QAction("Clear Browser Data", self)

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
        self.login_page = LoginPage(self.login)
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
        background: #f6f7fb;
        color: #17202a;
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 13px;
    }
    #title {
        font-size: 32px;
        font-weight: 700;
        color: #152238;
    }
    #subtitle {
        font-size: 15px;
        color: #506070;
    }
    #sectionTitle {
        font-size: 24px;
        font-weight: 700;
    }
    #hint {
        color: #5b677a;
    }
    #mono {
        font-family: Consolas, monospace;
        color: #32445a;
    }
    #loginPanel {
        background: #ffffff;
        border: 1px solid #dbe1ea;
        border-radius: 8px;
        min-width: 520px;
        max-width: 620px;
        padding: 18px;
    }
    QGroupBox#streamCard {
        background: #ffffff;
        border: 1px solid #dbe1ea;
        border-radius: 8px;
        padding: 18px;
        min-width: 360px;
        min-height: 150px;
        font-weight: 700;
    }
    QLineEdit, QTextEdit {
        background: #ffffff;
        border: 1px solid #c9d3df;
        border-radius: 6px;
        padding: 8px;
    }
    QPushButton {
        background: #e8edf5;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        color: #17202a;
        padding: 8px 12px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #dfe8f5;
    }
    QPushButton#primary {
        background: #2266cc;
        border-color: #1e5bb6;
        color: #ffffff;
    }
    QPushButton#primary:hover {
        background: #1f5fbf;
    }
    QToolBar#mainToolbar {
        background: #ffffff;
        border-bottom: 1px solid #dbe1ea;
        spacing: 6px;
        padding: 6px;
    }
    QTabWidget::pane {
        border: 0;
    }
    QTabBar::tab {
        background: #e8edf5;
        border: 1px solid #cbd5e1;
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
    return getattr(QLineEdit, "Password", QLineEdit.EchoMode.Password)


def message_box_yes():
    return getattr(QMessageBox, "Yes", QMessageBox.StandardButton.Yes)


def no_proxy_type():
    return getattr(QNetworkProxy, "NoProxy", QNetworkProxy.ProxyType.NoProxy)


def http_proxy_type():
    return getattr(QNetworkProxy, "HttpProxy", QNetworkProxy.ProxyType.HttpProxy)


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
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
