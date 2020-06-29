from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_pipeline(pipeLineName, *args, projectDirectory='.', dryrun=None, force=None):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    pipeLineName = NameString(pipeLineName)
    dependencies = [NameString(value) for value in args]
    project.check_dependencies(dependencies)

    content = project.render(
        templateName='pipeline.py.j2',
        templateData={
            'snakeName': pipeLineName.asSnake,
            'taskDependencies': [name for name in dependencies if project.is_task_class(name)],
            'dataModelDependencies': [name for name in dependencies if project.is_data_model_class(name)]
        },
        filePath=Path(projectDirectory, 'pipelines', pipeLineName.asFileName)
    )

    scriptContent = project.render_executable(
        templateName='pipeline.sh.j2',
        templateData={'snakeName': pipeLineName.asSnake},
        filePath=Path(projectDirectory, f'{pipeLineName.asSnake}.sh')
    )

    print('')
    print(f'PipeLine {pipeLineName.asSnake} was created in directory {project.pipelinesPath}.{project.modeMessage}')
    print('')
    if project.isDryRun:
        return content, scriptContent
    return None


if __name__ == "__main__":
    fire.Fire(create_pipeline)
