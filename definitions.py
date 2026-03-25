import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

Number = int | float

logger = logging.getLogger()

@dataclass
class Dimension:
    name: str
    units: List['Unit']
    description: str

@dataclass
class Transform:
    module: object
    function: object 
    params: Dict[str, str]

    @staticmethod
    def new(props):
        module_name = props.get('module')
        function_name = props.get('function')
        path = [function_name]

        path_str = props.get('path')
        if path_str:
            path = path_str.split('.')
            if len(path) == 0:
                logger.warning(f"Expected path string {path_str} to specify at least one object")
                return None
            module_name = path.pop(0)

        params = props.get('params') or {}

        try:
            module = __import__(module_name)
            obj = module
            for attr_name in path:
                obj = getattr(obj, attr_name)
            return Transform(
                module=module,
                function=obj,
                params=params
            )
        except Exception as exc:
            logger.warning(f'Unable to locate transform at {module_name}: {'.'.join(path)}: ', exc)
            return None

    def transform_value(self, value):
        params = {
            param_name: self.format_parameter(param_name, value)
            for param_name in self.params
        }
        mapped = self.function(**params)
        return mapped

    def format_parameter(self, param_name, value):
        param = self.params[param_name]

        if const := param.get('value'):
            return const

        if do_pass_num := param.get('variable'):
            return value

        return None


@dataclass
class Unit:
    name: str
    forms: str
    dimension: Dimension
    transform: Transform | None

    def transform_value(self, value):
        if not self.transform:
            return value
        return self.transform.transform_value(value)




class Definitions:
    def __init__(self, unit_data, dimension_data):
        self.dimensions = {}
        for name in dimension_data:
            props = dimension_data[name]
            dim = Dimension(
                name=name,
                units=[], # will fill in later
                description=props.get('description')
            )
            self.dimensions[name] = dim

        self.units = {}
        self.form_to_units = defaultdict(list)
        for name in unit_data:
            props = unit_data[name]
            dim_name = props.get('dimension')
            if dim_name not in self.dimensions:
                logger.warning(f'Unit dimension "{dim_name}" does not exist')
                continue

            dim = self.dimensions[dim_name]
            forms = props.get('forms')
            if not forms:
                logger.warning(f'Unit with name "{name}" does not have any declared forms. It will not be referencable.')
                forms = []

            transform_props = props.get('transform')
            transform = None
            if transform_props:
                transform = Transform.new(transform_props)

            unit = Unit(
                name=name,
                forms=forms,
                dimension=dim,
                transform=transform
            )
            dim.units.append(unit)
            for form in unit.forms:
                self.form_to_units[form].append(unit)

    def lookup_form(self, name):
        return self.form_to_units[name]
