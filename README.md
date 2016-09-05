# Gitlab Notifier

A Python script that (natively) notifies you about [GitLab](https://about.gitlab.com/) builds progress.

## Prerequisites

TODO

## Installation

TODO

## Configuration

TODO

## Usage

TODO

## How it works

This script, once started, polls the [GitLab builds API](http://docs.gitlab.com/ce/api/builds.html) of a specific
project every 60 seconds (by default) indefinitely. It maintain a [local database](https://tinydb.readthedocs.io/en/latest/) of
every builds that are in progress, thus allowing us to display [native notifications](https://plyer.readthedocs.io/en/latest/)
when build statuses are updated.