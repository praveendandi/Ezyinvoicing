#!/bin/bash

# Set the Frappe sites path and the associative array of custom app names and GitLab repo URLs
site_name=lifescc
FRAPPE_SITES_PATH=/home/erpnext/bench/frappe-bench/sites
declare -A CUSTOM_APPS=(
  ["version2_app"]="https://gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git"
  ["invoice_sync"]="https://gitlab.caratred.com/sumanth512/invoice-sync.git"
  ["healthcare"]="https://github.com/frappe/health.git"
)
# Loop through each custom app
for APP in "${!CUSTOM_APPS[@]}"
do
  # Check if the custom app is already installed
  if [[ -d "${FRAPPE_SITES_PATH}/${site_name}/apps/${APP}" ]]; then
    # If it's already installed, check if there are any updates in the GitLab repo
    cd "${FRAPPE_SITES_PATH}/${site_name}/apps/${APP}"
    git fetch
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u})
    if [[ $LOCAL != $REMOTE ]]; then
      # If there are updates, update the custom app and migrate the site
      git pull
      bench migrate
    fi
  else
    # If it's not installed, install the custom app and migrate the site
    REPO_URL=${CUSTOM_APPS[$APP]}
    bench get-app ${APP} ${REPO_URL}
    bench --site site1.local install-app ${APP}
    bench migrate
  fi
done
