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

"""This module contains all the class markups.

"""

####################################################################################################

__all__ = [
    'CodeNode',
    'CommentNode',
    'FigureNode',
    'GuardedCodeNode',
    'HiddenCodeNode',
    'InteractiveCodeNode',
    'LiteralNode',
    'MarkdownFormatNode',
    'MarkdownNode',
    'OutputNode',
    'RstFormatNode',
    'RstNode',
]

####################################################################################################

import logging

from nbformat import v4 as nbv4

from Pyterate.Tools.MarkupConverter import markdown_to_rest
from .Dom import Node, ExecutedNode, TextNode, MarkdownCellMixin
from .FigureNodes import ImageNode, ExternalFigureNode, TableFigureNode, SaveFigureNode
from .LitteralIncludeNodes import LiteralIncludeNode

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class MarkdownMixin:

    ##############################################

    def to_rst(self):
        # markdown_strict
        return markdown_to_rest(self.to_markdown())

####################################################################################################

class CommentNode(Node):
    MARKUP = '?'

####################################################################################################

class FigureNode(Node):

    MARKUP = 'f'

    _logger = _module_logger.getChild('FigureNode')

    ##############################################

    def __init__(self, document):
        super().__init__(document)
        self._childs = []

    ##############################################

    def append_child(self, child):
        self._childs.append(child)

    ##############################################

    def iter_on_childs(self):
        return iter(self._childs)

    ##############################################

    def to_cell(self):
        cell = []
        for child in self.iter_on_childs():
            # skip LitteralIncludeNodes.GetthecodeNode
            if isinstance(child, (LiteralIncludeNode, TableFigureNode)):
                markdown = child.to_markdown()
                _ = nbv4.new_markdown_cell(markdown)
                cell.append(_)
            elif isinstance(child, SaveFigureNode):
                pass
            elif isinstance(child, ImageNode):
                _ = child.to_cell()
                if _ is not None:
                    cell.append(_)
            else:
                self._logger.info("Unsupported figure child node type {}".format(type(node)))
        return cell

####################################################################################################

class RstNode(TextNode):

    """ This class represents a RST content. """

    MARKUP = 'r'

    ##############################################

    def to_rst(self):
        return str(self)

    ##############################################

    def to_format_node(self):
        return RstFormatNode(self)

####################################################################################################

class LiteralNode(Node):

    """ This class represents a literal block. """

    MARKUP = 'l'

    ##############################################

    def to_rst(self):
        if bool(self):
            source = self.indent_lines(self._lines)
            # rst = self.directive('class', args=('literal-node',)) # Don't work !
            return self.code_block_directive('py') + source + '\n'
        else:
            return ''

    ##############################################

    def to_cell(self):
        markdown = '```\n'
        markdown += self.to_markdown()
        markdown += '```\n'
        return nbv4.new_markdown_cell(markdown)

####################################################################################################

class MarkdownNode(MarkdownMixin, TextNode):

    """ This class represents a RST content. """

    MARKUP = 'm'

    ##############################################

    def to_markdown(self):
        return str(self)

    ##############################################

    def to_format_node(self):
        return MarkdownFormatNode(self)

####################################################################################################

class FormatNode(MarkdownCellMixin, ExecutedNode):

    ##############################################

    def __init__(self, node):
        super().__init__(node.document)
        self._lines = node._lines

    ##############################################

    def to_code(self):
        txt = '\n'.join(self._lines)
        txt = txt.replace('{', '{{') # to escape them
        txt = txt.replace('}', '}}')
        txt = txt.replace(self.opening_format_markup, '{')
        txt = txt.replace(self.closing_format_markup, '}')
        txt = txt.replace(self.escaped_opening_format_markup, self.opening_format_markup)
        txt = txt.replace(self.escaped_closing_format_markup, self.closing_format_markup)
        return 'print(r"""' + txt + '""".format(**locals()))\n'

####################################################################################################

class RstFormatNode(FormatNode):

    ##############################################

    def to_rst(self):
        # Fixmes: more than one output
        return str(self.outputs[0]) + '\n'

####################################################################################################

class MarkdownFormatNode(MarkdownMixin, FormatNode):

    ##############################################

    def to_markdown(self):
        # Fixmes: more than one output
        return str(self.outputs[0]) + '\n'

####################################################################################################

class CodeNode(ExecutedNode):

    """ This class represents a code block. """

    MARKUP = 'code' # fake markup

    ##############################################

    def to_rst(self):
        if bool(self):
            # Fixme: if previous is hidden : merge ???
            rst = self.code_block_directive(self.lexer)
            rst += self.indent_lines(self._lines)
            for output in self.outputs:
                if output.is_error:
                    rst += self.code_block_directive(self.error_lexer)
                    rst += self.indent_output(output)
            return rst + '\n'
        else:
            return '' # Fixme: ???

    ##############################################

    def to_code(self):
        source = ''
        for line in self._lines:
            # Fixme:
            if not line.startswith('pylab.show') and not line.startswith('plt.show'):
                source += line + '\n'
        return source

    ##############################################

    def to_cell(self):
        code = self.to_code()
        cell = nbv4.new_code_cell(code)
        for output in self.outputs:
            cell.outputs.append(output.node)
        return cell

####################################################################################################

class GuardedCodeNode(CodeNode):

    MARKUP = 'e'
    ENCLOSING_MARKUP = True

####################################################################################################

class InteractiveCodeNode(CodeNode):

    MARKUP = 'i'
    ENCLOSING_MARKUP = True

    ##############################################

    def to_line_node(self):
        nodes = []
        for line in self._lines:
            if not line.strip():
                continue
            node = InteractiveLineCodeNode(self._document, line)
            nodes.append(node)
        return nodes

####################################################################################################

class InteractiveLineCodeNode(CodeNode):

    ##############################################

    def __init__(self, document, line):
        super().__init__(document)
        self.append(line)

    ##############################################

    def to_rst(self):
        rst = super().to_rst()
        rst += self.code_block_directive('none')
        for output in self.outputs:
            if output.is_result:
                rst += self.indent_output(output)
        return rst + '\n'

####################################################################################################

class HiddenCodeNode(CodeNode):

    """ This class represents a hidden code block. """

    MARKUP = 'h'

    ##############################################

    def to_rst(self):
        return ''

####################################################################################################

class OutputNode(Node):

    """ This class represents an output block. """

    MARKUP = 'o'

    ##############################################

    @property
    def code_node(self):
        return self._code_node

    @code_node.setter
    def code_node(self, value):
        self._code_node = value

    ##############################################

    def to_rst(self):
        rst = self.code_block_directive('none')
        for output in self._code_node.outputs:
            if output.is_stream:
                rst += self.indent_output(output)
        return rst + '\n'

    ##############################################

    def to_cell(self):
        return None
