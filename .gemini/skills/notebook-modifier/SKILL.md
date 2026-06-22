---
name: notebook-modifier
description: "Describes how to modify and add cells to a notebook."
---

# Notebook Modifier

This skill guides the agent in modifying an existing notebook file.

## Workflow to edit a cell

### 1. Determine the cell

-   **Find relevant notebook**: Use the notebook-targeter skill to find the
    relevant notebook
-   **Find relevant cell**: Use the notebook-targeter skill to find the relevant
    cell

### 2. Modify the cell

-   **Edit source key only**: Only edit the **source** key of the cell object.
-   **Leave output intact**: Do not modify the **output** key of the cell.

### 3. Validate file

-   **Validate .ipynb file**: Use the notebook-validator skill to validate the
    newly created .ipynb notebook file.

## Workflow to add a cell

### 1. Determine the cell

-   **Find relevant notebook**: Use the notebook-targeter skill to find the
    relevant notebook
-   **Find relevant cell**: Use the notebook-targeter skill to find the relevant
    cell

### 2. Add a cell

-   **Create new cell**: Insert a new cell after the relevant cell.
-   **Edit source key only**: Only edit the **source** key of the cell object.
-   **Leave output intact**: Do not modify the **output** key of the cell.

### 3. Validate file

-   **Validate .ipynb file**: Use the notebook-validator skill to validate the
    updated .ipynb notebook file.
