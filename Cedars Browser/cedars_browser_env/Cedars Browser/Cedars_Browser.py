import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import *


class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()


class MainWindow(QMainWindow):
    urlChanged = pyqtSignal(QUrl)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_icon = QIcon(os.path.join(current_dir, 'icons', 'app_icon.png'))
        self.setWindowIcon(app_icon)

        # Inject custom CSS for scrollbars
        self.browser.page().profile().scripts().insert(self.custom_css_script())

        # navbar
        navbar = QToolBar()
        navbar.setMovable(False)
        self.addToolBar(navbar)

        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        back_btn = QToolButton(self)
        back_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'back.png')))
        back_btn.clicked.connect(self.browser.back)
        back_btn.setCursor(Qt.PointingHandCursor)
        navbar.addWidget(back_btn)

        forward_btn = QToolButton(self)
        forward_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'forward.png')))
        forward_btn.clicked.connect(self.browser.forward)
        forward_btn.setCursor(Qt.PointingHandCursor)
        navbar.addWidget(forward_btn)

        reload_btn = QToolButton(self)
        reload_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'reload.png')))
        reload_btn.clicked.connect(self.browser.reload)
        reload_btn.setCursor(Qt.PointingHandCursor)
        navbar.addWidget(reload_btn)

        home_btn = QToolButton(self)
        home_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'home.png')))
        home_btn.clicked.connect(self.navigate_home)
        home_btn.setCursor(Qt.PointingHandCursor)
        navbar.addWidget(home_btn)

        self.url_bar = ClickableLineEdit()
        self.url_bar.setMinimumHeight(40)
        self.url_bar.setStyleSheet("font-size: 22px;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.clicked.connect(self.url_bar.selectAll)
        navbar.addWidget(self.url_bar)

        # SSL lock icon
        self.ssl_icon = QLabel()
        self.ssl_icon.setPixmap(QIcon(os.path.join(current_dir, 'icons', 'ssl.png')).pixmap(20, 20))
        navbar.addWidget(self.ssl_icon)
        self.ssl_icon.setVisible(False)

        # Add zoom out button
        zoom_out_btn = QToolButton(self)
        zoom_out_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'zoom_out.png')))
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setCursor(Qt.PointingHandCursor)
        navbar.addWidget(zoom_out_btn)

        # Add zoom in button
        zoom_in_btn = QToolButton(self)
        zoom_in_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'zoom_in.png')))
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setCursor(Qt.PointingHandCursor)
        navbar.addWidget(zoom_in_btn)

        self.browser.urlChanged.connect(self.update_url)
        self.urlChanged.connect(self.browser.setUrl)
        
        # Add options menu button
        options_btn = QToolButton(self)
        options_btn.setIcon(QIcon(os.path.join(current_dir, 'icons', 'options.png')))
        options_btn.setPopupMode(QToolButton.InstantPopup)
        options_btn.setCursor(Qt.PointingHandCursor)
        options_btn.setStyleSheet("QToolButton::menu-indicator { image: none; }")  # Remove dropdown indicator
        navbar.addWidget(options_btn)

        # Create options menu
        options_menu = QMenu(self)
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.open_settings)
        options_menu.addAction(settings_action)
        history_action = QAction('History', self)
        history_action.triggered.connect(self.open_history)
        options_menu.addAction(history_action)

        options_btn.setMenu(options_menu)

    def custom_css_script(self):
        css_code = """
        ::-webkit-scrollbar {
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 7px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        """
        js_code = f"""
        var style = document.createElement('style');
        style.type = 'text/css';
        style.appendChild(document.createTextNode(`{css_code}`));
        document.head.appendChild(style);
        """
        script = QWebEngineScript()
        script.setSourceCode(js_code)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(True)
        return script

    @pyqtSlot()
    def navigate_home(self):
        self.browser.setUrl(QUrl('http://google.com'))

    @pyqtSlot()
    def navigate_to_url(self):
        input_text = self.url_bar.text().strip()
        if input_text and not input_text.startswith('http://') and not input_text.startswith('https://'):
            # If not a complete URL, construct Google search URL
            search_url = f"https://www.google.com/search?q={input_text}"
            self.browser.setUrl(QUrl(search_url))
        else:
            # If it's a complete URL, load it directly  
            self.urlChanged.emit(QUrl(input_text))

    @pyqtSlot(QUrl)
    def update_url(self, q):
        self.url_bar.setText(q.toString())
        self.update_ssl_icon(q)

    def update_ssl_icon(self, url):
        if url.scheme() == 'https':
            self.ssl_icon.setVisible(True)
        else:
            self.ssl_icon.setVisible(False)

    @pyqtSlot()
    def zoom_in(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1)

    @pyqtSlot()
    def zoom_out(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() - 0.1)

    @pyqtSlot()
    def open_settings(self):
        # Placeholder method for opening settings
        print("Opening Settings")

    @pyqtSlot()
    def open_history(self):
        # Placeholder method for opening history
        print("Opening History")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName('Cedars Browser')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
