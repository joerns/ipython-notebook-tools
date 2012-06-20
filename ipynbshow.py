#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
from IPython.nbformat.v2.nbjson import JSONReader
import nbtools.renderer as renderer

STYLE = '''
<style>
.in_prompt_number { 
    color: darkGray;
    font-family: monospace;
}

.out_prompt_number {
    color: darkGray; 
    font-family: monospace;
}

.code { 
    font-family: monospace; 
}

.codecell { 
}

.output_stream { 
    font-family: monospace; 
}

.display_data {
}

.pyout { 
    font-family: Monospace;
}

.pyerr { 
    font-family: Monospace;
    color: red;
}

body {
font-family: Helvetica, Arial, sans-serif;
}
</style>
'''

class Form(QDialog):
    
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Notebook")
        self.webview = QWebView()

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

    html_renderer = renderer.HtmlRenderer(use_mathjax=False, additional_style=STYLE)
    html = html_renderer.render(nb)

    app = QApplication(sys.argv)
    form = Form()
    form.setHtml(html)
    form.show()
    sys.exit(app.exec_())



 
