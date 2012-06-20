# coding: utf-8

import markdown
import base64
import cgi
import re

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class IPyNotebookRenderer:
    def __init__(self):
        pass

    def render(self, notebook):
        return str(notebook)


class HtmlRenderer:
    def __init__(self, use_mathjax=True, pygments_style="friendly", additional_style=None):
        self.html_formatter = HtmlFormatter(style=pygments_style)
        self.use_mathjax = use_mathjax

        if use_mathjax:
            self.MATHJAX = '''
<script type="text/x-mathjax-config">
  MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['$$','$$']]}});
</script>
<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML" charset="utf-8"></script>
'''
        else:
            self.MATHJAX = ''

        if additional_style:
            self.additional_style = additional_style
        else:
            self.additional_style = '''
<link rel="stylesheet" type="text/css" href="style.css" />
<link href='http://fonts.googleapis.com/css?family=PT+Serif' rel='stylesheet' type='text/css' />
'''
            

        self.PAGE_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/> 

<title>__TITLE__</title>

__MATHJAX__

__STYLE__

<style>

.in_prompt_number { 
    width: 11ex; 
    float: left;
}

.out_prompt_number { 
    width: 11ex; 
    float: left;
}

.code { 
    font-family: monospace; 
    margin-left: 13ex;
}

.codecell { 
}

.output_stream { 
    font-family: monospace; 
    margin-left: 13ex;
}

.display_data {
    margin-left: 13ex;
    display: block;
}

.pyout { 
    font-family: Monospace;
    margin-left: 13ex;
}

.pyerr { 
    font-family: Monospace;
    margin-left: 13ex;
    color: red;
}

__HIGHLIGHTCODE__

</style>

</head>
<body>
__CONTENTS__
</body>
</html>
'''
        self.PAGE_HTML = self.PAGE_HTML.replace("__HIGHLIGHTCODE__", self.html_formatter.get_style_defs('.highlight'))
        self.PAGE_HTML = self.PAGE_HTML.replace("__MATHJAX__", self.MATHJAX)
        self.PAGE_HTML = self.PAGE_HTML.replace("__STYLE__", self.additional_style)

        self.CODE_HTML = '''<div class="codecell">
<div class="in_prompt_number">IN [__PROMPT_NUMBER__]:</div>
<div class="code"><pre>__CODE__</pre></div>
<div class="outputs">__OUTPUT__</div>
</div>'''
        



    def render(self, notebook):
        return self._render_html(notebook).encode("utf-8")


    def _render_html(self, notebook):
        content_html = self._render_worksheets(notebook['worksheets'])
        html = self.PAGE_HTML
        html = html.replace("__TITLE__", notebook['metadata']['name'])
        html = html.replace("__CONTENTS__", content_html)
        return html
        
    def _render_worksheets(self, worksheets):
        w = [self._render_worksheet(i) for i in worksheets]
        return '\n'.join(w)

    def _render_worksheet(self, worksheet):
        return self._render_cells(worksheet['cells'])

    def _render_cells(self, cells):
        c = [self._render_cell(i) for i in cells]
        return '\n'.join(c)

    def _render_cell(self, cell):
        if cell['cell_type'] == 'markdown':
            cell_html = self._render_markdown_cell(cell)  
        elif cell['cell_type'] == 'code':
            cell_html =  self._render_code_cell(cell)
        else:
            cell_html = "Error: Unknown cell content"
            
        return '<div class="cell">' + cell_html + "</div>\n"

    def _render_markdown_cell(self, cell):
        return '<div id="markdowncell">'+markdown.markdown(cell['source'])+'</div>\n'

    def _render_code_cell(self, cell):
        cell_html = self.CODE_HTML
        cell_html = cell_html.replace('__CODE__', highlight(cell['input'],
                                                            PythonLexer(),
                                                            self.html_formatter))
        cell_html = cell_html.replace('__PROMPT_NUMBER__', str(cell.get('prompt_number', -1)))
        if cell['collapsed']:
            rendered_output = ""
        else:
            rendered_output = self._render_cell_outputs(cell)
            rendered_output = '<div class="out_prompt_number">OUT[%d]:</div>'%cell['prompt_number'] + rendered_output
        cell_html = cell_html.replace('__OUTPUT__', rendered_output)
        return cell_html


    def _render_cell_outputs(self, cell):
        o = ['<div id="celloutput">' + self._render_cell_output(i, cell) + '</div>\n' for i in cell['outputs']]
        return '\n'.join(o)

    def _render_cell_output(self, output, cell):
        if cell['collapsed']:
            return ''

        if output['output_type'] == 'stream':
            return self._render_cell_streamoutput(output)
        elif output['output_type'] == 'pyout':
            return self._render_cell_pyout(output)
        elif output['output_type'] == 'pyerr':
            return self._render_cell_pyerr(output)
        elif output['output_type'] == 'display_data':
            return self._render_cell_displaydata(output, cell)
        else:
            return "Error: Unknown cell output type\n"

    def _render_cell_streamoutput(self, output):
        return '<div class="output_stream">%s</div>\n' % cgi.escape(output['text']).replace('\n', '<br/>\n')

    def _render_cell_pyout(self, output):
        return '<div class="pyout">%s</div>\n' % cgi.escape(output['text'])

    def _render_cell_pyerr(self, output):
        s = ""
        for traceback in output['traceback']:
            temp = re.sub('\\[.*?m', '', traceback)
            s += '<div class="pyerr">%s</div>\n' % cgi.escape(temp).replace('\n', '<br/>\n')    
        return s

    def _render_cell_displaydata(self, output, cell):
        return '<div class="display_data"><img src="data:image/png;base64,%s"/></div>'%output['png']

