import logging

from smsh.target.target import CommandInvocationFailureException
from smsh.command import create as create_command
from smsh.command.exit import UserInitiatedExit
from smsh.session.session import Session


class EphemeralSession(Session):
    def __init__(self, *, configuration, target, command):
        Session.__init__(self, configuration=configuration, target=target)
        self.command = command

    def __enter__(self):
        logging.debug("creating temporary directory {}".format(self.session_context.get_temp_dir()))
        command = create_command(
            command="mkdir -p {temp_dir} >/dev/null && touch {sets} >/dev/null && touch {exports} >/dev/null".format(
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

        return self

    def start(self):
        try:
            user_input = self.command.strip()
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
                    pass
                except CommandInvocationFailureException as ex:
                    print(ex.stderr)
                    self.invocation.clear()
                    self.invocation = None

        except (KeyboardInterrupt, SystemExit):
            print()
