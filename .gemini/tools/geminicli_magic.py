"""IPython magic to interact with the Gemini CLI."""
import re
import subprocess
import IPython
from IPython.core import magic

register_cell_magic = magic.register_cell_magic


@register_cell_magic
def geminicli_magic(line, cell):
  """IPython cell magic to call the gemini CLI with the cell content.

  The content of the cell is used as a prompt for the gemini CLI. The output
  (expected to be Python code) is then injected into the next cell.

  Args:
    line: The line magic arguments (not used).
    cell: The content of the cell, used as the prompt for Gemini.
  """
  del line  # Unused by cell magic.
  user_input = cell.strip()

  # We add a 'system prompt' to ensure it returns raw code
  prompt_modifier = (
      "\n\nReturn ONLY the python code. Do not include explanations or"
      " file-writing commands."
  )
  full_prompt = user_input + prompt_modifier

  try:
    # Run the gemini CLI
    result = subprocess.run(
        ["gemini", "-p", full_prompt],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout.strip()

    # Clean up the output: Remove markdown code blocks (```python ... ```)
    # This regex looks for content inside backticks
    code_match = re.search(r"```(?:python)?(.*?)```", output, re.DOTALL)
    if code_match:
      final_code = code_match.group(1).strip()
    else:
      final_code = output

    # Inject into the next cell
    ip = IPython.get_ipython()
    ip.set_next_input(final_code, replace=False)

    print("✨ Code generated and placed in the cell below.")

  except subprocess.CalledProcessError as e:
    print(f"❌ CLI Error: {e.stderr}")
  except FileNotFoundError:
    print(
        "❌ CLI Error: 'gemini' command not found. Is it installed and in your"
        " PATH?"
    )
  except OSError as e:
    print(f"❌ OS Error: Failed to run gemini CLI: {e}")
  except AttributeError:
    print("❌ IPython Error: Could not get IPython instance to set next input.")
