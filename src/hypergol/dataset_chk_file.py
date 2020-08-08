import json
import gzip
import hashlib

from hypergol.utils import get_hash


CHECKSUM_BUFFER_SIZE = 128*1024


class DatasetChecksumMismatchException(Exception):
    pass


class DataSetChkFile:

    def __init__(self, dataset):
        self.dataset = dataset

    @property
    def chkFilename(self):
        """Full path of the checksum file for this dataset"""
        return f'{self.dataset.directory}/{self.dataset.name}.chk'

    def get_checksum(self):
        """Hashes the content of the be stored in the dependent dataset's ``.def`` file"""
        return get_hash(data=open(self.chkFilename, 'rt').read())

    def make_chk_file(self, checksums):
        """Creates the ``.chk`` file
        Parameters
        ----------
        checksums : List[str]
            SHA1 hash of the content of each chunk file
        """
        chkData = {checksum.chunk.fileName: checksum.value for checksum in checksums}
        chkData[f'{self.dataset.name}.def'] = get_hash(open(self.dataset.defFile.defFilename, 'rt').read())
        chkDataString = json.dumps(chkData, sort_keys=True, indent=4)
        with open(self.chkFilename, 'wt') as chkFile:
            chkFile.write(chkDataString)

    def check_chk_file(self):
        """Verifies a dataset file's checksum file by loading the entire contents and recalculating the SHA1 values. Can take a long time so never called automatically.
        """
        chkFileData = json.loads(open(self.chkFilename, 'rt').read())
        mv = memoryview(bytearray(CHECKSUM_BUFFER_SIZE))
        for fileName, chkFileChecksum in chkFileData.items():
            if fileName.endswith('.def'):
                data = open(self.dataset.defFile.defFilename, 'rt').read()
                actualChecksum = get_hash(data)
            else:
                hasher = hashlib.sha1(''.encode('utf-8'))
                with gzip.open(f'{self.dataset.directory}/{fileName}', 'rb') as f:
                    for n in iter(lambda: f.readinto(mv), 0):   # pylint: disable=cell-var-from-loop
                        hasher.update(mv[:n])
                actualChecksum = hasher.hexdigest()
            if chkFileChecksum != actualChecksum:
                raise DatasetChecksumMismatchException(f'Checksum error {self.dataset.name} for {fileName}: chkFile: {chkFileChecksum}, actual: {actualChecksum}')
        return True
