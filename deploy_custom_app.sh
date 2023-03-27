#!/bin/bash
WORKDIR=/home/erpnext/bench
app1=version2_app
app2=invoice_sync
app3=hrms
app1_repo_url=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
app2_repo_url=https://gitlab-ci-token:glpat-hkCE2pJqAC4ywuTHD4wP@gitlab.caratred.com/sumanth512/invoice-sync.git
app3_repo_url=https://github.com/frappe/hrms.git

# Check if the first app exists
cd $WORKDIR
if [ -d "frappe-bench/apps/$app1" ]
then
  echo "Updating $app1"
  # Change directory to the app directory
  cd "frappe-bench/apps/$app1"
  # Pull the latest changes from the git repository
  # Check if current branch is "master"
if [ $(git rev-parse --abbrev-ref HEAD) = "master" ]; then

  # Fetch tags from remote repository
  git fetch --tags

  # Get the latest tag on the current branch
  latest_tag=$(git describe --tags --abbrev=0)

  # Checkout to the latest tag
  git checkout $latest_tag
  # Get the latest tag for the branch and update to it
  ##git fetch --tags
  ##git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
  # Change directory back to the frappe-bench directory
  cd ../../..
else
  # If the app does not exist, get it from the git repository
  echo "Installing $app1"
  bench get-app $app1 $app1_repo_url
  # Install the app in the given site
  bench --site lifescc install-app $app1
fi

cd $WORKDIR
# Check if the second app exists
if [ -d "frappe-bench/apps/$app2" ]
then
  echo "Updating $app2"
  # Change directory to the app directory
  cd "frappe-bench/apps/$app2"
  # Pull the latest changes from the git repository
  git pull
  # Get the latest tag for the branch and update to it
  git fetch --tags
  git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
  # Change directory back to the frappe-bench directory
  cd ../../..
else
  # If the app does not exist, get it from the git repository
  echo "Installing $app2"
  bench get-app $app2 $app2_repo_url
  # Install the app in the given site
  bench --site lifescc install-app $app2
fi
cd $WORKDIR
# Check if the third app exists
if [ -d "frappe-bench/apps/$app3" ]
then
  echo "Updating $app3"
  # Change directory to the app directory
  cd "frappe-bench/apps/$app3"
  # Pull the latest changes from the git repository
  git pull
  # Get the latest tag for the branch and update to it
  git fetch --tags
  git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
  # Change directory back to the frappe-bench directory
  cd ../../..
else
  # If the app does not exist, get it from the git repository
  echo "Installing $app3"
  bench get-app $app3 $app3_repo_url
  # Install the app in the given site
  bench --site lifescc install-app $app3
fi
