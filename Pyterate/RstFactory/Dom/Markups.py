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
import os
from typing import TYPE_CHECKING, Iterable

from nbformat import v4 as nbv4
from nbformat import NotebookNode

from Pyterate.Tools.MarkupConverter import markdown_to_rest
from .Dom import Node, ExecutedNode, TextNode, MarkdownCellMixin, MystMixin
from .FigureNodes import ImageNode, TableFigureNode, SaveFigureNode
from .LitteralIncludeNodes import LiteralIncludeNode

if TYPE_CHECKING:
    from ..Document import Document

####################################################################################################

NEWLINE = os.linesep

_module_logger = logging.getLogger(__name__)

####################################################################################################

class MarkdownMixin:

    def to_rst(self) -> str:
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

    def __init__(self, document: 'Document') -> None:
        super().__init__(document)
        self._childs = []

    ##############################################

    def append_child(self, child: Node) -> None:
        self._childs.append(child)

    ##############################################

    def iter_on_childs(self) -> Iterable[Node]:
        return iter(self._childs)

    ##############################################

    def to_cell(self) -> NotebookNode:
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

    def to_rst(self) -> str:
        return str(self)

    ##############################################

    def to_myst(self) -> str:
        return self.to_markdown()

    ##############################################

    def to_format_node(self) -> 'RstFormatNode':
        return RstFormatNode(self)

####################################################################################################

class LiteralNode(MystMixin, Node):

    """ This class represents a literal block. """

    MARKUP = 'l'

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        indentation = self.indentation(use_myst)
        if bool(self):
            source = self.indent_lines(self._lines, indentation)
            # rst = self.directive('class', args=('literal-node',)) # Don't work !
            rst = self.code_block_directive('py', use_myst) + source + NEWLINE
            if use_myst:
                rst += self.close_directive(use_myst)
            return rst
        else:
            return ''

    ##############################################

    def to_cell(self) -> NotebookNode:
        _ = f'```{NEWLINE}'
        markdown = _
        markdown += self.to_markdown()
        markdown += _
        return nbv4.new_markdown_cell(markdown)

####################################################################################################

class MarkdownNode(MarkdownMixin, TextNode):

    """ This class represents a Markdown content. """

    MARKUP = 'm'

    ##############################################

    def to_markdown(self) -> str:
        return str(self)

    def to_myst(self) -> str:
        return self.to_markdown()

    ##############################################

    def to_format_node(self) -> 'MarkdownFormatNode':
        return MarkdownFormatNode(self)

####################################################################################################

class FormatNode(MarkdownCellMixin, ExecutedNode):

    ##############################################

    def __init__(self, node: Node) -> None:
        super().__init__(node.document)
        self._lines = node._lines

    ##############################################

    def to_code(self) -> str:
        txt = NEWLINE.join(self._lines)
        txt = txt.replace('{', '{{') # to escape them
        txt = txt.replace('}', '}}')
        txt = txt.replace(self.opening_format_markup, '{')
        txt = txt.replace(self.closing_format_markup, '}')
        txt = txt.replace(self.escaped_opening_format_markup, self.opening_format_markup)
        txt = txt.replace(self.escaped_closing_format_markup, self.closing_format_markup)
        return 'print(r"""' + txt + '""".format(**locals()))\n'

####################################################################################################

class FormatNodeMixin:
    # Fixme: ok ?

    def _to_rst(self) -> str:
        # Fixmes: more than one output
        return str(self.outputs[0]) + NEWLINE

    def to_myst(self) -> str:
        return self._to_rst()

####################################################################################################

class RstFormatNode(FormatNodeMixin, FormatNode):
    pass

####################################################################################################

class MarkdownFormatNode(MarkdownMixin, FormatNodeMixin, FormatNode):

    def to_markdown(self) -> str:
        return self._to_rst()

####################################################################################################

class CodeNode(MystMixin, ExecutedNode):

    """ This class represents a code block. """

    MARKUP = 'code' # fake markup

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        indentation = self.indentation(use_myst)
        if bool(self):
            # Fixme: if previous is hidden : merge ???
            rst = self.code_block_directive(self.lexer, use_myst)
            rst += self.indent_lines(self._lines, indentation)
            rst += self.close_directive(use_myst)
            for output in self.outputs:
                if output.is_error:
                    rst += self.code_block_directive(self.error_lexer, use_myst)
                    rst += self.indent_output(output, indentation)
                    rst += self.close_directive(use_myst)
            return rst + NEWLINE
        else:
            return '' # Fixme: ???

    ##############################################

    def to_code(self) -> str:
        source = ''
        for line in self._lines:
            # Fixme:
            if not line.startswith('pylab.show') and not line.startswith('plt.show'):
                source += line + NEWLINE
        return source

    ##############################################

    def to_cell(self) -> NotebookNode:
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

    def to_line_node(self) -> list['InteractiveCodeNode']:
        nodes = []
        for line in self._lines:
            if not line.strip():
                continue
            _ = InteractiveLineCodeNode(self._document, line)
            nodes.append(_)
        return nodes

####################################################################################################

class InteractiveLineCodeNode(CodeNode):

    ##############################################

    def __init__(self, document: 'Document', line: str):
        super().__init__(document)
        self.append(line)

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        indentation = self.indentation(use_myst)
        rst = super()._to_rst(use_myst)
        rst += self.code_block_directive('none', use_myst)
        for output in self.outputs:
            if output.is_result:
                rst += self.indent_output(output, indentation)
        rst += self.close_directive(use_myst)
        rst += NEWLINE
        return rst

####################################################################################################

class HiddenCodeNode(CodeNode):

    """ This class represents a hidden code block. """

    MARKUP = 'h'

    ##############################################

    def to_rst(self):
        return ''

    def to_myst(self):
        return ''

####################################################################################################

class OutputNode(MystMixin, Node):

    """ This class represents an output block. """

    MARKUP = 'o'

    ##############################################

    @property
    def code_node(self) -> Node:
        return self._code_node

    @code_node.setter
    def code_node(self, value: Node):
        self._code_node = value

    ##############################################

    def _to_rst(self, use_myst: bool = False) -> str:
        indentation = self.indentation(use_myst)
        rst = self.code_block_directive('none', use_myst)
        for output in self._code_node.outputs:
            if output.is_stream:
                rst += self.indent_output(output, indentation)
        rst += self.close_directive(use_myst)
        rst += NEWLINE
        return rst

    ##############################################

    def to_cell(self) -> Node:
        return None
