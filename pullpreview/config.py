import os

SETTINGS = {
    'github.token': os.environ.get('GITHUB_TOKEN', ''),
    'github.organization': os.environ.get('GITHUB_ORGANIZATION', 'getsentry'),
    'gcs.bucket_url': os.environ.get('GCS_BUCKET_URL', 'https://storage.googleapis.com/sentry-hackweek-serverless-ui/'),
    'upstream.host': os.environ.get('UPSTREAM_HOST'),
}
