import lark
import click
import logging
import tomllib
from dataclasses import dataclass
from definitions import Definitions
from eval import EvaluationTree

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(levelname)s: %s(message)s',
    level=logging.INFO)
@dataclass
class EvalContext:
    grammar: lark.Lark
    defs: Definitions

def setup_context() -> EvalContext:
    with open('units.toml', 'rb') as units_conf:
        units = tomllib.load(units_conf)

    with open('dimensions.toml', 'rb') as dimensions_conf:
        dimensions = tomllib.load(dimensions_conf)

    defs = Definitions(units, dimensions)
    transformer = EvaluationTree(defs)
    with open('grammar.lark') as grammar_file:
        grammar = lark.Lark(
            grammar_file,
            parser='lalr',
            transformer=transformer
        )

    return EvalContext(
        grammar=grammar,
        defs=defs
    )


def handle_eval(ctx: EvalContext, expression: str):
    result = ctx.grammar.parse(expression)
    # TODO: error handling
    click.echo(result)

@click.command()
def main(
    expression=None
):
    ctx = setup_context()

    if expression:
        handle_eval(ctx, expression)
        return

    while True:
        try:
            expression = input('> ')
            handle_eval(ctx, expression)
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as exc:
            click.echo("Exception occured: %s" % exc)
            continue



if __name__ == '__main__':
    main()
