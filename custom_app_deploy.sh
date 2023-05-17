#!/bin/bash

# Define variables
APP_NAME="version2_app"
BKP_DIR="/home/frappe/DBbackups"
WORK_DIR="/home/frappe/HIEX-bench"
GIT_CI_TOKEN="glpat-yk-_nkFvkGysxbYUevnz"
GIT_URL="https://gitlab-ci-token:$GIT_CI_TOKEN@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git"
SITE_NAME="ezyinvoicing.local"
TAG_PREFIX="stable"
BRANCH_NAME="Merge_Branches"

# Create a backup of the site

# Change directory to frappe-bench
   cd $WORK_DIR || exit
if bench --site $SITE_NAME list-apps | grep -q "$APP_NAME"; then
   echo "$APP_NAME is installed on the site $SITE_NAME"
   echo "Creating backup..."
# If custom_app is installed, create a backup of the site
   bench --site $SITE_NAME backup --backup-path "$BKP_DIR"
   echo "Backup created successfully!"
else
# If custom_app is not installed, display a message and exit
   echo $APP_NAME not found in site. Backup not created.
   exit 1
fi

# Check if $APP_NAME exists in frappe-bench
if [ ! -d "$WORK_DIR/apps/$APP_NAME" ]; then
# If it doesn't exist, get the app from GIT_URL and install it
   echo "$APP_NAME doesn't exists"
# Change to the bench directory
   cd "$WORK_DIR || exit" || exit
   echo cloning $APP_NAME in frappe-bench
   bench get-app $GIT_URL --branch $BRANCH_NAME
   echo Installing $APP_NAME in $SITE_NAME
   bench --site $SITE_NAME install-app $APP_NAME
     echo $APP_NAME installed successfully in $SITE_NAME
fi

# Change to the app directory and check for the current branch
   cd "$WORK_DIR"/apps/$APP_NAME || exit
   CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
   COMMIT_ID=$(git rev-parse --short "$CURRENT_BRANCH")
   echo Latest commit ID of branch "$CURRENT_BRANCH": "$COMMIT_ID"

if [ "$CURRENT_BRANCH" == "$BRANCH_NAME" ]; then
# If the current branch is $BRANCH_NAME, fetch the latest tag with the prefix and checkout to it
   git fetch --tags
   LATEST_TAG=$(git describe --tags --match "${TAG_PREFIX}*" "$(git rev-list --tags --max-count=1)")
  if [ -n "$LATEST_TAG" ]; then
    git checkout "$LATEST_TAG"
  else
    echo $TAG_PREFIX not found in branch $BRANCH_NAME
    exit 1
  fi
else
# If the current branch is not $CURRENT_BRANCH, checkout to it and fetch the latest tag with the prefix
  git checkout $BRANCH_NAME
  git fetch --tags
  LATEST_TAG=$(git describe --tags --match "${TAG_PREFIX}-*" "$(git rev-list --tags --max-count=1)")
  if [ -n "$LATEST_TAG" ]; then
    git checkout "$LATEST_TAG"
  else
    echo $TAG_PREFIX not found in branch $BRANCH_NAME
    exit 1
  fi
fi

# Migrate the site and set up requirements
  bench --site $SITE_NAME migrate

# Check if the migration was successful
if ! bench --site $SITE_NAME migrate; 
then
#     bench setup requirements
    echo $APP_NAME updated successfully
  fi
  else
# If the migration failed, checkout the previous tag commit id branch
    git checkout "$COMMIT_ID"
    bench --site $SITE_NAME migrate
    bench version
fi
