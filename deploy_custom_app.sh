#!/bin/bash
WORKDIR=/home/erpnext/bench/frappe-bench/
app1=version2_app
app2=invoice_sync
app1_repo_url=https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
app2_repo_url=https://gitlab-ci-token:glpat-hkCE2pJqAC4ywuTHD4wP@gitlab.caratred.com/sumanth512/invoice-sync.git

# Check if the first app exists

if [ -d "${WORKDIR}/apps/${app1}" ]
then
  echo "Updating $app1"
  # Change directory to the app directory
  cd "${WORKDIR}/apps/${app1}"
  #git remote remove origin
  #git remote remove upstream

  #git remote add origin https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
  #git remote add upstream https://gitlab-ci-token:glpat-yk-_nkFvkGysxbYUevnz@gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git
  # Pull the latest changes from the git repository
  # Get the latest tag for the branch and update to it
  git fetch --tags
  
  git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
  # Change directory back to the frappe-bench directory
  cd ../../..
else
  # If the app does not exist, get it from the git repository
  echo "Installing $app1"
  bench get-app $app1 $app1_repo_url
  # Install the app in the given site
  bench --site lifescc install-app $app1
fi

# Check if the second app exists
if [ -d "${WORKDIR}/apps/${app2}" ]
then
  echo "Updating $app2"
  # Change directory to the app directory
  cd "${WORKDIR}/apps/${app2}"
  # Get the latest tag for the branch and update to it
  git fetch --tags
  git checkout $(git describe --tags $(git rev-list --tags --max-count=1))
  # Change directory back to the frappe-bench directory
  cd ../../..
else
  # If the app does not exist, get it from the git repository
  echo "Installing $app2"
  bench get-app $app2_repo_url
  # Install the app in the given site
  bench --site lifescc install-app $app2
fi

# Once all the apps are updated, migrate the database and requirements
bench migrate
bench update --requirements

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
done
