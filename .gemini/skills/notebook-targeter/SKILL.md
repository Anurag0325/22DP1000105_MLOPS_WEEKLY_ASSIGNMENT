---
name: notebook-targeter
description: "Identifies the target notebook and cell to operate on."
tools:
    - name: target_notebook
      description: Targets the last active notebook or cell
      path: ./scripts/get_last_active.py
      outputs:
          - description: JSON object with last active data
---

# Notebook Targeter

This skill guides the agent in identifying the target notebook and cell to
operate on. The agent should use this skill when the user wants to modify a
notebook, a cell, or run a cell, and the target is ambiguous.

## Workflow

### 1. Explicit user input is a priority

-   **Use the user-provided notebook if any**: If the user provides a notebook
    path, use it.
-   **Use the user-provided cell if any**: If the user provides a cell
    reference, use it.
-   **Use the user-provided kernel if any**: If the user provides a kernel name,
    use it.

### 2. Ambiguous or no provided data

-   **Check for last active data**: If the user refers to "the notebook", "the
    active notebook", "last active cell", "the cell" or similar or no data, use
    the target_notebook tool to get the last active data.
-   **Extract notebook and cell data**: Extract from the target_notebook tool
    JSON output the notebook_path and cell_id identifier.
-   **Use notebook_path and cell_id as primary references**: Use `notebook_path`
    and `cell_id` as information on the notebook and cell to modify.
-   **Identify the kernel**: If a kernel information is needed, use values from
    the `kernel_id` and `kernel_name` keys.

### 3. No information

-   **Ask if no data**: If the script fails and the user provides no notebook,
    cell or kernel reference, ask for the needed information.
