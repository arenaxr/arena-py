from .attribute import Attribute


class ModelContainer(Attribute):
    """
    ModelContainer attribute class to manage its properties in the ARENA: Overrides absolute size for a 3D model. The model can be a glTF, glb, obj, or any other supported format. The model will be rescaled to fit to the sizes specified for each axes.
    Usage: `model_container=ModelContainer(...)`

    :param bool uniform: Whether to scale the model uniformly. Defaults to 'True' (optional)
    :param float x: Size of the model in the x-axis. Defaults to '1' (optional)
    :param float y: Size of the model in the y-axis. Defaults to '1' (optional)
    :param float z: Size of the model in the z-axis. Defaults to '1' (optional)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
