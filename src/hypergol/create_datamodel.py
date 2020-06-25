import re
import fire
from utils import Repr


class Renderer:

    def __init__(self):
        self.lines = []

    def add(self, template, value=None, **kwargs):
        if isinstance(value, bool) and value:
            self.lines.append(template.format(**kwargs))
        elif isinstance(value, (list, set)):
            for elem in value:
                if isinstance(elem, dict):
                    self.lines.append(template.format(**elem))
                else:
                    self.lines.append(template.format(elem))
        elif value is None:
            self.lines.append(template.format(**kwargs))
        return self

    def get(self):
        return '\n'.join([v.rstrip() for v in self.lines])


def to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class Category:
    ID_ = 0
    BASIC = 1
    TEMPORAL = 2
    DATA_MODEL = 3
    LIST_BASIC = 4
    LIST_TEMPORAL = 5
    LIST_DATA_MODEL = 6
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

    @classmethod
    def from_string(cls, memberString, temporalTypes, dataModelTypes):
        if ':' not in memberString:
            raise ValueError(f'You must specify a type as <name>:<type> in {memberString}')
        parts = memberString.split(':')
        type_ = parts[1][5:-1] if parts[1].startswith('List[') else parts[1]
        category = None
        if parts[-1] == 'id':
            category = Category.ID_
        elif parts[1].startswith('List['):
            if type_ in temporalTypes:
                category = Category.LIST_TEMPORAL
            elif type_ in dataModelTypes:
                category = Category.LIST_DATA_MODEL
            else:
                category = Category.LIST_BASIC
        else:
            if type_ in temporalTypes:
                category = Category.TEMPORAL
            elif type_ in dataModelTypes:
                category = Category.DATA_MODEL
            else:
                category = Category.BASIC
        return cls(name=parts[0], type_=type_, category=category)

    def get_full_type(self):
        return f'List[{self.type_}]' if self.category in Category.LIST_TYPES else self.type_


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
        if member.get_full_type() not in self.validTypes:
            raise ValueError(f'Member {member} has invalid type {member.get_full_type()}')
        self.members.append(member)

    def need_conversion(self):
        return self.any(Category.TEMPORAL_TYPES + Category.DATA_MODEL_TYPES)

    def any(self, categories):
        if not isinstance(categories, list):
            categories = [categories]
        return any(member.category in categories for member in self.members)

    def get_types(self, categories):
        if not isinstance(categories, list):
            categories = [categories]
        return list(set(member.type_ for member in self.members if member.category in categories))

    def get_names(self, categories):
        if not isinstance(categories, list):
            categories = [categories]
        return [member.name for member in self.members if member.category in categories]

    def get_members(self, categories):
        if not isinstance(categories, list):
            categories = [categories]
        return [member for member in self.members if member.category in categories]

    def get_id_string(self):
        return ' '.join([f'self.{member.name},' for member in self.get_members(Category.ID_)])


def create_datamodel(className, *args, projectDirectory='.'):
    dataModel = DataModel(className=className, members=[], dataModelTypes=['Token'])
    for memberString in args:
        dataModel.add_member_from_string(memberString)
    renderer = (
        Renderer()
        .add('from typing import List               ', dataModel.any(Category.LIST_TYPES))
        .add('from datetime import {0}              ', dataModel.get_types(Category.TEMPORAL_TYPES))
        .add('from hypergol import BaseData         ')
        .add('from data_models.{snake} import {name}', [{'snake': to_snake(name), 'name': name} for name in dataModel.get_types(Category.DATA_MODEL_TYPES)])
        .add('                                      ')
        .add('class {className}(BaseData):          ', className=dataModel.className)
        .add('                                      ')
        .add('    def __init__(self, {arguments}):  ', arguments=', '.join([f'{member.name}: {member.get_full_type()}' for member in dataModel.members]))
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
    with open(f'{projectDirectory}/datamodels/{dataModel.fileName}', 'wt') as dataModelFile:
        dataModelFile.write(renderer.get())


if __name__ == "__main__":
    fire.Fire(create_datamodel)
