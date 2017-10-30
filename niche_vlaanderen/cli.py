import click
import niche_vlaanderen

@click.command()
@click.argument('config')

def cli(config):
    n = niche_vlaanderen.Niche()
    n.run_config_file(config)
    print(n.__repr__)