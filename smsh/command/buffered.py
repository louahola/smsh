import logging
import re

from smsh.command.command import Command, CommandInvocation


class BufferedCommandInvocation(CommandInvocation):
    CWD_REGEX = re.compile("\n?{{pwd:(\S+?)}}")
    USER_REGEX = re.compile("\n?{{whoami:(\S+?)}}")

    def __init__(self, *, command, session_context, target):
        CommandInvocation.__init__(self)
        self.session_context = session_context
        self.target = target

        command = (
            # "{user_setup} &&"
            # " {environment_setup} &&"
            " {command} &&"
            # " {env_return} &&"
            " {cwd_return} &&"
            " {user_return}"
        ).format(
            user_setup=self.__get_user_setup(),
            environment_setup=self.__get_env_setup(),
            command=command,
            env_return=self.__get_env_return(),
            cwd_return=self.__get_cwd_return(),
            user_return=self.__get_user_return()
        )

        self.invocation_id = target.send_command(self.session_context.get_cwd(), command)

    def __get_user_setup(self):
        return "su - {user} >/dev/null 2>&1".format(
            user=self.session_context.get_user()
        )

    def __get_env_setup(self):
        return ("source {sets} >/dev/null 2>&1 &&"
                " set -a >/dev/null 2>&1 &&"
                " source {exports} >/dev/null 2>&1 &&"
                " set +a >/dev/null 2>&1"
                ).format(
            sets=self.session_context.get_sets_file_path(),
            exports=self.session_context.get_exports_file_path()
        )

    def __get_env_return(self):
        return "set > {} && env > {}".format(
            self.session_context.get_sets_file_path(),
            self.session_context.get_exports_file_path()
        )

    @staticmethod
    def __get_cwd_return():
        return "echo {{pwd:$(pwd)}}"

    @staticmethod
    def __get_user_return():
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

        matches = re.search(self.USER_REGEX, output)
        if matches:
            exit_user = matches.group(1)
            output = re.sub(self.USER_REGEX, "", output)
            self.session_context.set_user(exit_user)
        else:
            logging.error("No user found!")

        if output:
            print(output)

    def cancel(self):
        self.target.cancel_command(self.invocation_id)
        self.clear()

    def clear(self):
        self.invocation_id = None


class BufferedCommand(Command):
    def __init__(self, command):
        self.command = command

    def invoke(self, *, session_context, target):
        return BufferedCommandInvocation(
            command=self.command,
            session_context=session_context,
            target=target
        )
