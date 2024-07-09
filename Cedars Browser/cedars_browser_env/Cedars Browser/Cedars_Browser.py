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

        self.browser.urlChanged.connect(self.update_url)
        self.urlChanged.connect(self.browser.setUrl)

    def custom_css_script(self):
        css_code = """
        ::-webkit-scrollbar {
            width: 17px;
            height: 30px;
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName('Cedars Browser')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
