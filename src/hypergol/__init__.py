import sys

from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound

from .pipeline import Pipeline
from .base_data import BaseData
from .delayed import Delayed
from .dataset import Dataset
from .dataset_factory import DatasetFactory
from .repo_data import RepoData
from .job import Job
from .task import Task
from .repr import Repr
from .logger import Logger
from .hypergol_project import RepoManager
from .hypergol_project import HypergolProject
# This spicy hack allows not to load TF/Torch each time we run a CLI command which of course doesn't use TF/Torch - Laszlo
if '-m' not in sys.argv:
    from .base_batch_processor import BaseBatchProcessor

    from .tensorflow_model_manager import TensorflowModelManager
    from .base_tensorflow_model_block import BaseTensorflowModelBlock
    from .base_tensorflow_model import BaseTensorflowModel

    from .torch_model_manager import TorchModelManager
    from .base_torch_model_block import BaseTorchModelBlock
    from .base_torch_model import BaseTorchModel

try:
    __version__ = get_distribution('hypergol').version
except DistributionNotFound:
    __version__ = open('version', 'rt').read().strip()
