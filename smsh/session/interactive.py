import logging
import os

from smsh.target.target import CommandInvocationFailureException
from smsh.command import create as create_command
from smsh.command.exit import UserInitiatedExit
from smsh.session.session import Session


class InteractiveSession(Session):
    def __init__(self, *, configuration, target):
        Session.__init__(self, configuration=configuration, target=target)

    def __enter__(self):
        logging.debug("creating temporary directory {}".format(self.session_context.get_temp_dir()))
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

        self.invocation.wait()
        self.invocation.clear()
        self.invocation = None

        print("\nUser Arn: {}\n\n{}\n".format(self.iam_arn, self.target.get_details()))

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
