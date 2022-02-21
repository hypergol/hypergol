import json
import time
from typing import List

import fire
import uvicorn
import torch
from fastapi import FastAPI
from fastapi import Request
from hypergol.utils import create_pydantic_type

from models.my_torch_test_model.my_torch_test_model_batch_processor import MyTorchTestModelBatchProcessor
from data_models.sentence import Sentence
from data_models.model_output import ModelOutput

TITLE = 'Serve MyTorchTestModel'
VERSION = '0.1'
DESCRIPTION = 'FastApi wrapper on MyTorchTestModel, see /docs for API details'
USE_GPU = False
THREADS = None
MODEL_DIRECTORY = '<data directory>/<project>/<branch>/models/MyTorchTestModel/<epoch>'

# TODO:
# def load_model(modelDirectory, threads, useGPU):
#     if not useGPU:
#         tf.config.experimental.set_visible_devices([], 'GPU')
#     if threads is not None:
#         tf.config.threading.set_inter_op_parallelism_threads(threads)
#         tf.config.threading.set_intra_op_parallelism_threads(threads)
#     return tf.saved_model.load(export_dir=modelDirectory)


app = FastAPI(title=TITLE, version=VERSION, description=DESCRIPTION)
model = load_model(modelDirectory=MODEL_DIRECTORY, threads=THREADS, useGPU=USE_GPU)
batchProcessor = MyTorchTestModelBatchProcessor(
    inputDataset=None,
    inputBatchSize=0,
    maxTokenCount=100,
    outputDataset=None
)
pyDanticSentence = create_pydantic_type(Sentence)
pyDanticModelOutput = create_pydantic_type(ModelOutput)


@app.middleware("http")
async def add_headers(request: Request, call_next):
    startTime = time.time()
    response = await call_next(request)
    response.headers["X-Model-Long-Name"] = model.get_long_name().numpy().decode('utf-8')
    response.headers["X-Process-Time"] = str(time.time() - startTime)
    return response


@app.get("/")
def test_main():
    return {
        'title': TITLE,
        'version': VERSION,
        'description': DESCRIPTION,
        'model': model.get_long_name().numpy().decode('utf-8')
    }


@app.post("/output", response_model=List[pyDanticModelOutput])
def get_outputs(sentences: List[pyDanticSentence]):
    sentences = [Sentence.from_data(json.loads(sentence.json())) for sentence in sentences]
    tensorInputs = batchProcessor.process_input_batch(sentences)
    tensorOutputs = model.get_outputs(**tensorInputs)
    modelOutputs = batchProcessor.process_output_batch(tensorOutputs)
    return [pyDanticModelOutput.parse_raw(json.dumps(modelOutput.to_data())) for modelOutput in modelOutputs]


def uvicorn_serve_my_torch_test_model_run(port=8000, host='0.0.0.0'):
    uvicorn.run("serve_my_torch_test_model:app", port=port, host=host, reload=True)


if __name__ == "__main__":
    # tf.get_logger().setLevel('ERROR')
    fire.Fire(uvicorn_serve_my_torch_test_model_run)
