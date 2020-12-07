import fire

from hypergol.hypergol_project import HypergolProject


def list_datasets(dataDirectory, projectDirectory='.', pattern=None):
    """Convenience function to list existing datasets in the project

    Parameters
    ----------
    dataDirectory : string
        location of the project data
    projectDirectory : string (default ``.``)
        location of the data directory


    Please see :func:`~hypergol.hypergol_project.HypergolProject.list_datasets` in :class:`HypergolProject` for details.

    """
    project = HypergolProject(projectDirectory=projectDirectory, dataDirectory=dataDirectory, dryrun=False, force=False)
    project.list_datasets(pattern=pattern, asCode=True)


if __name__ == "__main__":
    fire.Fire(list_datasets)
