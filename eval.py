import logging
import lark
from dataclasses import dataclass
from definitions import (
    Definitions,
    Dimension,
    Unit
)

logger = logging.getLogger()

@lark.v_args(inline=True)
class EvaluationTree(lark.Transformer):
    from operator import (
        add,
        sub,
        mul,
        truediv as div,
        neg,
        lt,
        le,
        gt,
        ge,
        eq,
        ne
    )

    number = float

    def __init__(self, defs: Definitions):
        self.defs = defs

    def symbol(self, name):
        match self.defs.lookup_form(name):
            case [symbol]:
                return symbol
            case []:
                raise ValueError(f'No symbol found associated with name: "{name}"')
            case symbols:
                raise ValueError(f'Ambiguous symbol found: "{name}" could refer to one of: {symbols}')

    def quantity(self, num, unit):
        num = self.number(num)
        unit = self.symbol(unit)
        return unit.transform_value(num)


