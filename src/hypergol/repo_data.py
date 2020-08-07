from hypergol.base_data import BaseData


class RepoData(BaseData):
    """Stores the information about the repository in the dataset"""

    def __init__(self, branchName, commitHash, commitMessage, comitterName, comitterEmail):
        """
        Parameters
        ----------
        branchName : str
        commitHash : str
        commitMessage : str
        comitterName : str
        comitterEmail : str
        """
        self.branchName = branchName
        self.commitHash = commitHash
        self.commitMessage = commitMessage
        self.comitterName = comitterName
        self.comitterEmail = comitterEmail

    @classmethod
    def get_dummy(cls):
        """Creates an empty RepoData if the Dataset was created outside a git repository"""
        print('Dummy repodata was used, data lineage disabled')
        return RepoData(
            branchName='dummy',
            commitHash='0000000000000000000000000000000000000000',
            commitMessage='dummy',
            comitterName='Dummy Dummy',
            comitterEmail='dummy@dummy.com'
        )
