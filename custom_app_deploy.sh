#!/bin/bash

# Define variables
APP_NAME=version2_app
BKP_DIR=/home/frappe/DBbackups
WORK_DIR=/home/frappe/frappe-bench
FRONTEND_DIR=/home/frappe/ezy-invoice-production
INVOICE_PARSERS_DIR=/home/frappe/frappe-bench/apps/version2_app/version2_app/parsers_invoice/invoice_parsers
INVOICE_SYNC_DIR=/home/frappe/frappe-bench/apps/invoice_sync
#GIT_CI_TOKEN=glpat-yk-_nkFvkGysxbYUevnz
BACKEND_GIT_URL=https://bharani:cmmbgjlouzg66mstbezadlhmyulfq4kypwosp4yc76p37slugzyq@dev.azure.com/caratred/EzyInvoicing/_git/Ezyinvoice_Backend.git
PARSERS_GIT_URL=https://bharani:6admufoiq7ftu5677hop3vegwsqg724h4cbmnvre2zl2wmvcquba@dev.azure.com/caratred/EzyInvoicing/_git/invoice_parsers
FRONTEND_GIT_URL=https://bharani:ek35zeobnsxm4ugbv6gdcifyd2paigmv2zp4465wghj2lwalqmpa@dev.azure.com/caratred/EzyInvoicing/_git/ezy-invoice-production.git
SYNC_GIT_URL=https://bharani:urktaplg25az77fmu3mi4yc2oanijs4qm3m2ygqbicfird6w6lga@dev.azure.com/caratred/EzyInvoicing/_git/invoice-sync.git
SITE_NAME=ezyinvoicing.local
TAG_PREFIX=stable
BRANCH_NAME=Merge_Branches

# Create a backup of the site

# Change directory to frappe-bench
cd $WORK_DIR || exit
if bench --site $SITE_NAME list-apps | grep -q "$APP_NAME"; then
  echo "$APP_NAME is installed on the site $SITE_NAME"
  echo "Creating backup..."
# If custom_app is installed, create a backup of the site
  bench --site $SITE_NAME backup --compress --backup-path "$BKP_DIR"
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
  git fetch --tags --all
  LATEST_TAG=$(git describe --tags --match "${TAG_PREFIX}-*" "$(git rev-list --tags --max-count=1)")
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
# if ! bench --site $SITE_NAME migrate; then
if [ $? -eq 0 ]; then 
    echo $APP_NAME updated successfully
    echo updating invoice-parsers 
    cd $INVOICE_PARSERS_DIR || exit 
    git pull origin master
#    if [ $? -eq 0 ]; then 
      echo Parsers updated successfully....
#      exit 1
#    fi
      echo updating frontend 
      cd $FRONTEND_DIR || exit 
      git pull origin master --allow-unrelated-histories
#      if [ $? -eq 0 ]; then 
        echo Frontend updated successfully....
#        exit 1
#      fi
        echo updating Invoice-Sync
        cd $INVOICE_SYNC_DIR || exit 
        git pull origin master
#        if [ $? -eq 0 ]; then
          echo Invoice-sync updated successfully....
#          exit 1
#        fi
#    exit 1
else
# If the migration failed, checkout the previous tag commit id branch
    cd $WORK_DIR/apps/$APP_NAME || exit
    git checkout "$COMMIT_ID"
    bench --site $SITE_NAME migrate
fi
