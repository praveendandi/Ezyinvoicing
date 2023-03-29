#!/bin/bash

# Define the name of the custom app and the site
WORKDIR=/home/frappe/frappe-bench
CUSTOM_APP="version2_app"
SITE_NAME="ezyinvoicing.local"
GIT_URL="https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git"


# Check if the custom app exists
# Change directory to the app directory
    cd "$WORKDIR/apps/$CUSTOM_APP"
    git remote remove origin
    git remote remove upstream

    git remote add origin https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
    git remote add upstream https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git


if ! bench list-apps | grep -q "$CUSTOM_APP"; then
    # If it doesn't exist, download and install it
    bench get-app $GIT_URL 
    bench --site $SITE_NAME install-app $CUSTOM_APP
fi

# Check which branch the custom app is on
cd ~/frappe-bench/apps/$CUSTOM_APP
current_branch=$(git branch --show-current)

if [[ $current_branch == "master" ]]; then
    # If it's on the master branch, check for the latest "stable" tag
    git fetch tag
    latest_stable_tag=$(git describe --abbrev=0 --tags --match "stable*")
else
    # If it's on any other branch or detached head, switch to master and check for the latest "stable" tag
    git checkout master
    git fetch tag
    latest_stable_tag=$(git describe --abbrev=0 --tags --match "stable*")
fi

# Check if the latest "stable" tag was found
if [[ -z "$latest_stable_tag" ]]; then
    echo "No stable tag found for $CUSTOM_APP"
else
    # Checkout the latest "stable" tag
    git checkout $latest_stable_tag

    # Migrate the site
    bench --site $SITE_NAME migrate

    # Check if the migration was successful
    if [[ $? -eq 0 ]]; then
        echo "$CUSTOM_APP successfully updated to $latest_stable_tag"
    else
        # If the migration failed, checkout to the previous tag and try again
        echo "Migration failed for $CUSTOM_APP, rolling back to previous tag"
        git checkout $latest_stable_tag^{}
        bench --site $SITE_NAME migrate
        if [[ $? -eq 0 ]]; then
            echo "$CUSTOM_APP successfully updated to previous tag"
        else
            echo "Failed to update $CUSTOM_APP"
        fi
    fi
fi
