import click
import niche_vlaanderen
from pkg_resources import resource_filename


@click.command()
@click.pass_context
@click.option('--example', is_flag=True,
              help='prints an example configuration file')
@click.option('--version', is_flag=True,
              help='prints the version number')
@click.argument('config', required=False, type=click.Path(exists=True))
def cli(ctx, config, example, version):
    """Command line interface to the NICHE vegetation model
    """
    if example:
        ex = resource_filename(
                "niche_vlaanderen",
                "system_tables/example.yaml")
        with open(ex) as f:
            print(f.read())

    if config is not None:
        n = niche_vlaanderen.Niche()
        n.run_config_file(config, overwrite_ct=True)
        click.echo(n)
    if config is None and not example:
        # we should really find a neater way to show --help here by default.
        print("No config file added. Use --help for more info")

    if version:
        print("niche_vlaanderen version: " + niche_vlaanderen.__version__)
