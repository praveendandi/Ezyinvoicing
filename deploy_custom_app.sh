#!/bin/bash

# Define the prefix for the stable tag
STABLE_PREFIX="stable-"
WORKDIR=/home/erpnext/bench/test-bench
SITE_NAME=test.local
APP1=version2_app
APP2=invoice_sync
APP1_REPO_URL=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
APP2_REPO_URL=https://gitlab-ci-token:glpat-hkCE2pJqAC4ywuTHD4wP@gitlab.caratred.com/sumanth512/invoice-sync.git

# Check if the first app exists

if [ -d "${WORKDIR}/apps/${app1}" ]
then
  echo "Updating $app1"
  # Change directory to the app directory
  cd "${WORKDIR}/apps/${app1}"
   # git remote remove origin
   # git remote remove upstream

   # git remote add origin https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
   # git remote add upstream https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git

# Pull the latest changes from the git repository
# Get the latest tag for the branch and update to it
# Get the name of the current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check if we're on the master branch
if [ "$CURRENT_BRANCH" == "master" ]; then
  # Check for a stable tag with the prefix
  STABLE_TAG=$(git tag -l "$STABLE_PREFIX*" | sort -V | tail -n1)
  if [ -n "$STABLE_TAG" ]; then
    # Checkout the latest stable tag with the prefix
    git checkout "$STABLE_TAG"
  fi
else
  # Checkout the master branch
  git checkout master
  # Check for a stable tag with the prefix
  STABLE_TAG=$(git tag -l "$STABLE_PREFIX*" | sort -V | tail -n1)
  if [ -n "$STABLE_TAG" ]; then
    # Checkout the latest stable tag with the prefix
    git checkout "$STABLE_TAG"
  fi
fi

# Migrate the site
  bench use $SITE_NAME
if bench migrate; then
  # If the migration succeeds, echo "build success" and deployed
  echo "build success"
  # TODO: Deploy the site
else
  # If the migration fails, checkout the previous successful tag branch and migrate again
  LAST_SUCCESS_TAG=$(git tag --list --merged HEAD "success-*" | sort -V | tail -n1)
  if [ -n "$LAST_SUCCESS_TAG" ]; then
    git checkout "$LAST_SUCCESS_TAG"
    bench migrate
    # TODO: Deploy the site
  else
  # # Change directory back to the frappe-bench directory
  cd ${WORKDIR}
  # If the app does not exist, get it from the git repository
  echo "Installing $APP1"
  bench get-app ${APP1_REPO_URL}
  # Install the app in the given site
  bench --site ${SITE_NAME} install-app ${APP1}
fi
  fi
fi
