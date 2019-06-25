from __future__ import absolute_import
import logging
import pkg_resources
import re

import requests

from flask import Flask, request, Response
from pullpreview.config import SETTINGS
import pullpreview.github as github

application = Flask("pullpreview")
application.config.update(SETTINGS)

log = logging.getLogger(__name__)
version = pkg_resources.get_distribution('pullpreview').version


DOMAIN_PATTERN = re.compile(r'^([a-z-_0-9]+?)-(\d+)\.[a-z0-9\.-_]+(?:\:\d+)?$')


@application.route("/ping")
def ping():
    return "pullpreview: %s pong\n" % (version,)


PROXY_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')


@application.route('/', defaults={'path': ''}, methods=PROXY_METHODS)
@application.route('/<path:path>', methods=PROXY_METHODS)
def forward(path):
    matches = DOMAIN_PATTERN.match(request.host)
    if not matches:
        return Response(status=404, response='Unknown host format')

    # TODO(mark) Put a short LRU on this so we don't incur the
    # cost of talking to github on every request.
    try:
        client = github.get_client(application.config)
    except Exception as e:
        log.error('Failed to connect to github %s', e)
        return Response(status=400, response='Could not connect to github')

    try:
        pull_request = github.get_pull_request(
            client,
            application.config.get('github.organization'),
            matches.group(1),
            matches.group(2))
    except Exception as e:
        log.error('Failed to fetch pull request from github %s', e)
        return Response(status=404, response='Could not find pull request.')
    head_commit = pull_request.head.sha

    proxy_args = _generate_proxy_headers(application.config, head_commit)
    url = u'{}{}'.format(application.config.get('upstream.host'),
                         request.full_path)
    response = requests.request(request.method, url, **proxy_args)

    proxy_host = request.host_url.strip('/')
    res = Response(
        response=_adapt_response_body(response, proxy_host),
        headers=_adapt_response_headers(response, proxy_host),
        status=response.status_code)

    for cookie in response.cookies:
        # Intentionally drop the cookie domain.
        res.set_cookie(
            key=cookie.name,
            # Hack to get around doubly quoted values in session cookies
            value=cookie.value.strip('"'),
            expires=cookie.expires,
            path=cookie.path,
            secure=cookie.secure,
            httponly=cookie.get_nonstandard_attr('httponly'))
    return res


def _adapt_response_headers(response, proxy_host):
    headers = dict(response.headers)
    if 'Content-Encoding' in headers:
        del headers['Content-Encoding']
    if 'Transfer-Encoding' in headers:
        del headers['Transfer-Encoding']
    if 'Set-Cookie' in headers:
        del headers['Set-Cookie']
    if 'Location' in headers:
        new_location = headers['Location'].replace(
            application.config.get('upstream.host'),
            proxy_host
        )
        headers['Location'] = new_location

    return headers


def _adapt_response_body(response, proxy_host):
    text_types = ('text/plain', 'text/html', 'application/javascript',
                  'text/javascript', 'application/json', 'text/css')
    if response.headers['Content-Type'] not in text_types:
        return response.text

    return response.text.replace(
        application.config.get('upstream.host'),
        proxy_host)


def _generate_proxy_headers(config, commit):
    """
    Convert a flask request into a structure that
    can be passed to requests for the proxy.
    """
    headers = dict([(key.upper(), value)
                    for key, value in request.headers.items()])

    if 'HOST' in headers:
        del headers['HOST']

    # Add in the FE-Base header and upstream host
    headers['X-Sentry-FE-Base'] = config['gcs.bucket_url'] + commit + '/'
    headers['Content-Type'] = request.content_type

    data = None
    if len(request.data):
        data = request.data
    elif request.form:
        data = request.form

    return {
        'headers': headers,
        'data': data,
        'allow_redirects': False
    }
