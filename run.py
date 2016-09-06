from envparse import env, Env
from plyer.utils import platform
from plyer import notification
import time
import arrow
import click
import gitlab
import os


def debug(message, err=False):
    click.echo('{} - {} - {}'.format(
        arrow.now(env('TIMEZONE')).format('MMM, D YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
    ), err=err)


class GitLabNotifier:
    project_id = None
    gitlab = None

    builds_list = {}

    def __init__(self, project_id):
        Env.read_envfile('.env')

        debug('Initializing')

        self.project_id = project_id
        self.gitlab = gitlab.Gitlab(env('GITLAB_ENDPOINT'), env('GITLAB_TOKEN'))

    def get_humanized_date(self, date):
        return arrow.get(date).to(env('TIMEZONE')).humanize()

    def run(self):
        debug('Running')

        while True:
            try:
                debug('Getting builds')

                builds = self.gitlab.project_builds.list(project_id=self.project_id)
            except Exception as e:
                debug(e, err=True)
                return

            debug('Analyzing builds')

            for build in builds:
                if build.user.username != env('FILTER_USERNAME'): # Build wasn't started by the specified user
                    debug('  > Build #{} not started by user {}'.format(build.id, env('FILTER_USERNAME')))
                    continue

                if build.id not in self.builds_list: # Build isn't in the internal list
                    debug('  > Build #{} not in the internal list'.format(build.id))

                    self.builds_list[build.id] = build.status
                    self.notify(build)
                else: # Build is in the internal list
                    if self.builds_list[build.id] != build.status: # Build status changed
                        debug('  > Build #{} status changed'.format(build.id))

                        self.builds_list[build.id] = build.status
                        self.notify(build)
                    else: # Build status unchanged: next build
                        debug('  > Build #{} status unchanged'.format(build.id))

                        continue

            time.sleep(env('POLL_INTERVAL', cast=int))

    def notify(self, build):
        message = 'On branch {}, created {}'.format(build.ref, self.get_humanized_date(build.created_at))

        if build.started_at:
            message += ', started ' + self.get_humanized_date(build.started_at)

        if build.finished_at:
            message += ', finished ' + self.get_humanized_date(build.finished_at)

        message += '.'

        app_icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gitlab.ico' if platform == 'win' else 'gitlab.png')

        try:
            notification.notify(
                title='Build #{} {}'.format(build.id, build.status),
                message=message,
                app_name='GitLab Notifier',
                app_icon=app_icon
            )
        except Exception as e:
            debug(e, err=True)
            return


@click.command()
@click.option('--project', '-p', type=int, help='Gitlab project ID')
def run(project):
    gln = GitLabNotifier(project)
    gln.run()


if __name__ == '__main__':
    run()
