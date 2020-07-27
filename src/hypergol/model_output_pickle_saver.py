import pickle
from pathlib import Path


class ModelOutputPickleSaver:

    def __init__(self, savePath):
        self.savePath = savePath

    def save_outputs(self, batch, outputs, globalStep):
        savePath = Path(self.savePath, 'predictions', str(globalStep))
        savePath.mkdir(parents=True, exist_ok=True)
        pickle.dump(batch['batchIds'], open(f'{savePath}/batchIds.pkl', 'wb'))
        pickle.dump(outputs, open(f'{savePath}/outputs.pkl', 'wb'))
