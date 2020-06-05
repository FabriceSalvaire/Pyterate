####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2017 Fabrice Salvaire
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
#
# Forked code from Pweave
#   a scientific report generator and a literate programming tool for Python
#   Copyright (C) Matti Pastell and contributors
#   https://github.com/mpastell/Pweave
#   commit b27be64014a9497a8241de9c22246c8934c115cb
#   pweave/processors/jupyter.py sha1sum e0b11fdf837c43242e9d52633771ca178902c483
#
####################################################################################################

####################################################################################################

from queue import Empty
import base64
import logging
import os

from jupyter_client import KernelManager
import nbformat.v4 as nbformat_v4

####################################################################################################

_module_logger = logging.getLogger(__name__)

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

class JupyterOutput:

    ##############################################

    def __init__(self, notebook_node):

        self._node = notebook_node

    ##############################################

    @property
    def node(self):
        return self._node

    @property
    def output_type(self):
        return self._node.output_type

    @property
    def is_error(self):
        return self.output_type == 'error'

    @property
    def is_result(self):
        return self.output_type == 'execute_result'

    @property
    def is_display_data(self):
        return self.output_type == 'display_data'

    @property
    def is_stream(self):
        return self.output_type == 'stream'

    ##############################################

    @property
    def result(self):
        if self.is_result:
            return self._node.data['text/plain']
        else:
            return None

    @property
    def image(self):
        if self.is_display_data:
            return self._node.data['image/png']
        else:
            return None

    ##############################################

    def __str__(self):

        if self.is_error:
            traceback = '\n'.join(self._node.traceback)
            return "{0.ename} {0.evalue}\n{1}".format(self._node, traceback)
        elif self.is_stream:
            return self._node.text
        elif self.is_result:
            return self._node.data['text/plain']
        elif self.is_display_data:
            # Fixme: other cases
            return self._node.data['image/png']

    ##############################################

    def write_image(self, path):

        image = self.image
        if image is None:
            raise NameError("This node don't have an image")

        with open(path, 'wb') as fh:
            fh.write(base64.b64decode(image))

####################################################################################################

class JupyterOutputs(list):
    pass

####################################################################################################

class JupyterClient:

    _logger = _module_logger.getChild('JupyterClient')

    TIMEOUT = None

    ##############################################

    def __init__(self, working_directory, kernel='python3'):

        self._kernel_manager = KernelManager(kernel_name=kernel)

        stderr = open(os.devnull, 'w')
        self._kernel_manager.start_kernel(cwd=working_directory, stderr=stderr)

        self._init_client()

    ##############################################

    def __del__(self):
        self.close()

    ##############################################

    def _init_client(self):

        self._kernel_client = self._kernel_manager.client()
        self._kernel_client.start_channels()
        try:
            self._kernel_client.wait_for_ready()
        except RuntimeError:
            self._logger.error('Timeout from starting kernel')
            # \nTry restarting python session and running again
            self._kernel_client.stop_channels()
            self._kernel_manager.shutdown_kernel()
            raise

        self._kernel_client.allow_stdin = False

    ##############################################

    def close(self):
        self._logger.info('Stop kernel')
        # self._kernel_client.stop_channels() # Fixme: block ??? not documented ???
        self._kernel_manager.shutdown_kernel(now=True)

    ##############################################

    def restart(self):

        self._logger.info('Restart kernel')

        # self._kernel_client.shutdown(restart=True) # ???

        # self._kernel_client.stop_channels()
        self._kernel_manager.restart_kernel(now=False) # 1s to cleanup
        # do we have to sleep ???
        self._init_client()

    ##############################################

    @staticmethod
    def message_id_match(message, message_id):
        return message['parent_header'].get('msg_id') == message_id

    ##############################################

    def _wait_for_finish(self, message_id):

        """Wait for finish, with timeout"""

        # self._logger.debug('wait for finish, with timeout')

        while True:
            try:
                # Get a message from the shell channel
                message = self._kernel_client.get_shell_msg(timeout=self.TIMEOUT)
                # self._logger.debug('message {}'.format(message))
            except Empty:
                # if self._interrupt_on_timeout:
                #     self._kernel_manager.interrupt_kernel()
                #     break
                raise TimeoutError('Cell execution timed out') # , see log for details.

            if self.message_id_match(message, message_id):
                break
            else:
                # not our reply
                continue

        # self._logger.debug('wait for finish done')

    ##############################################

    def run_cell(self, source):

        """Execute the source.

        Return a list of :class:`nbformat.NotebookNode` instance.
        """

        source = source.lstrip()

        cell = {}
        cell['source'] = source
        message_id = self._kernel_client.execute(source, store_history=False)
        # self._logger.debug('message_id {}'.format(message_id))

        self._wait_for_finish(message_id)

        outputs = JupyterOutputs()
        while True:
            try:
                # We've already waited for execute_reply, so all output should already be
                # waiting. However, on slow networks, like in certain CI systems, waiting < 1 second
                # might miss messages.  So long as the kernel sends a status:idle message when it
                # finishes, we won't actually have to wait this long, anyway.
                message = self._kernel_client.iopub_channel.get_msg(block=True, timeout=4)
                # self._logger.debug('message {}'.format(message))
            except Empty:
                self._logger.error('Timeout waiting for IOPub output')
                # \nTry restarting python session and running weave again
                raise RuntimeError('Timeout waiting for IOPub output')
            # stdout from InProcessKernelManager has no parent_header
            if not self.message_id_match(message, message_id) and message['msg_type'] != 'stream':
                continue

            message_type = message['msg_type']
            content = message['content']
            # self._logger.debug('msg_type {}'.format(message_type))
            # self._logger.debug('content {}'.format(content))

            # set the prompt number for the input and the output
            if 'execution_count' in content:
                cell['execution_count'] = content['execution_count']

            if message_type == 'status':
                if content['execution_state'] == 'idle':
                    break
                else:
                    continue
            elif message_type == 'execute_input':
                continue
            elif message_type == 'clear_output':
                outputs = JupyterOutputs()
                continue
            elif message_type.startswith('comm'):
                continue

            try:
                output = nbformat_v4.output_from_msg(message)
            except ValueError:
                self._logger.error('unhandled iopub message: {}'.format(message_type))
            else:
                outputs.append(JupyterOutput(output))

        return outputs
