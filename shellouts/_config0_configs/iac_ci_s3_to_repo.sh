#!/bin/bash

# set VCS environment variables
if [ -z "$IAC_CI_GITHUB_TOKEN" ]; then
    echo "Error: IAC_CI_GITHUB_TOKEN is not set."
    exit 1
fi

if [ -z "$GITHUB_NICKNAME" ]; then
    echo "Error: GITHUB_NICKNAME is not set."
    exit 1
fi

# set IAC_CI environment variables
if [ -z "$IAC_CI_REPO" ]; then
    echo "Error: IAC_CI_REPO is not set."
    exit 1
fi

if [ -z "$IAC_CI_BRANCH" ]; then
    echo "Error: IAC_CI_BRANCH is not set."
    exit 1
fi

# AWS S3 LOCATION to get source files to track with VCS
if [ -z "$IAC_SRC_S3_LOC" ]; then
    echo "Error: IAC_SRC_S3_LOC is not set."
    exit 1
fi

if [ -z "$IAC_REPO_FOLDER" ]; then
    echo "Error: IAC_REPO_FOLDER is not set."
    exit 1
fi

IAC_SRC_FILENAME="${IAC_SRC_S3_LOC##*/}"  # Gets the file name from the full S3 path

# clone branch url
REPO_URL="https://$IAC_CI_GITHUB_TOKEN@github.com/$GITHUB_NICKNAME/$IAC_CI_REPO"
PWD=`pwd`
CLONE_DIR="$(basename "$REPO_URL" .git)"
DEST_DIR=$PWD/$CLONE_DIR/$IAC_REPO_FOLDER

# if branch exist, just exit and not create
if git ls-remote --heads "$REPO_URL" "$IAC_CI_BRANCH" | grep -q "$IAC_CI_BRANCH"
then
    echo "$IAC_CI_BRANCH branch exists."
    git clone "$REPO_URL"
    cd $PWD/$CLONE_DIR
    git checkout "$IAC_CI_BRANCH" || echo "already on branch $IAC_CI_REPO"
else
    echo "Creating branch $IAC_CI_BRANCH"

    # Clone the repository without checking out files
    git clone --no-checkout "$REPO_URL"
    cd $PWD/$CLONE_DIR

    # Create the new branch without files
    git checkout --orphan "$IAC_CI_BRANCH"
    git rm -rf .
fi

# Verify that the branch has been created
CURRENT_BRANCH=`git name-rev HEAD | cut -d " " -f 2`

echo "current branch $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "$IAC_CI_BRANCH" ]; then
    echo "WARNING: Failed to switch to branch '$IAC_CI_BRANCH'. Currently on '$CURRENT_BRANCH'."
fi

if [ -d "$DEST_DIR" ]; then
    echo "Directory '$DEST_DIR' exists. Deleting it..."
    rm -rf "$DEST_DIR"
fi

mkdir -p $DEST_DIR

# download the zip file from S3 and unzip
echo "Downloading s3 location: $IAC_SRC_S3_LOC..."
aws s3 cp $IAC_SRC_S3_LOC /tmp/$IAC_SRC_FILENAME || exit 9

echo "Unzipping file $IAC_IAC_SRC_FILENAME"
unzip "/tmp/$IAC_SRC_FILENAME" -d $DEST_DIR/ || exit 9
rm "/tmp/$IAC_SRC_FILENAME" || echo "could not delete zip file"

# Move unzipped files to the current directory
echo "Changing permissions on directory $DEST_DIR"
chmod 755 -R $DEST_DIR

echo "Commit code"
# Stage and commit the changes
git add .
git commit -a -m "updated commit with files from $IAC_SRC_FILENAME"

# Push the new branch to the remote
git push -u origin "$IAC_CI_BRANCH"

# Delete the zip file after unzipping
cd - && rm -rf $CLONE_DIR