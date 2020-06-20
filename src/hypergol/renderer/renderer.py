from jinja2 import Enviroment
from jinja2 import FileSystemLoader

from  hypergol.model import Member
from  hypergol.model import DataModelType


BUILTIN_TYPES = {'str', 'int'}


class Render:

    def __init__(self, templateFolderPath):
        self.templateFolderPath = templateFolderPath
        self.jinjaEnviroment = Enviroment(loader=FileSystemLoader(searchpath=self.templateFolderPath))

    # TODO(Rhys): These util functions are weird to have here - this should just be a list of render_* methods
    @staticmethod
    def make_file_executable(filePath):
        fileStat = os.stat(filePath)
        if os.getuid() == fileStat.st_uid:
            os.chmod(filePath, fileStat.st_mode | stat.S_IXUSR)

    def get_filename(className, withExtension=True):
        fileName = re.sub(r'([a-z])([A-Z])', r'\1_\2', className).lower()
        if withExtension:
            fileName += '.py'
        return fileName

    # TODO(Rhys): This needs to move elsewhere - I need to think about the project structure
    def pre_render_datamodel(className, *declarations):
        members = []
        dependencies = []
        doAddList: bool = False
        for declaration in declarations:
            name, strType_ = declaration.split(':')
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
                importName = get_filename(type_, withExtension=False)
                self.dependencies.append({'importName': importName, 'name': type_})
                member.needConversion = True
            elif type_ not in BUILTIN_TYPES:
                raise ValueError(f'Unknown type: {type_} must be in {BUILTIN_TYPES} or in datamodel')
            members.append(member)
            datamodelType.add_member(declaration=declaration)
        datamodelType = DataModelType(name=className, doAddList=doAddList, dependencies=dependencies, members=members)
        self.render_datamodel(datamodelType=datamodelType)

    def render_datamodel(self, datamodelType):
        template = self.jinjaEnviroment.get_template(name='datamodel/datamodel.py.j2')
        with open(f'datamodel/{get_filename(datamodelType.name)}', 'wt') as f:
            f.write(template.render(datamodelType=datamodelType) + '\n')

    def render_readme(self, project):
        template = self.jinjaEnviroment.get_template(name='README.md.j2')
        with open(f'{project.name}/README.md', 'wt') as f:
            f.write(template.render(project=project))

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
        shutil.copy(f'{self.templateFolderPath}/requirements.txt', f'{project.name}/requirements.txt')
        shutil.copy(f'{self.templateFolderPath}/.gitignore', f'{project.name}/.gitignore')
        shutil.copy(f'{self.templateFolderPath}/makevenv.sh', f'{project.name}/makevenv.sh')
        make_file_executable(f'{project.name}/makevenv.sh')
        render_readme(project=project)
