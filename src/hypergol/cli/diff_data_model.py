import fire

from hypergol.hypergol_project import HypergolProject


def diff_data_model(commit, *args, projectDirectory='.', dryrun=None, force=None):
    """Convenience function to compare old data model class definitions to the current one

    Please see :func:`~hypergol.hypergol_project.HypergolProject.diff_data_model` in :class:`HypergolProject` for details.

    """
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    project.diff_data_model(commit, *args)


if __name__ == "__main__":
    fire.Fire(diff_data_model)
