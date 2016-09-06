# GitLab Notifier

A Python script informing you about [GitLab](https://about.gitlab.com/) builds progress with native system notifications.

## Prerequisites

Python 3. May eventually works with Python 2 (not tested).

## Installation

Clone this repo, and then the usual `pip install -r requirements.txt`.

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `TIMEZONE` Self-explanatory parameter
  - `GITLAB_ENDPOINT` Root URL to your GitLab instance
  - `GITLAB_TOKEN` Token used to access your GitLab instance API. You can create one in **Profile Settings** > **Personal Access Tokens**
  - `POLL_INTERVAL` Interval, in seconds, when the script will check for updates
  - `POLL_FILTER_USERNAME` A GitLab username to filter builds by (you probably don't want to be spammed by your coworkers builds)

## Usage

```
python run.py --project=4
```

`--project` is a GitLab project ID.

## How it works

This script, once started, polls the [GitLab builds API](http://docs.gitlab.com/ce/api/builds.html) of a specific
project every 60 seconds (by default) indefinitely. It internally maintain a list of every builds that
are in progress, thus allowing us to display [native notifications](https://plyer.readthedocs.io/en/latest/) when build statuses are updated.