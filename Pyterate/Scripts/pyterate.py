####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2017 Salvaire Fabrice
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

import Pyterate.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from pathlib import Path
import argparse
import os
import sys

import Pyterate
from Pyterate.RstFactory.Document import Document
from Pyterate.RstFactory.RstFactory import RstFactory
from Pyterate.RstFactory.Settings import DefaultRstFactorySettings
from Pyterate.RstFactory.Topic import Topic

####################################################################################################

def main():

    parser = argparse.ArgumentParser(description='Generate RST files')

    parser.add_argument('--config',
                        default='pyterate-settings.py',
                        help="Pyterate settings file")

    parser.add_argument('--document-path',
                        default=None,
                        help="Document path")

    parser.add_argument('--skip-code-execution',
                        action='store_true', default=False,
                        help="Don't generate figures")

    parser.add_argument('--skip-external-figure',
                        action='store_true', default=False,
                        help="Don't generate external figures")

    parser.add_argument('--force',
                        action='store_true', default=False,
                        help="Force the figure generation")

    parser.add_argument('--version',
                        action='store_true', default=False,
                        help="Show version")

    args = parser.parse_args()


    if args.version:
        Pyterate.show_version()
        sys.exit(0)

    if not Path(args.config).exists():
        logger.info('Any config file, use default settings')
        settings = DefaultRstFactorySettings()
    else:
        logger.info('Load config file {}'.format(args.config))
        import importlib.util
        spec = importlib.util.spec_from_file_location('Config', args.config)
        Config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(Config)
        settings = Config.RstFactorySettings()

    settings.run_code = not args.skip_code_execution
    settings.make_external_figure = not args.skip_external_figure
    settings.force = args.force # Fixme: document mode ?

    rst_factory = RstFactory(settings)

    if args.document_path:
        document_path = Path(args.document_path)
        settings = rst_factory.settings
        document_path = settings.relative_input_path(document_path)
        topic = Topic(rst_factory, document_path.parent)
        language = settings.language_for(args.document_path)
        document = Document(topic, document_path.name, language)
        topic.process_document(document)
    else:
        rst_factory.process_recursively()
