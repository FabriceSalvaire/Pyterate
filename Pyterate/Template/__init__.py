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

from jinja2 import Environment, FileSystemLoader   # PackageLoader

from . import Filters

####################################################################################################

class TemplateEnvironment:

    JINJA_EXTENSION = '.jinja2'

    ##############################################

    def __init__(self, search_path: str) -> None:
        """

        Parameters:

        search_path
             list of strings

        """
        # string or list of strings
        self._search_path = [str(x) for x in search_path]
        self._environment = Environment(
            # loader=PackageLoader('', 'templates'),
            loader=FileSystemLoader(self._search_path),

            # trim_blocks=True,
            # lstrip_blocks=True,
            # keep_trailing_newline
        )
        for function in Filters.__all__:
            self._environment.filters[function] = getattr(Filters, function)

    ##############################################

    def render(self, template: str, **kwargs) -> str:
        if template is None:
            return ''
        if not template.endswith(self.JINJA_EXTENSION):
            template += self.JINJA_EXTENSION
        jinja_template = self._environment.get_template(template)
        # if isinstance(template, str):
        #     jinja_template = self._environment.get_template(template)
        # else:
        #     raise ValueError("Wrong template {}".format(template))
        return jinja_template.render(**kwargs)

####################################################################################################

class TemplateAggregator:

    ##############################################

    def __init__(self, template_environment: TemplateEnvironment) -> None:
        self._environment = template_environment
        self._output = ''

    ##############################################

    def __str__(self) -> str:
        return self._output

    ##############################################

    @staticmethod
    def _fix_output(output: str) -> str:
        output = output.replace(' \n', '\n')
        output = output.replace('\n\n\n', '\n\n')
        return output

    ##############################################

    def _render(self, template: str, **kwargs) -> str:
        output = self._environment.render(template, **kwargs)
        output = self._fix_output(output)
        return output

    ##############################################

    def append(self, template: str, **kwargs) -> None:
        self._output += self._render(template, **kwargs)
