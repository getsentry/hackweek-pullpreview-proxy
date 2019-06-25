Hackweek Pull Request Proxy
###########################

Acts as a proxy or man-in-middle between you and a sentry installation. When
used this proxy will allow you to view the application with the static assets of
a pull request. Given that the assets have already been uploaded to a publicly
readable GCS/S3 bucket.

On each proxied request the current HEAD of the pull request will be fetched and
added to the ``GCS_BUCKET_URL`` configuration value as ``X-Sentry-FE-Base``
header. 

Installation
============

::
    mkvirtualenv pullpreview
    pip install -e .


Configuration
=============

Configuration is all drawn from environment variables. You can put yours in
a ``.env`` file which you source before running the webserver. The following
options are **required**:

* ``GITHUB_TOKEN`` an access token that can read pull request information.
* ``UPSTREAM_HOST`` the host you want to forward requests to, including
  scheme and port if necessary.
* ``GITHUB_ORGANIZATION`` The github org containing your pull requests.
* ``GCS_BUCKET_URL`` The URL prefix (including protocol) of the bucket your
  assets are published in.


Running
=======

Run the server in development mode with::

    python pullpreview/server.py

:warning: There is no production mode.
