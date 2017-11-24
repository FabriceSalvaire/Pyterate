####################################################################################################

import base64

import nbformat
from nbformat.v4 import (
    new_notebook,
    new_code_cell, new_markdown_cell, new_raw_cell,
    new_output, output_from_msg
)

#  nbformat.write(nb, fp, version=nbformat.NO_CONVERT, **kwargs)
# nbformat.v4.new_notebook(**kwargs)
# nbformat.v4.new_code_cell(source='', **kwargs)
# nbformat.v4.new_markdown_cell(source='', **kwargs)
# nbformat.v4.new_raw_cell(source='', **kwargs)
# nbformat.v4.new_output(output_type, data=None, **kwargs)
# nbformat.v4.output_from_msg(msg)

####################################################################################################

with open('Untitled.ipynb') as fh:
    notebook = nbformat.read(fh, nbformat.NO_CONVERT)
print(type(notebook)) # <class 'nbformat.notebooknode.NotebookNode'>
print(type(notebook.cells)) # list

with open('untitled.png', 'wb') as fh:
    image_base64 = notebook.cells[2].outputs[0].data['image/png']
    fh.write(base64.b64decode(image_base64))

####################################################################################################

notebook = new_notebook()
print(type(notebook))

# nb.metadata.authors = [
#     {
#         'name': 'Fernando Perez',
#     },
#     {
#         'name': 'Brian Granger',
#     },
# ]

# Cell metadata
#
# Official Jupyter metadata, as used by Jupyter frontends should be placed in the metadata.jupyter namespace, for example metadata.jupyter.foo = “bar”.
#
# The following metadata keys are defined at the cell level:
# Key 	Value 	Interpretation
# collapsed 	bool 	Whether the cell’s output container should be collapsed
# autoscroll 	bool or ‘auto’ 	Whether the cell’s output is scrolled, unscrolled, or autoscrolled
# deletable 	bool 	If False, prevent deletion of the cell
# format 	‘mime/type’ 	The mime-type of a Raw NBConvert Cell
# name 	str 	A name for the cell. Should be unique across the notebook. Uniqueness must be verified outside of the json schema.
# tags 	list of str 	A list of string tags on the cell. Commas are not allowed in a tag
#
# The following metadata keys are defined at the cell level within the jupyter namespace
# Key 	Value 	Interpretation
# source_hidden 	bool 	Whether the cell’s source should be shown
# outputs_hidden 	bool 	Whether the cell’s outputs should be shown

notebook.metadata.update({
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {
        'codemirror_mode': {
            'name': 'ipython',
            'version': 3
        },
        'file_extension': '.py',
        'mimetype': 'text/x-python',
        'name': 'python',
        'nbconvert_exporter': 'python',
        'pygments_lexer': 'ipython3',
        'version': '3.6.3'
    }
})

####################################################################################################

# {
#   "cell_type" : "markdown",
#   "metadata" : {},
#   "source" : "[multi-line *markdown*]",
# }

# {
#   "cell_type" : "markdown",
#   "metadata" : {},
#   "source" : ["Here is an *inline* image ![inline image](attachment:test.png)"],
#   "attachments" : {
#     "test.png": {
#         "image/png" : "base64-encoded-png-data"
#     }
#   }
# }

cell = new_markdown_cell('''
# A Title

blabla ...
'''.lstrip())
print(cell)
notebook.cells.append(cell)

####################################################################################################

# {
#   "cell_type" : "code",
#   "execution_count": 1, # integer or null
#   "metadata" : {
#       "collapsed" : True, # whether the output of the cell is collapsed
#       "autoscroll": False, # any of true, false or "auto"
#   },
#   "source" : "[some multi-line code]",
#   "outputs": [{
#       # list of output dicts (described below)
#       "output_type": "stream",
#       ...
#   }],
# }

cell = new_code_cell('1+1')
notebook.cells.append(cell)

####################################################################################################

# {
#   "output_type" : "stream",
#   "name" : "stdout", # or stderr
#   "text" : "[multiline stream text]",
# }

# {
#   "output_type" : "display_data",
#   "data" : {
#     "text/plain" : "[multiline text data]",
#     "image/png": "[base64-encoded-multiline-png-data]",
#     "application/json": {
#       # JSON data is included as-is
#       "json": "data",
#     },
#   },
#   "metadata" : {
#     "image/png": {
#       "width": 640,
#       "height": 480,
#     },
#   },
# }

# {
#   "output_type" : "execute_result",
#   "execution_count": 42,
#   "data" : {
#     "text/plain" : "[multiline text data]",
#     "image/png": "[base64-encoded-multiline-png-data]",
#     "application/json": {
#       # JSON data is included as-is
#       "json": "data",
#     },
#   },
#   "metadata" : {
#     "image/png": {
#       "width": 640,
#       "height": 480,
#     },
#   },
# }

# {
#   'output_type': 'error',
#   'ename' : str,   # Exception name, as a string
#   'evalue' : str,  # Exception value, as a string
#
#   # The traceback will contain a list of frames,
#   # represented each as a string.
#   'traceback' : list,
# }

####################################################################################################

# [{
#     'data': {'text/plain': '2'},
#     'execution_count': 1,
#     'metadata': {},
#     'output_type': 'execute_result'
# }]

# [{
#     "data": {
#         "image/png": "iVBOR...mCC\n",
#         "text/plain": [
#             "<matplotlib.figure.Figure at 0x7f5ef4179e80>"
#         ]
#     },
#     "metadata": {},
#     "output_type": "display_data"
# }]

output = new_output('execute_result', data={'text/plain': '2'}, execution_count=1)
cell.outputs.append(output)

####################################################################################################

source = '''
import numpy as np
import matplotlib.pyplot as plt
figure = plt.figure(1, (20, 10))
x = np.arange(1, 10, .1)
y = np.sin(x)
plt.plot(x, y)
plt.show()
'''

cell = new_code_cell(source.strip())
notebook.cells.append(cell)
output = new_output('display_data', data={'image/png': image_base64})
cell.outputs.append(output)

####################################################################################################

# {
#   "cell_type" : "raw",
#   "metadata" : {
#     # the mime-type of the target nbconvert format.
#     # nbconvert to formats other than this will exclude this cell.
#     "format" : "mime/type"
#   },
#   "source" : "[some nbformat output text]"
# }

cell = new_raw_cell('raw ...')
notebook.cells.append(cell)

####################################################################################################

with open('test.ipynb', 'w') as fh:
    nbformat.write(notebook, fh)
