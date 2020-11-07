import re


class NameString:
    """Class to generate strings of various cases

        NameString stores the input string in components. The components are detected by splitting up the input name by single capital letters and underscores.

        An irregular plural version can be supplied; otherwise an 'es' or 's' will be attached to the end to get plural form.
    """

    def __init__(self, name, plural=None):
        """

        Parameters
        ----------
        name : string
            String in any case
        plural: string (default=None)
            If the plural form of a word is irregular, it can be provided here the same style as the name
        """

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
        """Returns the standard python filename

        e.g.: HelloWorld -> hello_world.py
        """
        return self.asSnake + '.py'

    @property
    def asSnake(self):
        """Returns the string as snakecase

        e.g.: HelloWorld -> hello_world
        """
        return '_'.join(v.lower() for v in self._components)

    @property
    def asClass(self):
        """Returns the string as a class name (PascalCase)

        e.g.: HelloWorld -> HelloWorld
        """
        return ''.join(self._components)

    @property
    def asVariable(self):
        """Returns the string as a variable name (camelCase)

        e.g.: HelloWorld -> helloWorld
        """
        return self._components[0].lower() + ''.join(self._components[1:])

    @property
    def asPluralVariable(self):
        """Returns the string as a plural variable name

        e.g.: HelloWorld -> helloWorlds

        Used for autogenerating dataset variable names
        """
        if len(self._pluralComponents) > 0:
            return self._pluralComponents[0].lower() + ''.join(self._pluralComponents[1:])
        return self.asVariable + ('s' if self.asVariable[-1] != 's' else 'es')

    @property
    def asPluralSnake(self):
        """Returns the string as a plural snakecase name

        e.g.: HelloWorld -> hello_worlds

        Used for autogenerating dataset file names
        """
        if len(self._pluralComponents) > 0:
            return '_'.join(v.lower() for v in self._pluralComponents)
        return self.asSnake + ('s' if self.asSnake[-1] != 's' else 'es')
