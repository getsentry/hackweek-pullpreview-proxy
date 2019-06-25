from __future__ import absolute_import
import github3


def get_client(config):
    return github3.GitHub(token=config['github.token'])


def get_pull_request(client, owner, repo, number):
    return client.repository(owner, repo).pull_request(number)
