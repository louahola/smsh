# Copyright (C) Lou Ahola, HashChain Technology, Inc.
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
import os

from smsh.target.target import CommandInvocationFailureException
from smsh.command import create as create_command
from smsh.command.exit import UserInitiatedExit
from smsh.session.session import Session


class InteractiveSession(Session):
    LICENSE_STATEMENT = """Copyright (C) 2018 Lou Ahola, HashChain Technology, Inc.

This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details. """

    def __init__(self, configuration, target):
        Session.__init__(self, configuration=configuration, target=target)

    def __enter__(self):
        logging.debug("connecting to instance {}".format(self.session_context.get_temp_dir()))
        command = create_command(
            command="mkdir -p {temp_dir} && touch {sets} && touch {exports} && cat /etc/motd".format(
                temp_dir=self.session_context.get_temp_dir(),
                sets=self.session_context.get_sets_file_path(),
                exports=self.session_context.get_exports_file_path()
            ),
            buffered_output=True
        )
        self.invocation = command.invoke(
            session_context=self.session_context,
            target=self.target
        )

        print(self.LICENSE_STATEMENT)
        print("\nUser Arn: {}\n\n{}\n".format(self.iam_arn, self.target.get_details()))

        self.invocation.wait()
        self.invocation.clear()
        self.invocation = None

        return self

    def start(self):
        try:
            while True:
                user_input = input(self._get_input_prompt()).strip()

                if user_input:
                    try:
                        command = create_command(
                            command=user_input,
                            buffered_output=self.buffered_output
                        )

                        self.invocation = command.invoke(
                            session_context=self.session_context,
                            target=self.target
                        )
                        if self.invocation:
                            self.invocation.wait()

                            self.invocation.clear()
                            self.invocation = None
                    except (KeyboardInterrupt, SystemExit):
                        self.invocation.cancel()
                        self.invocation = None
                    except UserInitiatedExit:
                        break
                    except CommandInvocationFailureException as ex:
                        print(ex.stderr)
                        self.invocation.clear()
                        self.invocation = None
        except (KeyboardInterrupt, SystemExit):
            print()

    def _get_input_prompt(self):
        if self.session_context.get_user() == 'root':
            prompt_symbol = '#'
        else:
            prompt_symbol = '$'

        return "[{}@{} {}]{} ".format(
            self.session_context.get_user(),
            self.target.name,
            os.path.basename(self.session_context.get_cwd().rstrip('/')),
            prompt_symbol
        )
