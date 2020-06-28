import re


class NameString:

    def __init__(self, name, plural=None):
        def _to_components(value):
            value = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
            value = re.sub('([a-z0-9])([A-Z])', r'\1_\2', value)
            return [v.title() for v in value.split('_')]
        self._components = _to_components(name)
        self._pluralComponents = _to_components(plural) if plural else []

    def __repr__(self):
        return self.asClass

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, NameString):
            return False
        return self.asClass == other.asClass

    def __hash__(self):
        return hash(self.asClass)

    @property
    def asFileName(self):
        return self.asSnake + '.py'

    @property
    def asSnake(self):
        return '_'.join(v.lower() for v in self._components)

    @property
    def asClass(self):
        return ''.join(self._components)

    @property
    def asVariable(self):
        return self._components[0].lower() + ''.join(self._components[1:])

    @property
    def asPluralVariable(self):
        if len(self._pluralComponents) > 0:
            return self._pluralComponents[0].lower() + ''.join(self._pluralComponents[1:])
        return self.asVariable + ('s' if self.asVariable[-1] != 's' else 'es')

    @property
    def asPluralSnake(self):
        if len(self._pluralComponents) > 0:
            return '_'.join(v.lower() for v in self._pluralComponents)
        return self.asSnake + ('s' if self.asSnake[-1] != 's' else 'es')
