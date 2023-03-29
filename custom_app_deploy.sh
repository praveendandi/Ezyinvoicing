#!/bin/bash

# Define variables
custom_app=version2_app
git_url=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
site_name=ezyinvoicing.local
tag_prefix=stable

# Check if custom_app exists in frappe-bench
if [ ! -d "/home/frappe/frappe-bench/apps/$custom_app" ]; then
  # If it doesn't exist, get the app from git_url and install it
  # Change to the bench directory 
  cd /home/frappe/frappe-bench
  bench get-app $git_url
  bench --site $site_name install-app $custom_app
fi

# Change to the app directory and check for the current branch
cd /home/frappe/frappe-bench/apps/$custom_app
current_branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$current_branch" == "master" ]; then
  # If the current branch is master, fetch the latest tag with the prefix and checkout to it
  git fetch --tags
  latest_tag=$(git describe --tags --match "${tag_prefix}*" `git rev-list --tags --max-count=1`)
  if [ -n "$latest_tag" ]; then
    git checkout $latest_tag
  else
    echo "$tag_prefix not found"
    exit 1
  fi
else
  # If the current branch is not master, checkout to it and fetch the latest tag with the prefix
  git checkout master
  git fetch --tags
  latest_tag=$(git describe --tags --match "${tag_prefix}*" `git rev-list --tags --max-count=1`)
  if [ -n "$latest_tag" ]; then
    git checkout $latest_tag
  else
    echo "$tag_prefix not found"
    exit 1
  fi 
fi

# Migrate the site and set up requirements
bench --site $site_name migrate

# Check if the migration was successful
if [ $? -eq 0 ]; then
  bench setup requirements
  echo "$custom_app updated successfully"
else
  # If the migration failed, checkout the previous tag branch
  git checkout $current_branch
  bench --site $site_name migrate
fi
