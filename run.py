from envparse import env, Env
from plyer.utils import platform
from plyer import notification
import time
import click
import gitlab
import os
import sys
import logging


def debug(message, err=False, terminate=False):
    """Log a regular or error message to the standard output, optionally terminating the script."""
    logging.getLogger().log(logging.ERROR if err else logging.INFO, message)

    if terminate:
        sys.exit(1)


class GitLabNotifier:
    project_id = None
    gitlab = None

    builds_list = {}

    def __init__(self, project_id):
        Env.read_envfile('.env')

        debug('Initializing')

        self.project_id = project_id
        self.gitlab = gitlab.Gitlab(env('GITLAB_ENDPOINT'), env('GITLAB_TOKEN'))

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

            filter_username = env('FILTER_USERNAME', default=None)
            filter_stage = env('FILTER_STAGE', default=None)

            for build in builds:
                if filter_username and build.user.username != filter_username: # Build wasn't started by the specified user
                    debug('  > Build #{} not started by user {}'.format(build.id, env('FILTER_USERNAME')))
                    continue

                if filter_stage and build.stage != filter_stage:
                    debug('  > Build #{} not in stage {}'.format(build.id, env('filter_stage')))
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
        message = 'On branch {}, created {}'.format(build.ref, build.created_at)

        if build.started_at:
            message += ', started ' + build.started_at

        if build.finished_at:
            message += ', finished ' + build.finished_at

        message += '.'

        app_icon = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', build.status + '.ico' if platform == 'win' else build.status + '.png')

        try:
            notification.notify(
                title='Build #{} ({}) {}'.format(build.id, build.name, build.status),
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
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        stream=sys.stdout
    )

    logging.getLogger().setLevel(logging.INFO)

    gln = GitLabNotifier(project)
    gln.run()


if __name__ == '__main__':
    run()
