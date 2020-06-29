from pathlib import Path
import fire
from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_project(projectName, dryrun=None, force=None):
    projectName = NameString(projectName)
    project = HypergolProject(projectName=projectName, projectDirectory=projectName.asSnake, dryrun=dryrun, force=force)
    project.create_project_directory()
    project.create_data_models_directory()
    project.create_tasks_directory()
    project.create_pipelines_directory()
    project.create_tests_directory()
    project.render_executable(templateName='make_venv.sh.j2', templateData={}, filePath=Path(project.projectDirectory, 'make_venv.sh'))
    project.render_executable(templateName='run_tests.sh.j2', templateData={}, filePath=Path(project.projectDirectory, 'run_tests.sh'))
    project.render_executable(templateName='run_pylint.sh.j2', templateData={}, filePath=Path(project.projectDirectory, 'run_pylint.sh'))
    project.render_simple(templateName='requirements.txt.j2', filePath=Path(project.projectDirectory, 'requirements.txt'))
    project.render_simple(templateName='.gitignore.j2', filePath=Path(project.projectDirectory, '.gitignore'))
    project.render_simple(templateName='README.md.j2', filePath=Path(project.projectDirectory, 'README.md'))
    project.render_simple(templateName='pylintrc.j2', filePath=Path(project.projectDirectory, 'pylintrc'))

    print('')
    print(f'Project {projectName} was created in directory {projectName.asSnake}.{project.modeMessage}')
    print('')


if __name__ == "__main__":
    fire.Fire(create_project)
