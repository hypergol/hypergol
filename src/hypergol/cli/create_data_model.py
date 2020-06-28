from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.utils import Mode
from hypergol.utils import Repr
from hypergol.utils import to_snake
from hypergol.utils import create_text_file
from hypergol.utils import get_mode
from hypergol.utils import mode_message
from hypergol.utils import get_data_model_types_old
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

    def __init__(self, className: NameString, members, dataModelTypes):
        self.className = className
        self._members = members
        self.dataModelTypes = dataModelTypes
        self.basicTypes = ['int', 'str', 'float']
        self.temporalTypes = ['datetime', 'date', 'time']
        self.validTypes = self.dataModelTypes + self.basicTypes + self.temporalTypes
        self.validTypes += [f'List[{t}]' for t in self.validTypes]
        self.validTypes += ['int:id', 'str:id']

    @property
    def fileName(self):
        return self.className.asFileName

    def add_member_from_string(self, memberString):
        member = Member.from_string(
            memberString=memberString,
            temporalTypes=self.temporalTypes,
            dataModelTypes=self.dataModelTypes
        )
        if member.fullType not in self.validTypes:
            raise ValueError(f'{member} has invalid type {member.fullType}')
        self._members.append(member)

    def select_members(self, categories):
        if not isinstance(categories, list):
            categories = [categories]
        return [member for member in self._members if member.category in categories]

    def is_any(self, categories):
        return len(self.select_members(categories)) > 0

    def needs_conversion(self):
        return self.is_any(Category.TEMPORAL_TYPES + Category.DATA_MODEL_TYPES)

    def get_types(self, categories):
        return list(set(member.type_ for member in self.select_members(categories)))

    def get_names(self, categories):
        return [member.name for member in self.select_members(categories)]

    def get_id_string(self):
        return ' '.join(f'self.{member.name},' for member in self.select_members(Category.ID_TYPES))


def create_data_model(className, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    className = NameString(className)
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    dataModelTypes = get_data_model_types_old(projectDirectory)
    dataModel = DataModel(className=className, members=[], dataModelTypes=dataModelTypes)
    for memberString in args:
        dataModel.add_member_from_string(memberString)
    renderer = (
        DataModelRenderer()
        .add('from typing import List               ', dataModel.is_any(Category.LIST_TYPES))
        .add('from datetime import {0}              ', dataModel.get_types(Category.TEMPORAL_TYPES))
        .add('from hypergol import BaseData         ')
        .add('from data_models.{snake} import {name}', [{'snake': to_snake(name), 'name': name} for name in dataModel.get_types(Category.DATA_MODEL_TYPES)])
        .add('                                      ')
        .add('                                      ')
        .add('class {className}(BaseData):          ', className=dataModel.className.asClass)
        .add('                                      ')
        .add('    def __init__(self, {arguments}):  ', arguments=', '.join([f'{member.name}: {member.fullType}' for member in dataModel.select_members(Category.ALL)]))
        .add('        self.{0} = {0}                ', dataModel.get_names(Category.ALL))
        .add('                                      ', dataModel.is_any(Category.ID_TYPES))
        .add('    def get_id(self):                 ', dataModel.is_any(Category.ID_TYPES))
        .add('        return ({idString} )          ', dataModel.is_any(Category.ID_TYPES), idString=dataModel.get_id_string())
        .add('                                      ', dataModel.needs_conversion())
        .add('    def to_data(self):                ', dataModel.needs_conversion())
        .add('        data = self.__dict__.copy()   ', dataModel.needs_conversion())
        .add("        data['{0}'] = data['{0}'].isoformat()                 ", dataModel.get_names(Category.TEMPORAL))
        .add("        data['{0}'] = data['{0}'].to_data()                   ", dataModel.get_names(Category.DATA_MODEL))
        .add("        data['{0}'] = [v.isoformat() for v in data['{0}']]    ", dataModel.get_names(Category.LIST_TEMPORAL))
        .add("        data['{0}'] = [v.to_data() for v in data['{0}']]      ", dataModel.get_names(Category.LIST_DATA_MODEL))
        .add('        return data                                           ', dataModel.needs_conversion())
        .add('                                                              ', dataModel.needs_conversion())
        .add('    @classmethod                                              ', dataModel.needs_conversion())
        .add('    def from_data(cls, data):                                 ', dataModel.needs_conversion())
        .add("        data['{name}'] = {type_}.fromisoformat(data['{name}'])                ", [{'name': member.name, 'type_': member.type_} for member in dataModel.select_members(Category.TEMPORAL)])
        .add("        data['{name}'] = {type_}.from_data(data['{name}'])                    ", [{'name': member.name, 'type_': member.type_} for member in dataModel.select_members(Category.DATA_MODEL)])
        .add("        data['{name}'] = [{type_}.fromisoformat(v) for v in data['{name}']]   ", [{'name': member.name, 'type_': member.type_} for member in dataModel.select_members(Category.LIST_TEMPORAL)])
        .add("        data['{name}'] = [{type_}.from_data(v) for v in data['{name}']]       ", [{'name': member.name, 'type_': member.type_} for member in dataModel.select_members(Category.LIST_DATA_MODEL)])
        .add('        return cls(**data)                                    ', dataModel.needs_conversion())
    )
    filePath = Path(projectDirectory, 'data_models', dataModel.fileName)
    create_text_file(filePath=filePath, content=renderer.get(), mode=mode)
    print('')
    print(f'Class {className.asClass} was created in directory {filePath}.{mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return renderer.get()
    return None


if __name__ == "__main__":
    fire.Fire(create_data_model)
