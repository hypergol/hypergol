import fire

from hypergol.hypergol_project import HypergolProject


def diff_data_model(commit, *args, projectDirectory='.', dryrun=None, force=None):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    project.diff_data_model(commit, *args)


if __name__ == "__main__":
    fire.Fire(diff_data_model)
