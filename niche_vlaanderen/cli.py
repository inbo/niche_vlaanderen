import click
import niche_vlaanderen


@click.command()
@click.option('--example', is_flag=True,
              help='prints an example configuration file')
@click.argument('config')
def cli(config):
    """Command line interface to the NICHE vegetation model
    """
    n = niche_vlaanderen.Niche()
    n.run_config_file(config)
    click.echo(n)
