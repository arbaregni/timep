import lark
import click
import logging
import rich
import tomllib
import sys
import os
from platformdirs import PlatformDirs
from dataclasses import dataclass
from definitions import Definitions
from eval import EvaluationTree
from logging import handlers

import lark_error_reporting as parse_error_reporting

platform = PlatformDirs("arbaregni", "timep")
def get_logging_location_name():
    if not os.path.isdir(platform.user_log_dir):
        os.makedirs(platform.user_log_dir)
    return os.path.join(platform.user_log_dir, 'app.log')

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='app.log',
    level=logging.INFO
)
handler = logging.handlers.RotatingFileHandler(
    filename=get_logging_location_name(),
    backupCount=10
)

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
    sources = { 'expression': expression }
    try:
        result = ctx.grammar.parse(expression)
    except lark.UnexpectedInput as parse_exc:
        logger.info("Parse error occured", exc_info=True)
        parse_error_reporting.handle(sources, 'expression', parse_exc)
    except Exception as exc:
        # TODO: better error JsonFragment::BeginDict)ng
        # TODO: better error handling
        logger.error("An unexpected error occured: %s" % exc, exc_info=True)
        click.echo("An unexpected error occured: %s" % exc)
        click.echo("Check stack trace at %s" % get_logging_location_name())
        return
    else:
        rich.print(result)

@click.command()
@click.argument('expression', default=None)
def main(expression):
    ctx = setup_context()

    if expression:
        handle_eval(ctx, expression)
        return

    while True:
        try:
            expression = input('> ')
            if expression.strip().lower() == 'exit':
                break
            handle_eval(ctx, expression)
        except (EOFError, KeyboardInterrupt):
            break
        
if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.error("An unexpected error occured: %s" % exc, exc_info=True)
        click.echo("An unexpected error occured: %s" % exc)
        click.echo("Check stack trace at %s" % get_logging_location_name())
        sys.exit(1)

