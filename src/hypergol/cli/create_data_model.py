from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.cli.data_model_renderer import DataModelRenderer
from hypergol.hypergol_project import HypergolProject

TEMPORAL = ['datetime', 'date', 'time']
DEFAULT_INITIALISATIONS = {
    'datetime': 'datetime.now()',
    'date': 'date.today()',
    'time': 'time.min()',
    'int': '0',
    'str': "''",
    'float': '0.0'
}


class Member:

    def __init__(self, name=None, type_=None, from_=None, to_=None, isList=False):
        self.name = name
        self.type_ = type_
        self.from_ = from_
        self.to_ = to_
        self.isList = isList


class DataModel:

    def __init__(self, className: NameString, project: HypergolProject):
        self.className = className
        self.project = project
        self.arguments = []
        self.initialisations = []
        self.names = []
        self.ids = []
        self.conversions = []
        self.isListDependent = False

    def process_inputs(self, value):
        m = Member(name=value.split(':', 1)[0], type_=value.split(':', 1)[1])
        self.names.append(m.name)

        if m.type_ in ['int:id', 'str:id']:
            self.ids.append(f'self.{m.name}')
            m.type_ = m.type_[:-3]
        self.arguments.append(f'{m.name}: {m.type_}')
        tmp = '[]' if m.type_.startswith('List[') else DEFAULT_INITIALISATIONS.get(m.type_, f'{m.type_}')
        self.initialisations.append(f'{m.name}={tmp}')

        if m.type_.startswith('List['):
            self.isListDependent = True
            m.type_ = m.type_[5:-1]
            m.isList = True

        if m.type_ in TEMPORAL:
            m.to_ = 'isoformat'
            m.from_ = 'fromisoformat'
            self.conversions.append(m)
        elif self.project.is_data_model_class(NameString(m.type_)):
            m.to_ = 'to_data'
            m.from_ = 'from_data'
            m.type_ = NameString(m.type_)
            self.conversions.append(m)
        elif m.type_ not in ['int', 'str', 'float']:
            raise ValueError(f'Unknown type: {value}')


def create_data_model(className, *args, projectDirectory='.', dryrun=None, force=None):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    dataModel = DataModel(className=NameString(className), project=project)
    for value in args:
        dataModel.process_inputs(value)

    content = (
        DataModelRenderer()
        .add('from typing import List               ', dataModel.isListDependent)
        .add('from datetime import {0}              ', sorted(list({m.type_ for m in dataModel.conversions if str(m.type_) in TEMPORAL})))
        .add('from hypergol import BaseData         ')
        .add('from data_models.{snake} import {name}', [{'snake': m.type_.asSnake, 'name': m.type_} for m in dataModel.conversions if str(m.type_) not in TEMPORAL])
        .add('                                      ')
        .add('                                      ')
        .add('class {className}(BaseData):          ', className=dataModel.className)
        .add('                                      ')
        .add('    def __init__(self, {arguments}):  ', arguments=', '.join(dataModel.arguments))
        .add('        self.{0} = {0}                ', dataModel.names)
        .add('                                      ', len(dataModel.ids) > 0)
        .add('    def get_id(self):                 ', len(dataModel.ids) > 0)
        .add('        return ({idString}, )         ', len(dataModel.ids) > 0, idString=', '.join(dataModel.ids))
        .add('                                      ', len(dataModel.conversions) > 0)
        .add('    def to_data(self):                ', len(dataModel.conversions) > 0)
        .add('        data = self.__dict__.copy()   ', len(dataModel.conversions) > 0)
        .add("        data['{name}'] = data['{name}'].{conv}()              ", [{'name': m.name, 'conv': m.to_} for m in dataModel.conversions if not m.isList])
        .add("        data['{name}'] = [v.{conv}() for v in data['{name}']] ", [{'name': m.name, 'conv': m.to_} for m in dataModel.conversions if m.isList])
        .add('        return data                                           ', len(dataModel.conversions) > 0)
        .add('                                                              ', len(dataModel.conversions) > 0)
        .add('    @classmethod                                              ', len(dataModel.conversions) > 0)
        .add('    def from_data(cls, data):                                 ', len(dataModel.conversions) > 0)
        .add("        data['{name}'] = {type_}.{conv}(data['{name}'])                ", [{'name': m.name, 'type_': str(m.type_), 'conv': m.from_} for m in dataModel.conversions if not m.isList])
        .add("        data['{name}'] = [{type_}.{conv}(v) for v in data['{name}']]   ", [{'name': m.name, 'type_': str(m.type_), 'conv': m.from_} for m in dataModel.conversions if m.isList])
        .add('        return cls(**data)                                    ', len(dataModel.conversions) > 0)
    ).get()
    project.create_text_file(content=content, filePath=Path(project.dataModelsPath, dataModel.className.asFileName))

    project.render(
        templateName='test_data_models.py.j2',
        templateData={
            'name': dataModel.className,
            'initialisations': ', '.join(dataModel.initialisations)
        },
        filePath=Path(project.testsPath, f'test_{dataModel.className.asFileName}')
    )

    print('')
    print(f'Class {dataModel.className} was created.{project.modeMessage}')
    print('')
    if project.isDryRun:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_data_model)
