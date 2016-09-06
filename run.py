from envparse import env, Env
import time
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
        while True:
            try:
                debug('Getting builds')

                builds = self.gitlab.project_builds.list(project_id=self.project_id, scope=['failed', 'success', 'canceled'])
            except Exception as e:
                debug(e, err=True)
                return

            debug('Analyzing builds')

            for build in builds:
                if build.user.username != env('FILTER_USERNAME'):
                    debug('  > Build #{} not owned by user {}'.format(build.id, env('FILTER_USERNAME')))
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
        message = 'On branch {}, created {}'.format(build.ref, arrow.get(build.created_at).to(env('TIMEZONE')).humanize())

        if build.started_at:
            message += ', started ' + arrow.get(build.started_at).to(env('TIMEZONE')).humanize()

        if build.finished_at:
            message += ', finished ' + arrow.get(build.finished_at).to(env('TIMEZONE')).humanize()

        message += '.'

        try:
            plyer.notification.notify(
                title='Build #{} {}'.format(build.id, build.status),
                message=message,
                app_name='GitLab Notifier',
                app_icon='gitlab.ico'
            )
        except Exception as e:
            debug(e, err=True)
            return


@click.command()
@click.option('--project', '-p', type=int, help='Gitlab project ID')
def run(project):
    gln = GitLabNotifier(project)

    debug('Running thread')

    gln.run()


if __name__ == '__main__':
    run()
