#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Execute Notebook
# @raycast.description Executes a notebook using a specified kernel.
# @raycast.mode silent
# @raycast.argument1 { "type": "text", "placeholder": "Notebook Path" }
# @raycast.argument2 { "type": "text", "placeholder": "Environment" }
# @raycast.argument3 { "type": "text", "placeholder": "Kernel" }

# Parameters
NOTEBOOK_PATH="$1"
KERNEL_ENV="$2"
KERNEL_NAME="$3"

# Check for micromamba
if command -v micromamba &> /dev/null
then
    # Use micromamba
    eval "$(micromamba shell hook -s bash)"
    micromamba activate "$KERNEL_ENV"

    # Execute the notebook
    python -m nbconvert --inplace --to notebook --execute \
      --ExecutePreprocessor.kernel_name="$KERNEL_NAME" \
      "$NOTEBOOK_PATH"

    micromamba deactivate
elif [[ -f "/opt/conda/etc/profile.d/conda.sh" ]]; then
    # Use conda
    . "/opt/conda/etc/profile.d/conda.sh"
    conda activate "$KERNEL_ENV"

    # Execute the notebook
    python -m nbconvert --inplace --to notebook --execute \
      --ExecutePreprocessor.kernel_name="$KERNEL_NAME" \
      "$NOTEBOOK_PATH"

    conda deactivate
else
    echo "Neither micromamba nor conda found. Please install one of them."
    exit 1
fi
