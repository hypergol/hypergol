import json
from datetime import datetime


class DatasetDefFileDoesNotMatchException(Exception):
    pass


class DataSetDefFile:

    def __init__(self, dataset):
        self.dataset = dataset
        self.dependencies = []

    def add_dependency(self, dataset):
        self.dependencies.append(dataset)

    @property
    def defFilename(self):
        """Full path of the definition file for this dataset"""
        return f'{self.dataset.directory}/{self.dataset.name}.def'

    def get_def_file_data(self):
        """Loads the data from the ``.def`` file"""
        return json.loads(open(self.defFilename, 'rt').read())

    def make_def_file(self):
        """Creates the ``.def`` file, adds the dependencies ``.def`` data with that dataset's own checksum (which is the SHA1 of the content of that dataset's ``.chk`` file)
        """
        dependencyData = []
        for dataset in self.dependencies:
            data = dataset.defFile.get_def_file_data()
            data['chkFileChecksum'] = dataset.chkFile.get_checksum()
            dependencyData.append(data)
        defData = {
            'dataType': self.dataset.dataType.__name__,
            'project': self.dataset.project,
            'branch': self.dataset.branch,
            'name': self.dataset.name,
            'chunkCount': self.dataset.chunkCount,
            'creationTime': datetime.now().isoformat(),
            'dependencies': dependencyData,
            'repo': self.dataset.repoData.to_data()
        }
        self.dataset.directory.mkdir(parents=True, exist_ok=True)
        with open(self.defFilename, 'wt') as defFile:
            defFile.write(json.dumps(defData, sort_keys=True, indent=4))

    def check_def_file(self):
        """Checks if a dataset already exists the definition of the object matches to that on disk"""
        defFileData = self.get_def_file_data()
        isDefValuesMatch = (
            defFileData['dataType'] == self.dataset.dataType.__name__ and
            defFileData['project'] == self.dataset.project and
            defFileData['branch'] == self.dataset.branch and
            defFileData['name'] == self.dataset.name and
            defFileData['chunkCount'] == self.dataset.chunkCount
        )
        if not isDefValuesMatch:
            raise DatasetDefFileDoesNotMatchException('The definition of the dataset class does not match the def file.')
        return True
