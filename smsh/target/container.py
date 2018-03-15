from smsh.target.target import Target


class Container(Target):
    def __init__(self, instance_id, ecs_container_id):
        Target.__init__(self, instance_id)
        self.ecs_container_id = ecs_container_id

    def send_command(self, wd, command):
        raise NotImplementedError("Not yet implemented!")
