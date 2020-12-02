from unittest import TestCase

class RequirementsText(TestCase):

    def test_requirements(self):
        import os
        print(os.getcwd())
        requirements = list(open('src/requirements.txt'))
        for line in open('src/setup.py'):
            if 'install_requires' in line:
                line = line[line.index('[')+1:line.index(']')].replace("'", '')
                installRequires = [req.strip() for req in line.split(',')]
        self.assertEqual(len(requirements), len(installRequires))
        for req, installReq in zip(requirements, installRequires):
            self.assertTrue(req.startswith(installReq), msg=f'{req} and {installReq} does not match')
