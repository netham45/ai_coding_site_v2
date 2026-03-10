from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from aicoding.errors import ApplicationError, CommandExecutionError
from aicoding.cli.context import build_cli_context
from aicoding.cli.parser import build_parser
from aicoding.logging import configure_logging


def emit_payload(payload: dict[str, object] | None, *, as_json: bool = True) -> None:
    if payload is None:
        return
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def emit_error(error: ApplicationError, *, as_json: bool = True) -> None:
    payload = error.to_payload()
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        return
    print(f"{payload['error']}: {payload['message']}", file=sys.stderr)


def run(argv: Sequence[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        context = build_cli_context()
        handler = getattr(args, "handler", None)
        if handler is None:
            raise CommandExecutionError(
                message="No handler is registered for the requested command.",
                code="handler_missing",
                exit_code=2,
                details={"command": args.command},
            )

        kwargs = {}
        alembic_config_factory = getattr(args, "alembic_config_factory", None)
        if alembic_config_factory is not None:
            kwargs["alembic_config_factory"] = alembic_config_factory

        emit_payload(handler(args, context, **kwargs), as_json=True)
        return 0
    except ApplicationError as error:
        emit_error(error, as_json=True)
        return error.exit_code
