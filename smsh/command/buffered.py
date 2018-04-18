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
import re

from smsh.command.command import Command, CommandInvocation


class BufferedCommandInvocation(CommandInvocation):
    CWD_REGEX = re.compile("\n?{{pwd:(\S+?)}}")
    EXIT_CODE_REGEX = re.compile("\n?{{exit_code:(\S+?)}}")
    USER_REGEX = re.compile("\n?{{whoami:(\S+?)}}")
    TRAILING_NEWLINE = re.compile("\n?$")

    def __init__(self, command, session_context, target):
        CommandInvocation.__init__(self)
        self.session_context = session_context
        self.target = target

        command = (
            "{directory_setup} &&"
            # "{user_setup} &&"
            # " {environment_setup} &&"
            " {{ {command}; echo {{{{exit_code:$?}}}}; }} 2>&1 || true &&"
            # " {env_return} &&"
            " {cwd_return} &&"
            " {user_return}"
        ).format(
            directory_setup=self._get_directory_setup(),
            user_setup=self._get_user_setup(),
            environment_setup=self._get_env_setup(),
            command=command,
            env_return=self._get_env_return(),
            cwd_return=self._get_cwd_return(),
            user_return=self._get_user_return()
        )

        self.invocation_id = target.send_command(self.session_context.get_cwd(), command)

    def _get_directory_setup(self):
        return "mkdir -p {temp_dir} && touch {sets} && touch {exports}".format(
            temp_dir=self.session_context.get_temp_dir(),
            sets=self.session_context.get_sets_file_path(),
            exports=self.session_context.get_exports_file_path()
        )

    def _get_user_setup(self):
        return "su - {user} >/dev/null 2>&1".format(
            user=self.session_context.get_user()
        )

    def _get_env_setup(self):
        return ("source {sets} >/dev/null 2>&1 &&"
                " set -a >/dev/null 2>&1 &&"
                " source {exports} >/dev/null 2>&1 &&"
                " set +a >/dev/null 2>&1"
                ).format(
            sets=self.session_context.get_sets_file_path(),
            exports=self.session_context.get_exports_file_path()
        )

    def _get_env_return(self):
        return "set > {} && env > {}".format(
            self.session_context.get_sets_file_path(),
            self.session_context.get_exports_file_path()
        )

    @staticmethod
    def _get_cwd_return():
        return "echo {{pwd:$(pwd)}}"

    @staticmethod
    def _get_user_return():
        return "echo {{whoami:$(whoami)}}"

    def wait(self):
        output = self.target.wait_for_output(self.invocation_id)

        matches = re.search(self.CWD_REGEX, output)
        if matches:
            exit_cwd = matches.group(1)
            output = re.sub(self.CWD_REGEX, "", output)
            self.session_context.set_cwd(exit_cwd)
        else:
            logging.error("No working directory found!")

        matches = re.search(self.EXIT_CODE_REGEX, output)
        if matches:
            exit_code = matches.group(1)
            output = re.sub(self.EXIT_CODE_REGEX, "", output)
            self.session_context.set_exit_code(exit_code)
        else:
            logging.error("No exit code found!")

        matches = re.search(self.USER_REGEX, output)
        if matches:
            exit_user = matches.group(1)
            output = re.sub(self.USER_REGEX, "", output)
            self.session_context.set_user(exit_user)
        else:
            logging.error("No user found!")

        output = re.sub(self.TRAILING_NEWLINE, "", output)

        if output:
            logging.getLogger('command_output').info(output)

    def cancel(self):
        self.target.cancel_command(self.invocation_id)
        self.clear()

    def clear(self):
        self.invocation_id = None


class BufferedCommand(Command):
    def __init__(self, command):
        self.command = command

    def invoke(self, session_context, target):
        return BufferedCommandInvocation(
            command=self.command,
            session_context=session_context,
            target=target
        )
