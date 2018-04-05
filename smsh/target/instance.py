from smsh.target.target import Target
from smsh import clients


class Instance(Target):
    DEFAULT_EXECUTION_TIMEOUT = '900'
    DEFAULT_DOCUMENT = 'AWS-RunShellScript'

    def __init__(self, instance_id):
        Target.__init__(self, instance_id)

    def send_command(self, wd, command):
        client = clients.SSM()
        resp = client.send_command(
            InstanceIds=[
                self.get_instance_id()
            ],
            DocumentName=self.DEFAULT_DOCUMENT,
            Parameters={
                'workingDirectory': [wd],
                'commands': [command],
                'executionTimeout': [self.DEFAULT_EXECUTION_TIMEOUT]
            }
        )
        return resp.get('Command', {}).get('CommandId')
