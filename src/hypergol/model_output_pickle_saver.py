import pickle
from pathlib import Path
from hypergol.base_model_output_saver import BaseModelOutputSaver


class ModelOutputPickleSaver(BaseModelOutputSaver):
    """
        Saves model outputs as .pkl files
    """
    def __init__(self, savePath):
        super().__init__(savePath=savePath)

    def get_file_save_path(self, globalStep):
        savePath = Path(self.savePath, 'predictions', str(globalStep))
        savePath.mkdir(parents=True, exist_ok=True)
        return savePath

    def save_outputs(self, batch, outputs, globalStep):
        savePath = self.get_file_save_path(globalStep=globalStep)
        saveData = {
            'batchIds': batch['batchIds'],
            'outputs': outputs
        }
        pickle.dump(saveData, open(f'{savePath}/outputs.pkl', 'wb'))
