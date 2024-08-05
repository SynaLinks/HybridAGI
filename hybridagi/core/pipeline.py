import dspy
from typing import Dict, Optional
from collections import OrderedDict

class Pipeline(dspy.Module):
    """
    A class used to represent a pipeline of dspy modules.
    It provides methods to add, remove, get, and clear modules, and to run the pipeline.
    """
    
    _modules: Dict[str, Optional[dspy.Module]] = None
    _outputs: Dict[str, Optional[dspy.Module]] = None
    
    def __init__(self):
        self._modules = OrderedDict()
        self._outputs = OrderedDict()

    def add(self, module_name: str, module: dspy.Module):
        """
        Add a module to the pipeline.

        Parameters:
            module_name (str): The name of the module.
            module (dspy.Module): The module to be added to the pipeline.

        Raises:
            ValueError: If a module with the same name already exists in the pipeline.
        """
        if not isinstance(module, dspy.Module):
            raise ValueError(f"Invalid {module_name} Module provided, only dspy.Module accepted")
        if module_name in self._modules:
            raise ValueError(f"Module {module_name} already exist.")
        self._modules[module_name] = module

    def remove(self, module_name: str):
        """
        Remove a module from the pipeline.

        Parameters:
            module_name (str): The name of the module to be removed from the pipeline.

        Raises:
            ValueError: If the module does not exist in the pipeline.
        """
        if module_name not in self._modules:
            raise ValueError(f"Module {module_name} does not exist.")
        del self._modules[module_name]

    def get(self, module_name: str) -> Optional[dspy.Module]:
        """
        Get a module from the pipeline.

        Parameters:
            module_name (str): The name of the module to be retrieved from the pipeline.

        Returns:
            Optional[dspy.Module]: The module that matches the input name.

        Raises:
            ValueError: If the module does not exist in the pipeline.
        """
        if module_name not in self._modules:
            raise ValueError(f"Module {module_name} does not exist.")
        return self._modules[module_name]
    
    def get_output(self, module_name: str):
        """
        Get the output of a module from the pipeline.

        Parameters:
            module_name (str): The name of the module whose output is to be retrieved from the pipeline.

        Returns:
            The output of the module that matches the input name.

        Raises:
            ValueError: If the module does not exist in the pipeline or if the module does not have any output yet.
        """
        if module_name not in self._modules:
            raise ValueError(f"Module {module_name} does not exist.")
        if module_name not in self._outputs:
            raise ValueError(f"Module {module_name} does not have any output yet, start by running the pipeline.")
        return self._outputs[module_name]
    
    def clear(self):
        """
        Clear the pipeline.
        This method removes all modules and outputs from the pipeline.
        """
        self._modules = OrderedDict()
        self._outputs = OrderedDict()

    def forward(self, input_or_inputs):
        """
        Run the pipeline with the input data.

        Parameters:
            input_or_inputs: The input data for the pipeline.

        Returns:
            The output of the last module in the pipeline.
        """
        current_inputs = input_or_inputs
        for module_name, module in self._modules.items():
            prediction = module(current_inputs)
            self._outputs[module_name] = prediction
            current_inputs = prediction
        return current_inputs