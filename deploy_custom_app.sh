#!/bin/bash

# Define the ENV
STABLE_TAG_PREFIX="stable-"
WORKDIR=/home/erpnext/bench/test-bench
SITE_NAME=test.local
APP1=version2_app
APP2=invoice_sync
APP1_REPO_URL=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
APP2_REPO_URL=https://gitlab-ci-token:glpat-hkCE2pJqAC4ywuTHD4wP@gitlab.caratred.com/sumanth512/invoice-sync.git

# Check if the first app exists

if [ -d "${WORKDIR}/apps/${APP1}" ]
then
  echo "Updating $APP1"
  # Change directory to the app directory
  cd "${WORKDIR}/apps/${APP1}"
   # git remote remove origin
   # git remote remove upstream

   # git remote add origin https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
   # git remote add upstream https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git

# Pull the latest changes from the git repository
# Get the latest tag for the branch and update to it
# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" == "master" ]; then
  # Check for latest stable tag with prefix
  STABLE_TAG=$(git describe --tags --match "$STABLE_TAG_PREFIX*" --abbrev=0)

  # Checkout to latest stable tag with prefix
  git checkout "$STABLE_TAG"

else
  # Checkout to master branch
  git checkout master

  # Check for latest stable tag with prefix
  STABLE_TAG=$(git describe --tags --match "$STABLE_TAG_PREFIX*" --abbrev=0)

  # Checkout to latest stable tag with prefix
  git checkout "$STABLE_TAG"
fi

# Migrate site
bench --site "$SITE_NAME" migrate

if [ $? -eq 0 ]; then
  echo "Build success and deploy"
else
  # Check out to last successful tag branch
  LAST_SUCCESS_TAG=$(git describe --tags --match "success-*" --abbrev=0)
  git checkout "$LAST_SUCCESS_TAG"

  # Migrate site again
  bench --site "$SITE_NAME" migrate
fi
else
  # # Change directory back to the frappe-bench directory
  cd ${WORKDIR}
  # If the app does not exist, get it from the git repository
  echo "Installing $APP1"
  bench get-app ${APP1_REPO_URL}
  # Install the app in the given site
  bench --site ${SITE_NAME} install-app ${APP1}
fi
