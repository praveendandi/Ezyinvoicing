#!/bin/bash

# Define the ENV
WORKDIR=/home/erpnext/bench/test-bench
SITE_NAME=test.local
APP1=version2_app
APP2=invoice_sync
APP1_REPO_URL=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
APP2_REPO_URL=https://gitlab-ci-token:glpat-hkCE2pJqAC4ywuTHD4wP@gitlab.caratred.com/sumanth512/invoice-sync.git

# Check if the first app exists

if [ -d "$WORKDIR/apps/$APP1" ]; then

  echo "Updating $APP1"
  # Change directory to the app directory
  cd "$WORKDIR/apps/$APP1"

   # git remote remove origin
   # git remote remove upstream

   # git remote add origin https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
   # git remote add upstream https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git

  # Pull the latest changes from the git repository
  # Check if the current branch is master
        if [[ "$(git rev-parse --abbrev-ref HEAD)"=="master" ]]; then
        # Find the latest tag with the prefix "stable"
        git fetch --tag
        latest_stable_tag=$(git describe --abbrev=0 --tags --match "stable*")

        # Check if a stable tag was found
        if [ -n "$latest_stable_tag" ]; then
                # Checkout the latest stable tag
                git checkout "$latest_stable_tag"
                 echo "Checked out tag: $latest_stable_tag"
         else
                echo "No stable tags found"
        fi
        else
        # Checkout the master branch
        git checkout master

        # Find the latest tag with the prefix "stable"
        git fetch --tag
        latest_stable_tag=$(git describe --abbrev=0 --tags --match "stable*")

        # Check if a stable tag was found
            if [ -n "$latest_stable_tag" ]; then
                # Checkout the latest stable tag
                git checkout "$latest_stable_tag"
                echo "Checked out tag: $latest_stable_tag"
            else
                echo "No stable tags found"
            fi
        fi
else
          cd $WORKDIR
          # If the app does not exist, get it from the git repository
          echo "Installing $APP1"
          bench get-app $APP1_REPO_URL  # Install the app in the given site
          bench --site $SITE_NAME install-app $APP1
fi
