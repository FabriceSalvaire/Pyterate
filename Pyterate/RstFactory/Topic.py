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

__all__ = ['Topic']

####################################################################################################

from pathlib import Path
from typing import TYPE_CHECKING, Iterator
import logging
import os

from ..Template import TemplateAggregator
from .Document import Document, ParseError
from .Evaluator.NodeEvaluator import NodeEvaluatorError

if TYPE_CHECKING:
    from .RstFactory import RstFactory
    from .Settings import DefaultRstFactorySettings

####################################################################################################

NEWLINE = os.linesep

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Topic:

    """Class to implement a RST topic, basically a sub-directory.

    """

    _logger = _module_logger.getChild('Topic')

    SKIP_PATTERN = 'skip'
    IMAGE_DIRECTIVE = '.. image:: '
    IMAGE_DIRECTIVE_LENGTH = len(IMAGE_DIRECTIVE)

    ##############################################

    def __init__(self, factory: 'RstFactory', relative_path: Path) -> None:
        self._factory = factory
        self._relative_path = Path(relative_path)   # relative input path
        self._basename = relative_path.name   # topic directory

        self._path = self.settings.join_input_path(relative_path)   # input path
        self._rst_path = self.settings.join_rst_path(relative_path)   # output path

        self._subtopics = []   # self._retrieve_subtopics()
        self._documents = []
        self._links = []

        input_files = list(self._input_files_iterator())   # Fixme: better ?
        if input_files:
            self._logger.info(f'{NEWLINE}Process Topic: {relative_path}')
            if self.settings.make_rst:
                os.makedirs(self._rst_path, exist_ok=True)   # removed code
            for filename, language in input_files:
                path = self.join_path(filename)
                self._logger.info(f"{NEWLINE}Found input '{path}' handled by {language.name}")
                document = Document(self, Path(filename), language)
                if document.is_link:
                    self._logger.info(f"{NEWLINE}  found link: {filename}")
                    self._links.append(document)
                else:
                    self._logger.info(f"{NEWLINE}  found: {filename}")
                    self._documents.append(document)

    ##############################################

    def __bool__(self) -> bool:
        # Fixme: usage ???
        return self._rst_path.exists()
        # return bool(self._documents) or bool(self._links)

    ##############################################

    @property
    def factory(self) -> 'RstFactory':
        return self._factory

    @property
    def settings(self) -> 'DefaultRstFactorySettings':
        return self._factory.settings

    @property
    def use_myst(self) -> bool:
        return self.settings.use_myst

    @property
    def basename(self) -> str:
        return self._basename

    @property
    def path(self) -> Path:
        return self._path

    @property
    def rst_path(self) -> Path:
        return self._rst_path

    ##############################################

    def join_path(self, *args) -> Path:
        return self._path.joinpath(*args)

    def join_rst_path(self, *args) -> Path:
        return self._rst_path.joinpath(*args)

    ##############################################

    def _input_files_iterator(self) -> Iterator[[str, str]]:
        for basename in os.listdir(self._path):
            path = self._path.joinpath(basename)
            if path.is_file():
                language = self.settings.language_for(path)
                if language and not self._is_file_skipped(path, language):
                    yield basename, language

    ##############################################

    def _is_file_skipped(self, path: Path, language: str) -> bool:
        skip_pattern = language.enclose_markup(self.SKIP_PATTERN)
        with open(path) as fh:
            for i in range(2):
                line = fh.readline()   # .strip()
                if line.startswith(skip_pattern):
                    self._logger.info(f'{NEWLINE}Skip file {path}')
                    return True
        return False

    ##############################################

    def _index_path(self) -> Path:
        # Fixme: hardcoded filename ???
        return self.join_path(self.settings.add_extension('index'))

    ##############################################

    def _has_index(self) -> bool:
        return self._index_path().exists()

    ##############################################

    def _read_index(self):
        """Read readme and collect figures"""
        figures = []
        with open(self._index_path()) as fh:
            content = fh.read()
            for line in content.split(NEWLINE):
                if line.startswith(self.IMAGE_DIRECTIVE):
                    figure = line[self.IMAGE_DIRECTIVE_LENGTH:]
                    figures.append(figure)
        return content, figures

    ##############################################

    def process_documents(self) -> None:
        for _ in self._documents:
            self.process_document(_)

    ##############################################

    def process_document(self, document: Document) -> None:
        self._logger.info(f'Process document {document.path}')
        try:
            document.read()
        except (ParseError, NodeEvaluatorError) as exception:
            self._logger.error(exception)
            self._logger.error(f"Failed to parse document {document.path}")
            self.factory.register_failure(document)
            # Fixme: insert errors in rst
            return
        make_notebook = False
        if self.settings.force or document:
            if self.settings.run_code:
                document.run()
            if self.settings.make_rst:
                document.make_rst()
            make_notebook = True
        if self.settings.make_external_figure:
            document.make_external_figure(self.settings.force)
        if self.settings.make_notebook and make_notebook:
            document.make_notebook()

    ##############################################

    def _directory_iterator(self) -> Iterator[Path]:
        for filename in os.listdir(self._rst_path):
            path = self.join_rst_path(filename)
            if path.is_dir():
                yield path   # absolut path

    ##############################################

    def _subtopic_iterator(self) -> Iterator['Topic']:
        for path in self._directory_iterator():
            # Fixme: hardcoded filename !
            index_path = path.joinpath(self.settings.add_extension('index'))
            if index_path.exists():
                relative_path = path.relative_to(self.settings.rst_path)
                topic = self._factory.topics[relative_path]
                yield topic

    ##############################################

    def _retrieve_subtopics(self) -> None:
        # Fixme: ???
        if not self:
            return None
        self._subtopics = list(self._subtopic_iterator())

    ##############################################

    def make_toc(self) -> None:
        """ Create the TOC. """
        if not self.settings.make_rst:
            return
        # Fixme: ???
        if not self:
            return

        toc_path = self.join_rst_path(self.settings.add_extension('index'))
        self._logger.info(f'{NEWLINE}Create TOC {toc_path}')

        kwargs = {
            'use_myst': self.use_myst,
        }

        if self._has_index():
            readme_content, figures = self._read_index()
            kwargs['user_content'] = readme_content
            # Fixme: external figure in readme / check PySpice code
            # if make_external_figure:
            #   ...
        else:
            kwargs['title'] = self._basename.replace('-', ' ').title()   # Fixme: Capitalize of

        # Sort the TOC
        # Fixme: sometimes we want a particular order !
        file_dict = {_.basename: _.doc_filename for _ in self._documents}
        file_dict.update({_.basename: _.link_rst for _ in self._links})
        kwargs['toc_items'] = [file_dict[x] for x in sorted(file_dict.keys())]

        self._retrieve_subtopics()
        subtopics = [topic.basename for topic in self._subtopics]
        kwargs['subtopics'] = sorted(subtopics)

        if self.settings.show_counters:
            self._number_of_documents = len(self._documents)   # don't count links twice
            kwargs['number_of_links'] = len(self._links)
            kwargs['number_of_subtopics'] = len(self._subtopics)
            number_of_subtopics = sum([topic._number_of_documents for topic in self._subtopics])
            kwargs['number_of_documents'] = self._number_of_documents + number_of_subtopics

        template_aggregator = TemplateAggregator(self.settings.template_environment)
        template_aggregator.append('toc', **kwargs)

        with open(toc_path, 'w') as fh:
            fh.write(str(template_aggregator))
