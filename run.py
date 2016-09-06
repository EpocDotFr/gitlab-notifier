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
    # 1. Get all desired builds from a certain project filtered by status
    # 2. Filter by user and/or branch
    # 3. For each builds: is it in the internal list?
    #     3.1 Yes: was its status changed?
    #       3.1.1 Yes: Notify
    #       3.1.2 No: do nothing, next build
    #     3.2 No: insert it in the internal list, notify
    # 4. Repeat every 60 seconds

if __name__ == '__main__':
    run()