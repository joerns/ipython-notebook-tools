#!/usr/bin/env python
# coding: utf-8

import os
import os.path
import urlparse

from IPython.nbformat.v2.nbjson import JSONReader

import renderer

class NotebookWSGI:
    def __init__(self, notebook_dir, enable_index, style=None):
        # config options
        self.notebook_dir = os.path.abspath(notebook_dir)
        self.enable_index = enable_index

        # constants
        self.RENDERERS = { 'html': renderer.HtmlRenderer(additional_style=style),
                           'ipynb': renderer.IPyNotebookRenderer() }
        self.DEFAULT_OUTPUT_FORMAT = 'html'
        self.CONTENT_TYPE = { 'html': 'text/html',
                              'ipynb': 'text/plain'
                              }
        
        self.nbreader = JSONReader()

    def __call__(self, environment, start_response):
        path_info = environment.get('PATH_INFO', '')
        query_str = environment.get('QUERY_STRING', '')

        if path_info.startswith('/'):
            path_info = path_info[1:]
        query = urlparse.parse_qs(query_str)

        resource = os.path.abspath(os.path.join(self.notebook_dir, path_info))

        try:
            if os.path.commonprefix([self.notebook_dir, resource]) != self.notebook_dir:
                return self._serve_error('Error 403: You do not have permission to access this resource',
                                         '403 Forbidden', start_response)
            elif not os.path.exists(resource):
                return self._serve_error('Error 404: The resource was not found',
                                         '404 Not Found', start_response)
            elif not self._check_query(query):
                return self._serve_error('Error 400: Bad request',
                                         '400 Bad Request', start_response)
            elif os.path.isdir(resource) and self.enable_index:
                return self._serve_index(path_info, resource, start_response)
            else:
                return self._serve_request(resource, start_response, query)
        except Exception as e:
            print e
            return self._serve_error('Error 500: Internal Server Error',
                                     '500 Internal Server Error', start_response)

    def _serve_request(self, resource, start_response, query):
        output_format = query.get('format', [self.DEFAULT_OUTPUT_FORMAT])[0]
        renderer = self.RENDERERS[output_format]

        nb = self.nbreader.reads(open(resource).read())
        
        status = "200 OK"        
        response = renderer.render(nb)
        
        headers = [("Content-Type", self.CONTENT_TYPE[output_format]),
                   ("Content-Length", str(len(response)))]
        
        start_response(status, headers)
        return [response]
        
    def _serve_index(self, path_info, resource, start_response):
        contents = os.listdir(resource)
        directories = filter(lambda x: os.path.isdir(os.path.join(resource, x)), contents)
        files = filter(lambda x: os.path.isfile(os.path.join(resource, x)) and x.endswith('.ipynb'), contents)
        
        contents = ""
        if not os.path.samefile(resource, self.notebook_dir):
            contents += '<li><a href="..">..</a></li>\n'
        for filename in directories:
            contents += '<li><a href="{path_info}/{filename}">{filename}/</a></li>\n'.format(path_info=path_info, 
                                                                                            filename=filename)
        for filename in files:
            contents += '<li><a href="{path_info}/{filename}">{filename}</a></li>\n'.format(path_info=path_info,
                                                                                            filename=filename)

        status = "200 OK"        
        response = """<!DOCTYPE html>
<html>
<head>
<title>Index of '{path_info}'</title>
<link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
<h1>Index of '{path_info}'</h1>
<ul>     
{contents}
</ul>
</body>
</html>
""".format(path_info=path_info, contents=contents)
        
        headers = [("Content-Type", "text/html"),
                   ("Content-Length", str(len(response)))]
        
        start_response(status, headers)
        return [response]

    def _serve_error(self, message, status, start_response):
        headers = [("Content-Type", "text/plain"),
                   ("Content-Length", str(len(message)))]

        start_response(status, headers)
        return [message]
        
    def _check_query(self, query):
        output_format = query.get('format', [self.DEFAULT_OUTPUT_FORMAT])[0]
        if output_format not in self.RENDERERS.keys():
            return False

        return True



if __name__ == '__main__':
    from wsgiref.simple_server import make_server   

    import sys
    if len(sys.argv) == 2:
        wd = sys.argv[1]
    else:
        wd = os.getcwd()

    try:
        style = "<style>\n" + open(os.path.join(wd, "style.css")).read() + "\n</style>\n"
    except:
        style = None

    notebook_wsgi = NotebookWSGI(notebook_dir=wd, enable_index=True, style=style)

    httpd = make_server('localhost', 8080, notebook_wsgi)
    httpd.serve_forever()
        
    
