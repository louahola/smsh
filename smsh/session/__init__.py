from smsh.session.interactive import InteractiveSession
from smsh.session.ephemeral import EphemeralSession


def create(configuration, target, command):
    if command:
        return EphemeralSession(configuration=configuration, target=target, command=command)
    else:
        return InteractiveSession(configuration=configuration, target=target)
