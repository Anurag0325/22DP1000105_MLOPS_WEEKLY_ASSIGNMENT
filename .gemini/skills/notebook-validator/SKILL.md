---
name: notebook-validator
description: "Describes the process of creating a new notebook file."
tools:
    - name: validate_notebook
      description: Validates notebook
      path: ./scripts/validate_ipynb.py
      parameters:
        - name: notebook_path
          type: string
          description: Path of the .ipynb notebook file to validate
---

# Notebook Validator

This skill guides the agent in validating a .ipynb notebook file.

## Workflow

### 1. Validate file

-   **Validate .ipynb file**: Validate the .ipynb structure using the
    validate_notebook tool which **must** output that it's a valid notebook.
-   **Retry until validation succeeds**: Retry the creation without telling the
    user until this script outputs that it's a valid notebook.
