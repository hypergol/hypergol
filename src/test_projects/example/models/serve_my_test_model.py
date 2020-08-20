import json
import fire
import uvicorn
import tensorflow as tf
from fastapi import FastAPI
from hypergol.utils import create_pydantic_type
from models.my_test_model import MyTestModelBatchProcessor
from data_models.sentence import Sentence
from data_models.model_output import ModelOutput

TITLE = 'Serve MyTestModel'
VERSION = '0.1'
DESCRIPTION = 'FastApi wrapper on MyTestModel, see /docs for API details'
USE_GPU = False
THREADS = None
MODEL_DIRECTORY = '<data directory>/<project>/<branch>/models/MyTestModel/<epoch>'


def load_model(modelDirectory, threads, useGPU):
    if not useGPU:
        tf.config.experimental.set_visible_devices([], 'GPU')
    if threads is not None:
        tf.config.threading.set_inter_op_parallelism_threads(threads)
        tf.config.threading.set_intra_op_parallelism_threads(threads)
    return tf.saved_model.load(export_dir=modelDirectory)


model = load_model(modelDirectory=MODEL_DIRECTORY, threads=THREADS, useGPU=USE_GPU)
batchProcessor = MyTestModelBatchProcessor(
    inputDataset=None,
    inputBatchSize=0,
    maxTokenCount=100,
    outputDataset=None
)

pyDanticSentence= create_pydantic_type(Sentence)
pyDanticModelOutput= create_pydantic_type(ModelOutput)

app = FastAPI(
    title=TITLE,
    version=VERSION,
    description=DESCRIPTION
)


@app.get("/")
def test_main():
    return {
        'title': TITLE,
        'version': VERSION,
        'description': DESCRIPTION
    }


@app.post("/output", response_model=pyDanticModelOutput)
def get_outputs(sentence: pyDanticSentence):
    sentence = Sentence.from_data(json.loads(sentence.json()))
    tensorInput = batchProcessor.process_input_batch(sentence)
    tensorOutput = model.get_outputs(**tensorInput)
    modelOutput = batchProcessor.process_output_batch(tensorOutput)
    return pyDanticModelOutput.parse_raw(json.dumps(modelOutput.to_data()))


def uvicorn_serve_my_test_model_run(port=8000, host='0.0.0.0'):
    uvicorn.run("serve_my_test_model:app", port=port, host=host, reload=True)


if __name__ == "__main__":
    fire.Fire(uvicorn_serve_my_test_model_run)
