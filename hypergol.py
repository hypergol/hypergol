import logging

import fire

from hypergol.renderer import Renderer

# TODO(Rhys): move this elsewhere (ideally some kind of core library!)
root_logger = logging.getLogger('')

def log(message):
    root_logger.log(msg=message, level=logging.CRITICAL)


def generate_project(projectName, targetDirectoryPath=None, expectedOutputDirectoryPath=None):
    # NOTE(Rhys): I'd build a docker image here with a mounted container so that we can compare what's generated in the container to what we have on the local machine
    # For now just generate in line

    # Generate project
    log(message=f'Generating {projectName}...')
    renderer = Renderer(templateFolderPath='src/hypergol/render/templates')
    render.render_project(projectName=projectName)

    if expectedOutputDirectoryPath:
        log(message=f'Comparing to {expectedOutputDirectoryPath}...')
        # TODO(Rhys): run diff
        pass

def generate_datamodel(className, *declarations, targetDirectoryPath=None, expectedOutputDirectoryPath=None):
    # NOTE(Rhys): I'd build a docker image here with a mounted container so that we can compare what's generated in the container to what we have on the local machine
    # For now just generate in line

    # Generate project
    log(message=f'Generating {projectName}...')
    renderer = Renderer(templateFolderPath='src/hypergol/render/templates')
    datamodelType = renderer.pre_render_datamodel(className, *declarations)
    render.render_datamodel(datamodelType=datamodelType)

    if expectedOutputDirectoryPath:
        log(message=f'Comparing to {expectedOutputDirectoryPath}...')
        # TODO(Rhys): run diff
        pass


if __name__ == "__main__":
    fire.Fire(generate_project)
    fire.Fire(generate_project)
    fire.Fire(generate_project)
