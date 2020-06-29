import re


class NameString:

    def __init__(self, name, plural=None):
        r1 = re.compile(r'(.)([A-Z][a-z]+)')
        r2 = re.compile(r'([a-z0-9])([A-Z])')
        self._components = [v.title() for v in r2.sub(r'\1_\2', r1.sub(r'\1_\2', name)).split('_')]
        self._pluralComponents = [v.title() for v in r2.sub(r'\1_\2', r1.sub(r'\1_\2', plural)).split('_')] if plural is not None else []

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
