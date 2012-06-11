from IPython.nbformat.v2.nbjson import JSONReader

def parse_notebook(filename):
    nbreader = JSONReader()
    nb = nbreader.reads(open(filename).read())

    
