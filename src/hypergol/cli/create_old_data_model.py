import fire

from hypergol.hypergol_project import HypergolProject


def create_old_data_model(commit, *args, projectDirectory='.', dryrun=None, force=None):
    """Create an older version of a data model class from git

    Please see :func:`~hypergol.hypergol_project.HypergolProject.create_old_data_model` in :class:`HypergolProject` for details.

    """
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    project.create_old_data_model(commit, *args)


if __name__ == "__main__":
    fire.Fire(create_old_data_model)
