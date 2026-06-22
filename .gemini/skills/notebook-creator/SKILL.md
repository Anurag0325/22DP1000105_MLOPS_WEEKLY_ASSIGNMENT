---
name: notebook-creator
description: "Describes the process of creating a new notebook file."
assets:
    - path: ./assets/example1.ipynb
      description: Notebook file example 1
    - path: ./assets/example2.ipynb
      description: Notebook file example 2
    - path: ./assets/example3.ipynb
      description: Notebook file example 3
---

# Notebook Creator

This skill guides the agent in creating a new valid .ipynb notebook file.

## Workflow

### 1. Analyze examples

-   **Learn ipynb JSON structure**: Analyze how an .ipynb file is built reading
    all the assets.

### 2. Create file

-   **Create .ipynb file**: Create a new Jupyter notebook file (`.ipynb`) in the
    `/home/jupyter` directory based on a user's request.

### 3. Validate file

-   **Validate .ipynb file**: Use the notebook-validator skill to validate the
    newly created .ipynb notebook file.
