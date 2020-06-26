from pathlib import Path
import glob
import os
import fire

from hypergol.utils import Mode
from hypergol.utils import Repr
from hypergol.utils import to_snake
from hypergol.utils import to_camel
from hypergol.utils import create_text_file
from hypergol.utils import get_mode
from hypergol.cli.data_model_renderer import DataModelRenderer


class Category:
    ID_ = 'ID'
    BASIC = 'BASIC'
    TEMPORAL = 'TEMPORAL'
    DATA_MODEL = 'DATA_MODEL'
    LIST_BASIC = 'LIST_BASIC'
    LIST_TEMPORAL = 'LIST_TEMPORAL'
    LIST_DATA_MODEL = 'LIST_DATA_MODEL'
    ID_TYPES = [ID_]
    LIST_TYPES = [LIST_BASIC, LIST_TEMPORAL, LIST_DATA_MODEL]
    BASIC_TYPES = [ID_, BASIC, LIST_BASIC]
    TEMPORAL_TYPES = [TEMPORAL, LIST_TEMPORAL]
    DATA_MODEL_TYPES = [DATA_MODEL, LIST_DATA_MODEL]
    ALL = [ID_, BASIC, TEMPORAL, DATA_MODEL, LIST_BASIC, LIST_TEMPORAL, LIST_DATA_MODEL]


class Member(Repr):

    def __init__(self, name, type_, category):
        self.name = name
        self.type_ = type_
        self.category = category

    @property
    def fullType(self):
        return f'List[{self.type_}]' if self.category in Category.LIST_TYPES else self.type_

    @classmethod
    def from_string(cls, memberString, temporalTypes, dataModelTypes):
        if ':' not in memberString:
            raise ValueError(f'You must specify a type as <name>:<type> in {memberString}')
        parts = memberString.split(':')
        type_ = parts[1][5:-1] if parts[1].startswith('List[') else parts[1]
        category = None
        if parts[-1] == 'id':
            category = Category.ID_
        elif type_ in temporalTypes:
            category = Category.LIST_TEMPORAL if parts[1].startswith('List[') else Category.TEMPORAL
        elif type_ in dataModelTypes:
            category = Category.LIST_DATA_MODEL if parts[1].startswith('List[') else Category.DATA_MODEL
        else:
            category = Category.LIST_BASIC if parts[1].startswith('List[') else Category.BASIC
        return cls(name=parts[0], type_=type_, category=category)


class DataModel(Repr):

    def __init__(self, className, members, dataModelTypes):
        self.className = className
        self.members = members
        self.dataModelTypes = dataModelTypes
        self.basicTypes = ['int', 'str', 'float']
        self.temporalTypes = ['datetime', 'date', 'time']
        self.validTypes = self.dataModelTypes + self.basicTypes + self.temporalTypes
        self.validTypes += [f'List[{t}]' for t in self.validTypes]
        self.validTypes += ['int:id', 'str:id']

    @ property
    def fileName(self):
        return f'{to_snake(self.className)}.py'

    def add_member_from_string(self, memberString):
        member = Member.from_string(
            memberString=memberString,
            temporalTypes=self.temporalTypes,
            dataModelTypes=self.dataModelTypes
        )
        if member.fullType not in self.validTypes:
            raise ValueError(f'{member} has invalid type {member.fullType}')
        self.members.append(member)

    def get_members(self, categories):
        if not isinstance(categories, list):
            categories = [categories]
        return [member for member in self.members if member.category in categories]

    def any(self, categories):
        return len(self.get_members(categories)) > 0

    def need_conversion(self):
        return self.any(Category.TEMPORAL_TYPES + Category.DATA_MODEL_TYPES)

    def get_types(self, categories):
        return list(set(member.type_ for member in self.get_members(categories)))

    def get_names(self, categories):
        return [member.name for member in self.get_members(categories)]

    def get_id_string(self):
        return ' '.join(f'self.{member.name},' for member in self.get_members(Category.ID_TYPES))


def get_data_model_types(projectDirectory):
    return [
        to_camel(os.path.split(filePath)[1][:-3])
        for filePath in glob.glob(str(Path(projectDirectory, 'data_models', '*.py')))
    ]


def create_data_model(className, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    dataModelTypes = get_data_model_types(projectDirectory)
    dataModel = DataModel(className=className, members=[], dataModelTypes=dataModelTypes)
    for memberString in args:
        dataModel.add_member_from_string(memberString)
    renderer = (
        DataModelRenderer()
        .add('from typing import List               ', dataModel.any(Category.LIST_TYPES))
        .add('from datetime import {0}              ', dataModel.get_types(Category.TEMPORAL_TYPES))
        .add('from hypergol import BaseData         ')
        .add('from data_models.{snake} import {name}', [{'snake': to_snake(name), 'name': name} for name in dataModel.get_types(Category.DATA_MODEL_TYPES)])
        .add('                                      ')
        .add('class {className}(BaseData):          ', className=dataModel.className)
        .add('                                      ')
        .add('    def __init__(self, {arguments}):  ', arguments=', '.join([f'{member.name}: {member.fullType}' for member in dataModel.members]))
        .add('        self.{0} = {0}                ', dataModel.get_names(Category.ALL))
        .add('                                      ', dataModel.any(Category.ID_TYPES))
        .add('    def get_id(self):                 ', dataModel.any(Category.ID_TYPES))
        .add('        return ({idString} )          ', dataModel.any(Category.ID_TYPES), idString=dataModel.get_id_string())
        .add('                                      ', dataModel.need_conversion())
        .add('    def to_data(self):                ', dataModel.need_conversion())
        .add('        data = self.__dict__.copy()   ', dataModel.need_conversion())
        .add("        data['{0}'] = data['{0}'].isoformat()                 ", dataModel.get_names(Category.TEMPORAL))
        .add("        data['{0}'] = data['{0}'].to_data()                   ", dataModel.get_names(Category.DATA_MODEL))
        .add("        data['{0}'] = [v.isoformat() for v in data['{0}']]    ", dataModel.get_names(Category.LIST_TEMPORAL))
        .add("        data['{0}'] = [v.to_data() for v in data['{0}']]      ", dataModel.get_names(Category.LIST_DATA_MODEL))
        .add('        return data                                           ', dataModel.need_conversion())
        .add('                                                              ', dataModel.need_conversion())
        .add('    @classmethod                                              ', dataModel.need_conversion())
        .add('    def from_data(self, data):                                ', dataModel.need_conversion())
        .add("        data['{name}'] = {type_}.fromisoformat(data['{name}'])                ", [{'name': member.name, 'type_': member.type_} for member in dataModel.get_members(Category.TEMPORAL)])
        .add("        data['{name}'] = {type_}.from_data(data['{name}'])                    ", [{'name': member.name, 'type_': member.type_} for member in dataModel.get_members(Category.DATA_MODEL)])
        .add("        data['{name}'] = [{type_}.fromisoformat(v) for v in data['{name}']]   ", [{'name': member.name, 'type_': member.type_} for member in dataModel.get_members(Category.LIST_TEMPORAL)])
        .add("        data['{name}'] = [{type_}.from_data(v) for v in data['{name}']]       ", [{'name': member.name, 'type_': member.type_} for member in dataModel.get_members(Category.LIST_DATA_MODEL)])
        .add('        return cls(**data)                                    ', dataModel.need_conversion())
    )
    filePath = Path(projectDirectory, 'data_models', dataModel.fileName)
    create_text_file(filePath=filePath, content=renderer.get(), mode=mode)
    if mode == Mode.DRY_RUN:
        return renderer.get()


if __name__ == "__main__":
    fire.Fire(create_data_model)
