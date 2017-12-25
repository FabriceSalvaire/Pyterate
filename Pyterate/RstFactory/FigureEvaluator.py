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

__all__ = [
    'FigureEvaluator',
]

####################################################################################################

from .Dom.Registry import MarkupRegistry

####################################################################################################

class FigureEvaluatorError(Exception):

    ##############################################

    def __init__(self, code):

        self._code = code

    ##############################################

    def __repr__(self):

        return "Syntax error in \n{0._code}".format(self)

####################################################################################################

class FigureCommand:

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

class FigureEvaluator:

    ##############################################

    def __init__(self):

        self._commands = []

        self._sandbox_globals = {
            '__command__': self._commands,
        }

        for name in MarkupRegistry.commands():
            self._sandbox_globals[name] = self.make_figure_wrapper(name)

        self._sandbox_locals = {}

    ##############################################

    def make_figure_wrapper(self, name):

        def figure_wrapper(*args, **kwargs):
            self._commands.append(FigureCommand(name, args, kwargs))

        return figure_wrapper

    ##############################################

    def eval(self, code):

        self._commands.clear()

        try:
            exec(compile(code, 'inline', 'exec'), self._sandbox_globals, self._sandbox_locals)
        except SyntaxError:
            raise FigureEvaluatorError(code)
        return self._commands
