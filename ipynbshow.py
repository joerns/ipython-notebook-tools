#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
from IPython.nbformat.v2.nbjson import JSONReader
import nbtools.renderer as renderer

class Form(QDialog):
    
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Notebook")
        self.webview = QWebView()
        self.webview.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        self.webview.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.webview.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.webview.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.webview.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        self.webview.settings().setAttribute(QWebSettings.LocalStorageEnabled, True)
        self.webview.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.webview.settings().setAttribute(QWebSettings.JavaEnabled, True)
        self.webview.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)

    def setHtml(self, html):
        self.webview.setHtml(html)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {0} FILENAME".format(sys.argv[0]))
        sys.exit(-1)

    nbfile = sys.argv[1]

    nbreader = JSONReader()
    nb = nbreader.reads(open(nbfile).read())

    html_renderer = renderer.HtmlRenderer()
    html = html_renderer.render(nb)

    app = QApplication(sys.argv)
    form = Form()
    form.setHtml(html)
    form.show()
    sys.exit(app.exec_())



 
