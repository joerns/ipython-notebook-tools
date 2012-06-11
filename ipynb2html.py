#!/usr/bin/env python

from IPython.nbformat.v2.nbjson import JSONReader
import nbtools.renderer

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print "Usage: %s FILENAME" % sys.argv[0]
        sys.exit(-1)

    nbfile = sys.argv[1]

    nbreader = JSONReader()
    nb = nbreader.reads(open(nbfile).read())

    html_renderer = nbtools.renderer.HtmlRenderer()
    print html_renderer.render(nb)

