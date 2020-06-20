import argparse
import logging

# TODO(Rhys): move this elsewhere (ideally some kind of core library!)
root_logger = logging.getLogger('')

def log(message):
    root_logger.log(msg=message, level=logging.CRITICAL)


def generate_project(projectDescriptionFilePath, expectedOutputDirectoryPath=None):
    # NOTE(Rhys): I'd build a docker image here with a mounted container so that we can compare what's generated in the container to what we have on the local machine
    # For now just generate in line

    # Generate project
    log(message=f'Generating {projectDescriptionFilePath}...')

    if expectedOutputDirectoryPath:
        log(message=f'Comparing to {expectedOutputDirectoryPath}...')
        # TODO(Rhys): run diff
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # TODO(Rhys): Better describe these once I understand them!
    # TODO(Rhys): Currently we are generating these in line - I would suggest that we build docker images with the project and output projects for consistency across OS versions
    parser.add_argument('-t', '--generate', type=str, help='The file with information about the project to build')
    parser.add_argument('-e', '--excepted-output-directory', type=str, help='The directory containing the project we expect to generate')
    args = parser.parse_args()
    if not args.generate:
        raise Exception('Generate flag must be provided with a target')
    generate_project(projectDescriptionFilePath=args.generate, expectedOutputDirectoryPath=args.excepted_output_directory)