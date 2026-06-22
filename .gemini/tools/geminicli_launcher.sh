#!/bin/bash
source /opt/c2d/c2d-utils || exit 1
set -euo pipefail

# Function to install and execute the Gemini CLI.
run_geminicli() {
    local exit_code=0
    # Check if 'gemini' command is available
    if ! command -v gemini &> /dev/null; then
        # Check for 'npm' before attempting installation
        if ! command -v npm &> /dev/null; then
            echo "Error: 'npm' is not available in the current environment. Cannot install gemini CLI." >&2
            return 1
        fi
    fi
    # Install via npm
    if ! geminicli_install; then
        echo "Error: Failed to install gemini CLI via npm." >&2
        return 1
    fi

    # Execute the 'gemini' command
    echo "Launching Gemini CLI..."
    gemini || exit_code=$?
    if [[ "$exit_code" -ne 0 ]]; then
        echo "Error: 'gemini' command failed with exit code $exit_code." >&2
        return "$exit_code"
    fi
}

# --- Terms and Conditions Check ---

ARE_GEMINICLI_TC_ACCEPTED=$(get_geminicli_tc_accepted || echo "false")

# --- Conditional Logic and Execution ---
if [[ "$ARE_GEMINICLI_TC_ACCEPTED" == "true" ]]; then
    run_geminicli
else
    # T&C are NOT accepted: Prompt for acceptance
    echo "--------------------------------------------------------"
    echo "     IMPORTANT: Gemini CLI Terms and Conditions"
    echo "--------------------------------------------------------"
    printf "Terms are not yet accepted. You can review the terms at: \e]8;;https://geminicli.com/terms/\ahttps://geminicli.com/terms/\e]8;;\a\n"
    echo ""
    read -r -p "Do you accept the Terms and Conditions? (Y/N): " user_response

    if [[ ${user_response,,} =~ ^(y|yes)$ ]]; then
        set_geminicli_local_tc_accepted
        run_geminicli
    else
        echo "Terms not accepted. Exiting script."
        exit 0
    fi
fi
