import datetime
import logging
import os

from smsh import clients
from smsh.target.target import CommandInvocationFailureException
from smsh.command import create as create_command
from smsh.command.exit import UserInitiatedExit


class SessionConfiguration(object):
    def __init__(self, *, buffered_output, command, environment_variables, user, working_directory):
        self.buffered_output = buffered_output
        self.command = command
        self.environment_variables = environment_variables
        self.user = user
        self.working_directory = working_directory


class SessionContext(object):
    EXPORTS_FILE_NAME = "exports"
    SETS_FILE_NAME = "sets"

    def __init__(self, *, temp_dir, user="root", working_directory):
        self.__temp_dir = temp_dir
        self.__user = user
        self.__cwd = working_directory

    def get_cwd(self):
        return self.__cwd

    def set_cwd(self, cwd):
        self.__cwd = cwd

    def get_temp_dir(self):
        return self.__temp_dir

    def get_sets_file_path(self):
        return "{}/{}".format(self.__temp_dir, self.SETS_FILE_NAME)

    def get_exports_file_path(self):
        return "{}/{}".format(self.__temp_dir, self.EXPORTS_FILE_NAME)

    def get_user(self):
        return self.__user

    def set_user(self, user):
        self.__user = user


class Session(object):
    def __init__(self, *, configuration, target):
        self.command = configuration.command
        self.buffered_output = configuration.buffered_output

        self.target = target
        self.iam_arn = clients.STS().get_caller_identity()["Arn"]

        epoch = datetime.datetime.utcfromtimestamp(0)
        now = datetime.datetime.utcnow()
        timestamp = (now - epoch).total_seconds()
        self.session_id = "{}-{}".format(self.iam_arn, timestamp)

        self.session_context = SessionContext(
            temp_dir="/tmp/smsh/{}".format(self.session_id),
            working_directory=configuration.working_directory
        )

        self.invocation = None

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
                if self.command:
                    user_input = self.command.strip()
                else:
                    user_input = input(self.get_input_prompt()).strip()

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

                if self.command:
                    break
        except (KeyboardInterrupt, SystemExit):
            print()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.invocation:
            self.invocation.cancel()

    def get_input_prompt(self):
        if self.session_context.get_user() == "root":
            prompt_symbol = "#"
        else:
            prompt_symbol = "$"

        return "[{}@{} {}]{} ".format(
            self.session_context.get_user(),
            self.target.name,
            os.path.basename(self.session_context.get_cwd().rstrip("/")),
            prompt_symbol
        )
