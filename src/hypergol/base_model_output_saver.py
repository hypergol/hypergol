

class BaseModelOutputSaver:
    """
        Base class for model output savers
    """

    def __init__(self, savePath):
        """
        Parameters
        ----------
        savePath: path
            path to save the model outputs to
        """
        self.savePath = savePath

    def save_outputs(self, batch, outputs, globalStep):
        """saves outputs to savePath

        Parameters
        ----------
        batch:
            batch of input data that produced the given outputs, typing depends on the subclass of saver
        outputs:
            model outputs to save, typing depends on the subclass of saver
        globalStep: int
            step that the model produced these outputs
        """
        raise NotImplementedError(f'{self.__class__} must implement `save_outputs` function')
