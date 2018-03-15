class Command(object):
    def invoke(self, *, session_context, target):
        raise NotImplementedError("Overwrite This Method!")


class CommandInvocation(object):
    def __init__(self):
        pass

    def wait(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
