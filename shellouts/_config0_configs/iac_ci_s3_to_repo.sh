#!/bin/bash
#
# Infrastructure as Code (IAC) S3 to GitHub Sync
#
# This script downloads Infrastructure as Code (IAC) files from an S3 bucket,
# creates or checks out a specified branch in a GitHub repository, and commits
# the files to that branch.
#
# Copyright 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

set -e  # Exit immediately if a command exits with a non-zero status

# Function to check required environment variables
check_required_env() {
    local var_name="$1"
    local var_value="${!var_name}"

    if [ -z "$var_value" ]; then
        echo "Error: $var_name is not set."
        exit 1
    fi
}

# Function to validate environment variables
validate_environment() {
    echo "Validating environment variables..."
    
    # Check for required VCS environment variables
    check_required_env "IAC_CI_GITHUB_TOKEN"
    check_required_env "GITHUB_NICKNAME"

    # Check for required IAC_CI environment variables
    check_required_env "IAC_CI_REPO"
    check_required_env "IAC_CI_BRANCH"

    # Check for required AWS S3 environment variables
    check_required_env "IAC_SRC_S3_LOC"
    check_required_env "IAC_REPO_FOLDER"
}

# Function to initialize repository paths
initialize_paths() {
    echo "Initializing paths..."
    
    # Extract filename from S3 path
    IAC_SRC_FILENAME="${IAC_SRC_S3_LOC##*/}"

    # Set up repository paths
    REPO_URL="https://$IAC_CI_GITHUB_TOKEN@github.com/$GITHUB_NICKNAME/$IAC_CI_REPO"
    PWD=$(pwd)
    CLONE_DIR="$(basename "$REPO_URL" .git)"
    DEST_DIR="$PWD/$CLONE_DIR/$IAC_REPO_FOLDER"
    
    echo "Repository: $IAC_CI_REPO"
    echo "Branch: $IAC_CI_BRANCH"
    echo "S3 Source: $IAC_SRC_S3_LOC"
}

# Function to prepare the git repository
prepare_git_repo() {
    echo "Preparing git repository..."
    
    # Check if branch exists and handle accordingly
    if git ls-remote --heads "$REPO_URL" "$IAC_CI_BRANCH" | grep -q "$IAC_CI_BRANCH"; then
        echo "Branch '$IAC_CI_BRANCH' exists. Cloning repository..."
        git clone "$REPO_URL" || { echo "Failed to clone repository"; exit 2; }
        cd "$PWD/$CLONE_DIR" || { echo "Failed to change to cloned directory"; exit 3; }
        git checkout "$IAC_CI_BRANCH" || { echo "Failed to checkout branch $IAC_CI_BRANCH"; exit 4; }
    else
        echo "Creating new branch '$IAC_CI_BRANCH'..."
        # Clone the repository without checking out files
        git clone --no-checkout "$REPO_URL" || { echo "Failed to clone repository"; exit 2; }
        cd "$PWD/$CLONE_DIR" || { echo "Failed to change to cloned directory"; exit 3; }
        # Create the new branch without files
        git checkout --orphan "$IAC_CI_BRANCH" || { echo "Failed to create orphan branch"; exit 5; }
        git rm -rf . || { echo "Failed to remove files from new branch"; exit 6; }
    fi

    # Verify that the branch has been created
    CURRENT_BRANCH=$(git name-rev HEAD | cut -d " " -f 2)
    echo "Current branch: $CURRENT_BRANCH"

    if [ "$CURRENT_BRANCH" != "$IAC_CI_BRANCH" ]; then
        echo "WARNING: Failed to switch to branch '$IAC_CI_BRANCH'. Currently on '$CURRENT_BRANCH'."
    fi
}

# Function to prepare the destination directory
prepare_destination() {
    echo "Preparing destination directory..."
    
    if [ -d "$DEST_DIR" ]; then
        echo "Directory '$DEST_DIR' exists. Deleting it..."
        rm -rf "$DEST_DIR" || { echo "Failed to delete existing directory"; exit 7; }
    fi
    mkdir -p "$DEST_DIR" || { echo "Failed to create destination directory"; exit 8; }
}

# Function to download and extract files from S3
download_and_extract() {
    echo "Downloading and extracting files..."
    
    echo "Downloading from S3 location: $IAC_SRC_S3_LOC..."
    aws s3 cp "$IAC_SRC_S3_LOC" "/tmp/$IAC_SRC_FILENAME" || { echo "Failed to download file from S3"; exit 9; }

    echo "Unzipping file $IAC_SRC_FILENAME..."
    unzip "/tmp/$IAC_SRC_FILENAME" -d "$DEST_DIR/" || { echo "Failed to unzip file"; exit 10; }
    rm "/tmp/$IAC_SRC_FILENAME" || echo "Warning: Could not delete temporary zip file"

    # Set appropriate permissions
    echo "Setting permissions on directory $DEST_DIR..."
    chmod 755 -R "$DEST_DIR" || { echo "Failed to set permissions"; exit 11; }
}

# Function to get a random number between min and max
random_between() {
    local min=$1
    local max=$2
    echo $((min + RANDOM % (max - min + 1)))
}

# Function to commit and push changes with retry mechanism
commit_and_push() {
    echo "Committing and pushing changes..."
    
    # Stage files
    git add . || { echo "Failed to stage files"; exit 12; }
    
    # Commit files
    git commit -a -m "Updated commit with files from $IAC_SRC_FILENAME" || { 
        # If nothing to commit, consider it success and return
        if git status | grep -q "nothing to commit"; then
            echo "No changes to commit. Repository is already up to date."
            return 0
        else
            echo "Failed to commit files"; 
            exit 13; 
        fi
    }
    
    # Push with retry mechanism
    local start_time=$(date +%s)
    local timeout=120  # 2 minutes timeout
    local push_successful=false
    local retry_count=0
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        retry_count=$((retry_count + 1))
        echo "Attempt #$retry_count: Pushing changes to branch '$IAC_CI_BRANCH'..."
        
        if git push -u origin "$IAC_CI_BRANCH" 2>&1; then
            push_successful=true
            echo "Successfully pushed changes to branch '$IAC_CI_BRANCH'"
            break
        else
            echo "Push failed. Remote changes detected. Pulling latest changes and retrying..."
            git pull --rebase origin "$IAC_CI_BRANCH" || {
                # Generate random delay between 1-5 seconds
                local random_delay=$(random_between 1 5)
                echo "Failed to pull/rebase changes. Trying again in $random_delay seconds..."
                sleep $random_delay
                continue
            }
        fi
    done
    
    if [ "$push_successful" = false ]; then
        echo "Error: Failed to push changes after $timeout seconds timeout ($retry_count attempts)."
        echo "The operation may be conflicting with other concurrent changes."
        exit 14
    fi

    echo "Successfully synced files from S3 to GitHub branch '$IAC_CI_BRANCH' after $retry_count attempt(s)"
}

# Function to clean up resources
cleanup() {
    echo "Cleaning up resources..."
    
    cd - || true
    rm -rf "$CLONE_DIR" || echo "Warning: Failed to remove temporary clone directory"
}

# Main function to orchestrate the process
main() {
    echo "==== Starting IAC sync process ===="
    
    validate_environment
    initialize_paths
    prepare_git_repo
    prepare_destination
    download_and_extract
    commit_and_push
    cleanup
    
    echo "==== IAC sync process completed ===="
}

# Execute the main function
main
