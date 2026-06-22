"""Utility to validate Jupyter Notebook files."""

import argparse
import sys
import nbformat


def validate_ipynb_file(filepath):
  """Validates an .ipynb file using nbformat.

  Args:
    filepath: The path to the .ipynb file to validate.

  Prints validation errors if found.

  Returns:
    True if the .ipynb file is a valid Jupyter Notebook.
  """
  try:
    with open(filepath, "r", encoding="utf-8") as f:
      nbformat.read(f, as_version=nbformat.NO_CONVERT)
    print(f"'{filepath}' is a valid Jupyter Notebook.")
    return True
  except nbformat.ValidationError as e:
    print(f"Validation Error in '{filepath}':")
    print(e)
    return False
  except OSError as e:
    print(f"Error accessing file '{filepath}': {e}")
    return False


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Validate a Jupyter Notebook file."
  )
  parser.add_argument(
      "notebook_path", help="The path to the .ipynb file to validate."
  )
  args = parser.parse_args()

  if not validate_ipynb_file(args.notebook_path):
    sys.exit(1)
