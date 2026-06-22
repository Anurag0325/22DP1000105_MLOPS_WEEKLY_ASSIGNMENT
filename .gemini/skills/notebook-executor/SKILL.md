---
name: notebook-executor
description: "Executes a notebook file."
tools:
    - name: execute_notebook
      description: Executes notebook
      path: ./scripts/execute_notebook.sh
      parameters:
        - name: notebook_path
          type: string
          description: Path of the .ipynb notebook file to execute
        - name: kernel_env
          type: string
          description: Name of the environment to activate to access the
            relevant kernel.
        - name: kernel_name
          type: string
          description: Name of the kernel used to execute the notebook.
---

# Notebook Executor

This skill describes how to execute a notebook.

## Workflow

### 1. Determine the notebook

-   **Find relevant notebook**: Use the notebook-targeter skill to find the
    relevant notebook.

### 2. Execute the notebook

-   **Run the notebook in place**: Use the execute_notebook tool to execute the
    notebook.
