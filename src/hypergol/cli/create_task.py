import fire

from hypergol.utils import Mode
from hypergol.utils import get_mode

from hypergol.cli.task_creator import TaskCreator


def create_task(className, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    taskCreator = TaskCreator(taskType='Task', mode=get_mode(mode, dryrun, force))
    return taskCreator.create(className, *args, projectDirectory=projectDirectory)


if __name__ == "__main__":
    fire.Fire(create_task)
