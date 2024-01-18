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

from pathlib import Path
import logging
import os

import nbformat
from nbformat import v4 as nbv4

####################################################################################################

from ..Template import TemplateAggregator
from ..Tools.Timestamp import timestamp
from .Dom.Dom import Dom, TextNode
from .Dom.FigureNodes import ImageNode, ExternalFigureNode
from .Dom.Markups import *
from .Dom.Registry import MarkupRegistry
from .Evaluator.NodeEvaluator import NodeEvaluator

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class ParseError(Exception):

    ##############################################

    def __init__(self, message, line):
        self._message = message
        self._line = line

    ##############################################

    def __repr__(self):
        return "{0.message} on line\n{0._line}".format(self)

####################################################################################################

class Document:

    """This class is responsible to process a document."""

    _logger = _module_logger.getChild('Document')

    ##############################################

    def __init__(self, topic, input_file, language):

        self._topic = topic
        self._input_file = input_file
        self._basename = input_file.stem
        self._language = language

        path = topic.join_path(input_file)

        self._is_link = path.is_symlink()
        if self._is_link:
            self._path = path # symlink
            self._rst_path = None
        else:
            self._path = path.resolve() # Python input path
            self._rst_path = self._topic.join_rst_path(self.rst_filename)

    ##############################################

    @property
    def factory(self):
        return self._topic.factory

    @property
    def topic(self):
        return self._topic

    @property
    def topic_path(self):
        return self._topic.path

    @property
    def topic_rst_path(self):
        return self._topic.rst_path

    @property
    def factory(self):
        return self._topic.factory

    @property
    def settings(self):
        return self._topic.settings

    @property
    def language(self):
        return self._language

    @property
    def path(self):
        return self._path

    @property
    def basename(self):
        return self._basename

    @property
    def rst_filename(self):
        return self._basename + '.rst'

    @property
    def nb_filename(self):
        return self._basename + '.ipynb' # Fixme

    @property
    def rst_inner_path(self):
        return self._rst_path.relative_to(self._topic.rst_path)

    @property
    def dom(self):
        return self._dom

    ##############################################

    @property
    def is_link(self):
        return self._is_link

    @property
    def link_py(self):
        """return the Python symlink path"""
        if self._is_link:
            return Path(os.readlink(self._path))
        else:
            return None

    @property
    def link_rst(self):
        """return the reST symlink path"""
        if self._is_link:
            link = self.link_py
            # Fixme: to func
            return link.parent.joinpath(link.stem + '.rst')
        else:
            return None

    ##############################################

    def read(self):

        # Fixme: update doc
        # Fixme: API ??? called process_document()

        # Must be called first !

        """Parse the source code and extract nodes of codes, RST contents, plot and Tikz figures.  The
        source code is annoted using comment lines starting with special directives of the form
        *#directive name#*.  RST content lines start with *#!#*.  We can include a figure using
        *#lfig#*, a figure generated by matplotlib using the directive *#fig#*, tikz figure using
        *#tz#* and the content of a file using *#itxt#* and *#i#* for codes.  Comment that must be
        skipped start with *#?#*.  Hidden code start with *#h#*.  The directive *#o#* is used to
        split the output and to instruct to include the previous node.  RST content can be
        formatted with variable from the locals dictionary using *@<@...@>@* instead of *{...}*.

        """

        with open(self._path) as fh:
            source = fh.readlines()

        dom = self._source_to_nodes(source)
        self._dom = self._post_process_dom(dom)

        # for node in self._dom:
        #     print('\n' + '#'*50)
        #     print(node)

    ##############################################

    @property
    def source_timestamp(self):
        return timestamp(self._path)

    ##############################################

    @property
    def rst_timestamp(self):
        if self._rst_path.exists():
            return timestamp(self._rst_path)
        else:
            return -1

    ##############################################

    def __bool__(self):
        """Return True if source is older than rst."""
        return self.source_timestamp > self.rst_timestamp or self.factory.was_failure(self)

    ##############################################

    def _run(self):
        self._logger.info('\nRun document {}'.format(self._path))
        node_evaluator = NodeEvaluator(self._language)
        if not node_evaluator.run(self._dom, self._path, eval_figure=self.settings.make_rst):
            self._logger.error("Failed to run document {}".format(self._path))
            self.factory.register_failure(self)
        # Windows has an issue with the garbage collecting of the temporary working directory
        node_evaluator.stop_jupyter()

    ##############################################

    def run(self):
        self._run()

        # tenacity like code
        # try_counter = 0
        # while True:
        #     if try_counter:
        #         self._logger.error('Retry to run Jupyter kernel ...')
        #     if try_counter > 10:
        #         self._logger.error('Retry done')
        #         raise RuntimeError('Too much timeout')
        #     try:
        #         self._run()
        #     except TimeoutError:
        #         # Fixme: cleanup ???
        #         try_counter += 1
        #         self._logger.error('Catched timeout')

    ##############################################

    def symlink_source(self, source_path):
        """Create a symlink to a source in the reST document directory"""

        # used by LocaleFigureNode

        source = self._topic.join_path(source_path)
        basename = source_path.name
        target = self._topic.join_rst_path(basename)

        # Fixme: too early check
        # if not source_path.exists():
        #     raise NameError("File {} doesn't exist, cannot create a symlink to {}".format(source_path, target))

        # Fixme: Windows UCA
        if not target.exists() and self.settings.make_rst:
            target.symlink_to(source)

        return basename

    ##############################################

    def make_external_figure(self, force):
        # Fixme: simplify ???
        for node in self._dom:
            if isinstance(node, FigureNode):
                for child in node.iter_on_childs():
                    if isinstance(child, ExternalFigureNode):
                        if force or child:
                            child.make_figure()

    ##############################################

    def _parse_line(self, line):

        markup = None
        open_markup = False
        close_markup = False
        parsed_line = line

        def is_valid_makup(markup):
            if not MarkupRegistry.is_valid_makup(markup):
                raise ParseError("Invalid markup", line)

        def is_valid_enclosing_makup(markup):
            if not MarkupRegistry.is_valid_enclosing_makup(markup):
                raise ParseError("Invalid markup", line)

        def push_stack(markup):
            if not self._stack:
                self._stack.append(markup)
            else:
                raise ParseError("Nested markup", line)

        def pop_stack(markup):
            if self._stack:
                opening_markup = self._stack.pop()
                if opening_markup != markup:
                    raise ParseError("Unbalanced and mismatch markup", line)
            else:
                raise ParseError("Unbalanced markup", line)

        if line.startswith(self._language.left_markup):
            right = line.find(self._language.right_markup, 1)
            if right != -1:
                markup = line[1:right]
                if self._language.open_markup in markup:
                    markup = markup[1]
                    is_valid_enclosing_makup(markup)
                    open_markup = True
                    parsed_line = None
                    push_stack(markup)
                elif self._language.close_markup in markup:
                    markup = markup[0]
                    is_valid_enclosing_makup(markup)
                    close_markup = True
                    parsed_line = None
                    pop_stack(markup)
                elif markup:
                    is_valid_makup(markup)
                    parsed_line = line[right+1:]
                    # strip space
                    if parsed_line and parsed_line[0] == ' ':
                        parsed_line = parsed_line[1:]
                else:
                    markup = None
                    # Fixme: ??? raise ParseError('Invalid Markup', line)

        enclosing_markup = open_markup or close_markup

        if self._stack:
            if markup is None:
                markup = self._stack[-1] # use enclosing markup
            elif not enclosing_markup:
                raise ParseError("Nested markup", line)

        if markup is None:
            markup_cls = CodeNode
        else:
            markup_cls = MarkupRegistry.markup_to_class(markup)

        return markup_cls, parsed_line

    ##############################################

    def _source_to_nodes(self, source):
        """Build the raw DOM from the source"""

        dom = Dom()
        prev_markup_cls = None
        self._stack = []
        for line in source:
            line = line.rstrip()

            # Handle rule comments
            if self._language.rule_filter(line):
                continue

            # Lookup for markup
            markup_cls, line = self._parse_line(line)

            # Fixme: invalid markup
            # self._logger.info('Markup {} \n'.format(markup_cls) + line.rstrip())

            # Is it new node ?
            if markup_cls != prev_markup_cls:
                node = markup_cls(self)
                dom.append(node)

            # Skip enclosing markup lines
            if line is not None:
                dom.last_node.append(line)

            prev_markup_cls = markup_cls

        return dom

    ##############################################

    def _post_process_dom(self, raw_dom):
        """Perform some post-processing on DOM"""

        dom = Dom()
        for node in raw_dom.iter_on_not_empty_node():
            previous_node = dom.last_node
            if isinstance(node, CommentNode):
                continue
            elif previous_node is not None and previous_node.mergable(node):
                previous_node.merge(node)
            # Fixme: could use childs ???
            elif isinstance(node, InteractiveCodeNode):
                for line_node in node.to_line_node():
                    dom.append(line_node)
            else:
                if isinstance(node, OutputNode):
                    if previous_node is not None and previous_node.is_executed:
                        node.code_node = previous_node
                    else:
                        raise NameError('Previous node must be code')
                elif isinstance(node, TextNode):
                    if node.has_format():
                        node = node.to_format_node()
                dom.append(node)

        return dom

    ##############################################

    def _has_title(self):

        """Return whether a title is defined."""

        # Fixme: test if first node ?
        for node in self._dom:
            if isinstance(node, RstNode):
                content = str(node)
                if '='*(3+2) in content:  # Fixme: hardcoded !
                    return True

        return False

    ##############################################

    def make_rst(self):

        """Generate the document RST file."""

        self._logger.info("\nCreate RST file {}".format(self._rst_path))

        # place the input file in the rst path
        link_path = self._topic.join_rst_path(self._input_file)
        if not link_path.exists():
            link_path.symlink_to(self._path)

        kwargs = {
            'input_file':self._input_file,
        }

        has_title = self._has_title()
        if not has_title:
            kwargs['title'] = self._basename.replace('-', ' ').title()  # Fixme: Capitalize of

        template_aggregator = TemplateAggregator(self.settings.template_environment)
        template_aggregator.append('document', **kwargs)

        with open(self._rst_path, 'w') as fh:
            fh.write(str(template_aggregator))
            for node in self._dom:
                if isinstance(node, FigureNode):
                    for child in node.iter_on_childs():
                        fh.write(child.to_rst())
                else:
                    fh.write(node.to_rst())

    ##############################################

    def make_notebook(self):

        """Generate a notebook file.

        https://nbformat.readthedocs.io/en/latest
        """

        notebook = nbv4.new_notebook()

        notebook.metadata.update(self.language.notebook_metadata)

        last_cell = None
        for node in self._dom:
            if last_cell is not None and isinstance(node, ImageNode):
                _ = node.to_output_cell()
                if _ is not None:
                    last_cell.outputs.append(_)
            else:
                cell = node.to_cell()
                if cell:
                    if not isinstance(cell, list):
                        last_cell = cell
                        cell = [cell]
                    for _ in cell:
                        notebook.cells.append(_)

        path = self._topic.join_rst_path(self.nb_filename)
        self._logger.info("\nCreate Notebook file {}".format(path))
        with open(path, 'w') as fh:
            nbformat.write(notebook, fh)
