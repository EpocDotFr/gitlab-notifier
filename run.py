from envparse import env, Env
import arrow
import click
import gitlab
import plyer


def debug(message, err=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
), err=err)


@click.command()
@click.option('--project', '-p', type=int, help='Gitlab project ID')
def run(project):
    Env.read_envfile('.env')

    gl = gitlab.Gitlab(env('GITLAB_ENDPOINT'), env('GITLAB_TOKEN'))

    try:
        builds = gl.project_builds.list(project_id=project)
    except Exception as e:
        debug(e, err=True)

    # plyer.notification.notify(title='Tu pues', message='ahah d gsdhsdhhd hsdh g shgdsggsd sdggsd fdsfsf f', app_name='Test')

    # TODO
    # 1. Get all desired builds from a certain project
    # 2. For each builds: is it in the DB?
    #     2.1 Yes: was its status changed?
    #       2.1.1 Yes: Notify
    #       2.1.2 No: do nothing, next build
    #     2.2 No: insert it in the DB, notify
    # 3. Repeat every 30 seconds

if __name__ == '__main__':
    run()