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

from smsh.command.command import Command
from smsh.command.command import CommandInvocation


class UnbufferedCommandInvocation(CommandInvocation):
    CWD_REGEX = re.compile("\n?{{pwd:(\S+?)}}")
    EXIT_CODE_REGEX = re.compile("\n?{{exit_code:(\S+?)}}")
    USER_REGEX = re.compile("\n?{{whoami:(\S+?)}}")
    TRAILING_NEWLINE = re.compile("\n?$")

    LOG_FILENAME = 'command.log'
    LATEST_LOG_FILENAME = 'latest.log'
    PREVIOUS_LOG_LINE_FILENAME = 'previous.line'
    OUTPUT_BUFFER_FILENAME = 'output.buffer'

    def __init__(self, command, session_context, target):
        CommandInvocation.__init__(self)
        self.session_context = session_context
        self.target = target

        command = (
            "{directory_setup} &&"
            # "{user_setup} &&"
            # " {environment_setup} &&"
            " {logging_setup} &&"
            " {command} &&"
            # " {env_return} &&"
            " {cwd_return} &&"
            " {user_return}"
        ).format(
            directory_setup=self._get_directory_setup(),
            user_setup=self._get_user_setup(),
            environment_setup=self._get_env_setup(),
            logging_setup=self._get_logging_setup(),
            command=self._get_command_setup(command),
            env_return=self._get_env_return(),
            cwd_return=self._get_cwd_return(),
            user_return=self._get_user_return()
        )

        self.invocation_id = target.send_command(self.session_context.get_cwd(), command)
        self.output_invocation_id = None

    def _get_log_path(self):
        return "{}/{}".format(self.session_context.get_temp_dir(), self.LOG_FILENAME)

    def _get_latest_log_path(self):
        return "{}/{}".format(self.session_context.get_temp_dir(), self.LATEST_LOG_FILENAME)

    def _get_previous_log_line_path(self):
        return "{}/{}".format(self.session_context.get_temp_dir(), self.PREVIOUS_LOG_LINE_FILENAME)

    def _get_output_buffer_path(self):
        return "{}/{}".format(self.session_context.get_temp_dir(), self.OUTPUT_BUFFER_FILENAME)

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

    def _get_logging_setup(self):
        return "touch {} && echo 0 > {}".format(
            self._get_log_path(),
            self._get_previous_log_line_path()
        )

    def _get_command_setup(self, command):
        return "{{ {command}; echo {{{{exit_code:$?}}}}; }} >{log_file} 2>&1 || true".format(
            command=command,
            log_file=self._get_log_path()
        )

    def _get_env_return(self):
        return "set > {} && env > {}".format(
            self.session_context.get_sets_file_path(),
            self.session_context.get_exports_file_path()
        )

    def _get_cwd_return(self):
        return "echo {{{{pwd:$(pwd)}}}} >> {log}".format(log=self._get_log_path())

    def _get_user_return(self):
        return "echo {{{{whoami:$(whoami)}}}} >> {log}".format(log=self._get_log_path())

    def wait(self):
        exit_cwd = None
        exit_code = None
        exit_user = None

        while not exit_cwd or not exit_code or not exit_user:
            output = self.get_output()

            cwd_matches = re.search(self.CWD_REGEX, output)
            exit_code_matches = re.search(self.EXIT_CODE_REGEX, output)
            user_matches = re.search(self.USER_REGEX, output)

            if cwd_matches:
                exit_cwd = cwd_matches.group(1)
                output = re.sub(self.CWD_REGEX, "", output)
            if exit_code_matches:
                exit_code = exit_code_matches.group(1)
                output = re.sub(self.EXIT_CODE_REGEX, "", output)
            if user_matches:
                exit_user = user_matches.group(1)
                output = re.sub(self.USER_REGEX, "", output)

            output = re.sub(self.TRAILING_NEWLINE, "", output)

            if output:
                logging.getLogger('command_output').info(output)

        self.session_context.set_cwd(exit_cwd)
        self.session_context.set_user(exit_user)
        self.session_context.set_exit_code(exit_code)

    def get_output(self):
        cmd = (
            "if [ -e \"{log}\" ]; then cp {log} {latest_log} &&"
            " tail -n $(expr $(cat {latest_log} | wc -l) - $(cat {previous_line})) {latest_log} >> {output_buffer} &&"
            " echo $(cat {latest_log} | wc -l) > {previous_line} &&"
            " rm {latest_log} &&"
            " head -n 100 {output_buffer} &&"
            " sed -i -e '1,100d' {output_buffer}; fi"
        ).format(
            log=self._get_log_path(),
            latest_log=self._get_latest_log_path(),
            previous_line=self._get_previous_log_line_path(),
            output_buffer=self._get_output_buffer_path()
        )

        self.output_invocation_id = self.target.send_command(self.session_context.get_cwd(), cmd)
        output = self.target.wait_for_output(self.output_invocation_id)
        self.output_invocation_id = None

        return output

    def cancel(self):
        self.target.cancel_command(self.invocation_id)
        self.target.cancel_command(self.output_invocation_id)
        self.clear()

    def clear(self):
        self.invocation_id = None
        self.output_invocation_id = None


class UnbufferedCommand(Command):
    def __init__(self, command):
        self.command = command

    def invoke(self, session_context, target):
        return UnbufferedCommandInvocation(
            command=self.command,
            session_context=session_context,
            target=target
        )
