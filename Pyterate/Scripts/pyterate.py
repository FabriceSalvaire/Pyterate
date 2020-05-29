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

__all__ = ['main']

####################################################################################################

from pathlib import Path
import argparse
import sys

import Pyterate.Logging.Logging as Logging
_logger = Logging.setup_logging()

####################################################################################################

def _load_module(module_path, module_name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

####################################################################################################

def main():

    parser = argparse.ArgumentParser(description='Generate reRST files')

    parser.add_argument('--config',
                        default='pyterate-settings.py',
                        help="Pyterate settings file")

    parser.add_argument('--document-path',
                        default=None,
                        help="only process this document")

    parser.add_argument('--only-run',
                        action='store_true', default=False,
                        help="same as --skip-rst --skip-external-figure --skip-notebook")

    parser.add_argument('--skip-processing',
                        action='store_true', default=False,
                        help="Start and quit without processing documents")

    parser.add_argument('--skip-code-execution',
                        action='store_true', default=False,
                        help="Don't generate figures")

    parser.add_argument('--skip-external-figure',
                        action='store_true', default=False,
                        help="Don't generate external figures")

    parser.add_argument('--skip-rst',
                        action='store_true', default=False,
                        help="Don't generate reST")

    parser.add_argument('--skip-notebook',
                        action='store_true', default=False,
                        help="Don't generate notebook")

    parser.add_argument('--force',
                        action='store_true', default=False,
                        help="Force the figure generation")

    parser.add_argument('--version',
                        action='store_true', default=False,
                        help="Show version")

    args = parser.parse_args()

    ##############################################

    if args.version:
        import Pyterate
        Pyterate.show_version()
        sys.exit(0)

    # Load config ...

    if not Path(args.config).exists():
        _logger.info('Any config file, use default settings')
        from Pyterate.RstFactory.Settings import DefaultRstFactorySettings
        settings = DefaultRstFactorySettings()
    else:
        _logger.info('Load config file %s', args.config)
        Config = _load_module(args.config, 'Config')
        settings = Config.RstFactorySettings()

    settings.force = args.force  # Fixme: document mode ?
    settings.make_external_figure = not args.skip_external_figure
    settings.make_notebook = not args.skip_notebook
    settings.make_rst = not args.skip_rst
    settings.run_code = not args.skip_code_execution

    if args.only_run:
        settings.make_external_figure = False
        settings.make_notebook = False
        settings.make_rst = False
        settings.run_code = True

    from Pyterate.RstFactory.RstFactory import RstFactory

    # Process ...

    if args.skip_processing:
        sys.exit(0)

    rst_factory = RstFactory(settings)

    if args.document_path:
        from Pyterate.RstFactory.Document import Document
        from Pyterate.RstFactory.Topic import Topic
        document_path = Path(args.document_path)
        settings = rst_factory.settings
        document_path = settings.relative_input_path(document_path)
        topic = Topic(rst_factory, document_path.parent)
        language = settings.language_for(args.document_path)
        document = Document(topic, document_path.name, language)
        topic.process_document(document)
    else:
        rst_factory.process_recursively()
