import pickle
from pathlib import Path
from hypergol.base_model_output_saver import BaseModelOutputSaver


class ModelOutputPickleSaver(BaseModelOutputSaver):
    """
        Saves model outputs as .pkl files
    """
    def __init__(self, savePath):
        super().__init__(savePath=savePath)

    def save_outputs(self, batch, outputs, globalStep):
        savePath = Path(self.savePath, 'predictions', str(globalStep))
        savePath.mkdir(parents=True, exist_ok=True)
        pickle.dump(batch['batchIds'], open(f'{savePath}/batchIds.pkl', 'wb'))
        pickle.dump(outputs, open(f'{savePath}/outputs.pkl', 'wb'))
