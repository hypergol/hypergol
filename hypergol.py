import logging

import fire

from hypergol.renderer import Renderer

# TODO(Rhys): move this elsewhere (ideally some kind of core library!)
root_logger = logging.getLogger('')


def log(message):
    root_logger.log(msg=message, level=logging.CRITICAL)


def create_project(projectName, targetDirectoryPath=None, expectedOutputDirectoryPath=None):
    # NOTE(Rhys): I'd build a docker image here with a mounted container so that we can compare what's created in the container to what we have on the local machine
    # For now just create in line
    log(message=f'Generating project {projectName}...')
    renderer = Renderer(templateFolderPath='src/hypergol/renderer/templates')
    renderer.render_project(projectName=projectName)
    if expectedOutputDirectoryPath:
        log(message=f'Comparing to {expectedOutputDirectoryPath}...')
        # TODO(Rhys): run diff
        pass


def create_datamodel(projectName, className, *declarations):
    # NOTE(Rhys): I'd build a docker image here with a mounted container so that we can compare what's created in the container to what we have on the local machine
    # For now just create in line
    log(message=f'Generating datamodel {className} in project {projectName}...')
    renderer = Renderer(templateFolderPath='src/hypergol/renderer/templates')
    datamodelType = renderer.pre_render_datamodel(className=className, declarations=declarations)
    renderer.render_datamodel(projectName=projectName, datamodelType=datamodelType)


if __name__ == "__main__":
    fire.Fire()
