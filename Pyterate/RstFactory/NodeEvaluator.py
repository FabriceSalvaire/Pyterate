####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

__all__ = [
    'NodeEvaluator',
]

####################################################################################################

import json
import logging
import tempfile

from ..Jupyter import JupyterClient
from .Dom.Markups import CodeChunk, GuardedCodeChunk, FigureChunk
from .Dom.Registry import MarkupRegistry

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class NodeEvaluatorError(Exception):

    ##############################################

    def __init__(self, code):

        self._code = code

    ##############################################

    def __repr__(self):

        return "Syntax error in \n{0._code}".format(self)

####################################################################################################

class NodeCommand:

    ##############################################

    def __init__(self, name, args, kwargs):

        self._name = name
        self._args = args
        self._kwargs = kwargs

    ##############################################

    def __repr__(self):

        return '{0.__class__.__name__} {0._name} {0._args} {0._kwargs}'.format(self)

    ##############################################

    def to_chunk(self, document):

        chunk_cls = MarkupRegistry.command_to_class(self._name)
        return chunk_cls(document, *self._args, **self._kwargs)

####################################################################################################

class NodeEvaluator:

    _logger = _module_logger.getChild('Document')

    EXPORT_TEMPLATE = '''
_ = {}
export_value(_)
'''

    ##############################################

    def __init__(self, language):

        self._language = language
        self._start_jupyter(language)

        self._commands = []

        self._sandbox_globals = {
            '__command__': self._commands,
            'export': self._export,
        }

        for name in MarkupRegistry.commands():
            self._sandbox_globals[name] = self._make_figure_wrapper(name)

        self._sandbox_locals = None
        self._has_error = None

    ##############################################

    def _start_jupyter(self, language):

        self._working_directory = tempfile.TemporaryDirectory()
        self._jupyter_client = JupyterClient(self._working_directory.name, kernel=language.jupyter_kernel)
        code = self._language.setup_code # .format(**kwargs)
        self._jupyter_client.run_cell(code)

    ##############################################

    def _export_method(self, method):

        def wrapper(*args, **kwargs):
            method(self, *args, **kwargs)

        return wrapper

    ##############################################

    def _make_figure_wrapper(self, name):

        def wrapper(*args, **kwargs):
            self._commands.append(NodeCommand(name, args, kwargs))

        return wrapper

    ##############################################

    def _log_error(self, code, output):

        self._has_error = True
        self._logger.error(
            "Error in document {}\n".format(self._document_path) +
            str(code) + '\n\n' +
            str(output)
        )

    ##############################################

    def _export_value(self, name, code):

        self._logger.info('Export value: code\n{} := {}'.format(name, code))

        outputs = self._jupyter_client.run_cell(code)

        for output in outputs:
            if output.is_error:
                self._log_error(code, output)

        # Fixme: to func ??? , duplicated
        # Fixme: 0 str() ???
        json_data = outputs[0].result
        value = json.loads(json_data[1:-1]) # remove quote

        self._logger.info('Export value: value \n{} = {}'.format(name, value))
        self._sandbox_locals[name] = value

    ##############################################

    def _export(self, *names, **kwargs):

        self._logger.info('Export values\n{} {}'.format(names, kwargs))

        for name in names:
            code = 'export_value({})'.format(name)
            self._export_value(name, code)

        for name, code_value in kwargs.items():
            code = self.EXPORT_TEMPLATE.format(code_value)
            self._export_value(name, code)

    ##############################################

    def _run_code_chunk(self, chunk):

        code = chunk.to_code()
        if code:
            # self._logger.info('Execute\n{}'.format(code))
            outputs = self._jupyter_client.run_cell(code)
            if outputs:
                output = outputs[0]
                # self._logger.info('Output {0.output_type}\n{0}'.format(output))
                chunk.outputs = outputs
            for output in outputs:
                if output.is_error and not isinstance(chunk, GuardedCodeChunk):
                    self._log_error(code, output)

    ##############################################

    def _eval_figure(self, chunk):

        self._commands.clear()

        code = str(chunk)

        try:
            exec(compile(code, 'inline', 'exec'), self._sandbox_globals, self._sandbox_locals)
        except SyntaxError:
            raise NodeEvaluatorError(code)

        return self._commands

    ##############################################

    def run(self, dom, document_path):

        self._document_path = document_path

        code = self._language.document_setup_code.format(file=document_path)
        self._jupyter_client.run_cell(code)

        self._sandbox_locals = {}
        self._has_error = False

        for chunk in dom:
            if chunk.is_executed:
                self._run_code_chunk(chunk)
            elif isinstance(chunk, FigureChunk):
                for figure_command in self._eval_figure(chunk):
                    figure_chunk = figure_command.to_chunk(chunk.document)
                    chunk.append_child(figure_chunk)
                    if figure_chunk.is_executed:
                        self._run_code_chunk(figure_chunk)

        return not self._has_error
