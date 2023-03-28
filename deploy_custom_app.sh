#!/bin/bash

# Define the ENV
WORKDIR=/home/erpnext/bench/test-bench
SITE_NAME=test.local
APP1=version2_app
APP2=invoice_sync
APP1_REPO_URL=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
APP2_REPO_URL=https://gitlab-ci-token:glpat-hkCE2pJqAC4ywuTHD4wP@gitlab.caratred.com/sumanth512/invoice-sync.git

# Check if the first app exists

if [[ -d "$WORKDIR/apps/$APP1" ]]; then
  
  echo "Updating $APP1"
  # Change directory to the app directory
  cd "$WORKDIR/apps/$APP1"
   # git remote remove origin
   # git remote remove upstream

   # git remote add origin https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
   # git remote add upstream https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git

# Pull the latest changes from the git repository
# Step 2: Check the git branch
    pwd
  if [[ "$(git rev-parse --abbrev-ref HEAD)" == "master" ]]; then
    # Check for latest tag with prefix stable
    tag=$(git describe --tags --match "stable-*" --abbrev=0)
    if [[ "$tag" == "" ]]; then
        echo "No stable tag found"
    else
        # Checkout to stable prefix tag and migrate the site
        git checkout "$tag"
        bench migrate
    fi
else
    # Check if git branch is detached tag
    if [[ "$(git describe --tags)" != "" ]]; then
        # Checkout to master branch
        git checkout master
        # Check for latest tag with prefix stable
        tag=$(git describe --tags --match "stable-*" --abbrev=0)
        if [[ "$tag" == "" ]]; then
            echo "No stable tag found"
        else
            # Checkout to stable prefix tag and migrate the site
            git checkout "$tag"
            bench migrate
        fi
    else
        echo "No stable tag found"
    fi
fi
  cd ../../..
else
  cd $WORKDIR
  # If the app does not exist, get it from the git repository
  echo "Installing $APP1"
  bench get-app $APP1_REPO_URL  # Install the app in the given site
  bench --site $SITE_NAME install-app $APP1
fi
