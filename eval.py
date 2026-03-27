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

    def symbol(self, form):
        symbol = self.defs.get_symbol(form)
        return symbol.transform_value(None)

    def quantity(self, num_form, unit_form):
        num = self.number(num_form)
        unit = self.defs.get_symbol(unit_form)
        return unit.transform_value(num)


