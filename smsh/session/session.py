import datetime

from smsh import clients


class SessionConfiguration(object):
    def __init__(self, *, buffered_output, environment_variables, user, working_directory):
        self.buffered_output = buffered_output
        self.environment_variables = environment_variables
        self.user = user
        self.working_directory = working_directory


class SessionContext(object):
    EXPORTS_FILE_NAME = 'exports'
    SETS_FILE_NAME = 'sets'

    def __init__(self, *, temp_dir, user='root', working_directory):
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
        self.buffered_output = configuration.buffered_output

        self.target = target
        self.iam_arn = clients.STS().get_caller_identity()['Arn']

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
        raise NotImplementedError("Override this method!")

    def start(self):
        raise NotImplementedError("Override this method!")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.invocation:
            self.invocation.cancel()
