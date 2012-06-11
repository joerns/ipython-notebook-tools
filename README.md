IPython Notebook Tools
======================

Some tools for handling ipython notebooks. Includes tools for
converting to html and a wsgi server to host read-only
notebooks. Currently only in a very early, experimental state.

* **ipynb2html.py** converts .ipynb files to html suitable for
    deploying on a webserver.
* **ipnbshow.py** is a Qt application which simply renders a .ipynb in
    webkit component. Not really working because QWebView and
    MathJax.js are not playing nicely together. 
* **nbtools/ipynb_wsgi.py** is a simple WSGI server to host .ipynb
    files read-only.

