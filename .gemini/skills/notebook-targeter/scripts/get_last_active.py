"""Gets the last active notebook information from ~/.lastactive."""

import json


def get_last_active_info():
  """Reads the last active file and returns the notebook path, cell id, and cell index."""
  try:
    with open("/home/jupyter/.lastactive", "r") as f:
      last_line = f.readlines()[-1].strip()

    parts = last_line.split("|")
    if len(parts) >= 5:
      notebook_path = parts[0]
      cell_id = parts[1]
      cell_index = parts[2]
      kernel_id = parts[3]
      kernel_name = parts[4]

      print(
          json.dumps({
              "notebook_path": notebook_path,
              "cell_id": cell_id,
              "cell_index": cell_index,
              "kernel_id": kernel_id,
              "kernel_name": kernel_name,
          })
      )
    else:
      print(json.dumps({"error": "Invalid format in .lastactive file"}))
  except FileNotFoundError:
    print(json.dumps({"error": ".lastactive file not found"}))
  except (IOError, IndexError) as e:
    print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
  get_last_active_info()
