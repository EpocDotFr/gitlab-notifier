from envparse import env, Env
import arrow
import click
import gitlab


def debug(message, err=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
), err=err)


@click.command()
def run():
    Env.read_envfile('.env')

    gl = gitlab.Gitlab(env('GITLAB_ENDPOINT'), env('GITLAB_TOKEN'))

    try:
        builds = gl.project_builds.list(project_id=env('GITLAB_PROJECT'))
    except Exception as e:
        debug(e, err=True)

if __name__ == '__main__':
    run()