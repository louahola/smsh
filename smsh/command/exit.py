from smsh.command.command import Command


class UserInitiatedExit(Exception):
    pass


class ExitCommand(Command):
    def invoke(self, *, session_context, target):
        raise UserInitiatedExit()
