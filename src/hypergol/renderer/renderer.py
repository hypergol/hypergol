import os
import stat
import shutil
import re

from jinja2 import Environment
from jinja2 import FileSystemLoader

from hypergol.model import DataModelType
from hypergol.model import Member
from hypergol.model import Project


BUILTIN_TYPES = {'str', 'int'}


class Renderer:

    def __init__(self, templateFolderPath):
        self.templateFolderPath = templateFolderPath
        self.jinjaEnvironment = Environment(loader=FileSystemLoader(searchpath=self.templateFolderPath))

    # TODO(Rhys): These util functions are weird to have here - this should just be a list of render_* methods
    @staticmethod
    def make_file_executable(filePath):
        fileStat = os.stat(filePath)
        if os.getuid() == fileStat.st_uid:
            os.chmod(filePath, fileStat.st_mode | stat.S_IXUSR)

    @staticmethod
    def get_filename(className, withExtension=True):
        fileName = re.sub(r'([a-z])([A-Z])', r'\1_\2', className).lower()
        if withExtension:
            fileName += '.py'
        return fileName

    # TODO(Rhys): This needs to move elsewhere - I need to think about the project structure
    def pre_render_datamodel(self, className, declarations):
        members = []
        dependencies = []
        doAddList: bool = False
        for declaration in declarations:
            splitDeclaration = declaration.split(':')
            if len(splitDeclaration) != 2:
                raise Exception(f'Found declaration that doesn\'t match the format "name:type" - {declaration}')
            name, strType_ = splitDeclaration
            # TODO(Laszlo): handle Dicts if needed at all
            type_ = next(iter(re.findall(r'^List\[(.+)\]$', strType_)), None)
            member = Member(name=name, type=strType_)
            if type_ is not None:
                doAddList = True
                member.isList = True
                member.innerType = type_
            else:
                type_ = strType_
            # TODO(Laszlo): maybe importlib.util.find_spec can solve this nicer
            if os.path.exists(f'datamodel/{type_.lower()}.py'):
                importName = self.get_filename(type_, withExtension=False)
                self.dependencies.append({'importName': importName, 'name': type_})
                member.needConversion = True
            elif type_ not in BUILTIN_TYPES:
                raise ValueError(f'Unknown type: {type_} must be in {BUILTIN_TYPES} or in datamodel')
            members.append(member)
        return DataModelType(name=className, doAddList=doAddList, dependencies=dependencies, members=members)

    def render_datamodel(self, projectName, datamodelType):
        template = self.jinjaEnvironment.get_template(name='datamodel/datamodel.py.j2')
        with open(f'{projectName}/datamodel/{self.get_filename(datamodelType.name)}', 'w+') as f:
            f.write(template.render(datamodelType=datamodelType) + '\n')

    def render_readme(self, project):
        template = self.jinjaEnvironment.get_template(name='README.md.j2')
        with open(f'{project.name}/README.md', 'wt') as f:
            f.write(template.render(project=project))

    def render_directory(self, templateDirectoryPath, outputDirectoryPath, jinjaVariables):
        for path, _, files in os.walk(os.path.join(self.templateFolderPath), templateDirectoryPath):
            templateRelativePath = path.replace(self.templateFolderPath, '')
            for filename in files:
                tempaltePath = os.path.join(templateRelativePath, filename)
                template = self.jinjaEnvironment.get_template(name=tempaltePath)
                if filename.endswith('.j2'):
                    targetFilePath = os.path.join(outputDirectoryPath, filename[:3])
                    with open(targetFilePath, 'w+') as targetFile:
                        targetFile.write(template.render(**jinjaVariables))
                else:
                    raise Exception('All templates must end in .j2')


    def render_project(self, projectName):
        project = Project(name=projectName)
        if os.path.exists(project.name):
            raise ValueError(f'directory {project.name} already exist!')
        os.mkdir(project.name)

        # TODO(Laszlo): datasets??, models, deploys at the respective command
        directories = [
            'datamodel',
            'tasks',
            'pipelines',
            'scripts',
            'tests',
        ]
        for directory in directories:
            os.mkdir(f'{project.name}/{directory}')
        self.render_directory(templateDirectoryPath='project', outputDirectoryPath=project.name, jinjaVariables={'project': project})
        # shutil.copy(f'{self.templateFolderPath}/requirements.txt', f'{project.name}/requirements.txt')
        # shutil.copy(f'{self.templateFolderPath}/.gitignore', f'{project.name}/.gitignore')
        # shutil.copy(f'{self.templateFolderPath}/makevenv.sh', f'{project.name}/makevenv.sh')
        # self.make_file_executable(f'{project.name}/makevenv.sh')
        # self.render_readme(project=project)
