# Copyright (C) 2018 Lou Ahola, HashChain Technology, Inc.
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

import logging
from subprocess import call
import tempfile

from smsh.command.command import Command, CommandInvocation
from smsh.target.target import CommandInvocationFailureException


class EditorCommandInvocation(CommandInvocation):
    def __init__(self, file, ide, session_context, target):
        CommandInvocation.__init__(self)
        self.file = file
        self.ide = ide
        self.session_context = session_context
        self.target = target

        self.invocation_id = target.send_command(self.session_context.get_cwd(), "cat {} 2>&1".format(file))

    def wait(self):
        input_contents = ""
        try:
            input_contents = self.target.wait_for_output(self.invocation_id)
        except CommandInvocationFailureException as ex:
            if ex.stdout.rstrip().endswith("No such file or directory"):
                logging.debug("no file found. creating new file")
                pass
            else:
                raise ex

        self.invocation_id = None

        with tempfile.NamedTemporaryFile(suffix='.tmp') as tf:
            tf.write(input_contents.encode('utf-8'))
            tf.flush()

            call([self.ide, "+set backupcopy=yes", tf.name])
            tf.flush()

            tf.seek(0)
            output_contents = tf.read().decode()

        logging.debug("output contents: {}".format(output_contents))
        if input_contents != output_contents:
            logging.debug("file changes found. updating file")
            command = (
                "(\n"
                "cat <<'--EOF--'\n"
                "{contents}\n"
                "--EOF--\n"
                ") > {destination}"
            ).format(
                contents=output_contents,
                destination=self.file
            )
            self.invocation_id = self.target.send_command(
                self.session_context.get_cwd(),
                command
            )
            output = self.target.wait_for_output(self.invocation_id)
            if output:
                logging.getLogger('command_output').info(output)

        self.clear()

        return self.session_context

    def cancel(self):
        self.target.cancel_command(self.invocation_id)
        self.clear()

    def clear(self):
        self.invocation_id = None


class EditorCommand(Command):
    def __init__(self, ide, file):
        self.ide = ide
        self.file = file

    def invoke(self, session_context, target):
        return EditorCommandInvocation(
            file=self.file,
            ide=self.ide,
            session_context=session_context,
            target=target
        )
