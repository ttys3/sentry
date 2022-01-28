import click

from sentry.runner.decorators import configuration


@click.group()
def migrations():
    "Manage migrations."


@migrations.command()
@click.argument("app_name")
@click.argument("migration_name")
@click.option("--big-red-button", is_flag=True)
@configuration
@click.pass_context
def run(ctx, app_name, migration_name, big_red_button):
    "Manually run a single data migration. Will error if migration is not data only."

    from django.apps import apps
    from django.db import connections
    from django.db.migrations import RunPython
    from django.db.migrations.executor import MigrationExecutor

    migration = MigrationExecutor(connections["default"]).loader.get_migration_by_prefix(
        app_name, migration_name
    )

    if not big_red_button:
        for op in migration.operations:
            if not isinstance(op, RunPython):
                raise click.ClickException(
                    f"""
Migration must contain only RunPython ops, found: {type(op).__name__}
If you know what you're doing, you can bypass this with sentry migrations run --big-red-button.
"""
                )

    # TODO: some ops like AlterIndexTogether just don't have code attr.
    for op in migration.operations:
        op.code(apps, None)
