class DataModelRenderer:

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
        return '\n'.join([v.rstrip() for v in self.lines]) + '\n'
