---
name: notebook-explainer
description: "Describes the process of explaining a notebook."
---

# Notebook Explainer

This skill describes how to interpret and explain the content of a notebook.

## Workflow

### 1. Determine the notebook

-   **Find relevant notebook**: Use the notebook-targeter skill to find the
    relevant notebook.

### 2. Explain Code and Output

-   **Explain the source**: Provide a clear and concise explanation of the
    cell's `source` content.
-   **Explain the output**: If the cell object has an `outputs > data` key,
    provide a clear and concise explanation of the `data` key content.
-   **Explain the error**: If the cell object has an `output > output_type` key
    equals to `error`, provide a clear and concise explanation of the `evalue`.

### 3. Be proactive when error

-   **Propose to help**: If there is an error, ask the user if they need help to
    fix the cell.
-   **Fix the cell**: Use the notebook-modifier skill to update the relevant
    cell code with the fix.
