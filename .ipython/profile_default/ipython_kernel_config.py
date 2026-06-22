"""IPython configuration file."""
import logging
import requests

# pylint: disable=undefined-variable
c.IPKernelApp.extensions = [
    'bq_stats',
    'google.cloud.bigquery',
    'sql'
]


def _is_jupyterlab4_enabled():
  """Checks if jupyterlab4 is enabled via metadata."""
  for flag in ['enable-jupyterlab4-preview', 'enable-jupyterlab4']:
    try:
      metadata_url = f'http://metadata.google.internal/computeMetadata/v1/instance/attributes/{flag}'
      headers = {'Metadata-Flavor': 'Google'}
      response = requests.get(metadata_url, headers=headers, timeout=1)
      if (response.status_code == 200 and response.text is not None and
          response.text.lower() == 'true'):
        return True
      # 404 is expected if the flag is not set.
      if response.status_code != 404:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
      logging.warning('Failed to fetch metadata for flag %s: %s', flag, e)
    except Exception as e:  # pylint: disable=broad-except
      logging.warning('An unexpected error occurred for flag %s: %s', flag, e)
  return False

# We don't load the beatrix_jupyterlab extension for jupyterlab 4.x
enable_beatrix_jupyterlab = not _is_jupyterlab4_enabled()
if enable_beatrix_jupyterlab:
  c.IPKernelApp.extensions.append('beatrix_jupyterlab')

c.InteractiveShellApp.matplotlib = 'inline'
