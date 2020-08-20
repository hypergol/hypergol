from hypergol.repr import Repr
from hypergol.dataset import Dataset
from hypergol.repo_data import RepoData


class DatasetFactory(Repr):
    """Convenience class to create lots of datasets at once. Used in pipelines where multiple datasets are created into the same location, project, branch
    """

    def __init__(self, location, project, branch, chunkCount, repoData=None):
        """
        Parameters
        ----------
        location : str
            path the project is in
        project : str
            project name
        branch : str
            branch name
        repoData : RepoData
            stores the commit information at the creation of the dataset
        chunkCount : int = {16 , 256, 4096}
            How many files the data will be stored in, sets the granularity of multithreaded processing
        """
        self.location = location
        self.project = project
        self.branch = branch
        self.chunkCount = chunkCount
        self.repoData = repoData or RepoData.get_dummy()

    def get(self, dataType, name, chunkCount=None):
        """Creates a dataset with the parameters given and the factory's own parameters

        Parameters
        ----------
        dataType : BaseData
            Type of the dataset
        name : str
            Name of the dataset (recommended to be in snakecase)
        chunkCount : int=None
            Number of chunks, if None, the factory's own value will be used
        """
        if chunkCount is None:
            chunkCount = self.chunkCount
        return Dataset(
            dataType=dataType,
            location=self.location,
            project=self.project,
            branch=self.branch,
            name=name,
            chunkCount=chunkCount,
            repoData=self.repoData
        )
