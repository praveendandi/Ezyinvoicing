pipeline {
  agent none

  environment {
    GITLAB_TOKEN = credentials('glpat-72tFJ_LRsEW5LJnVVxzp')
    APP_NAME = 'EzyinvoiceDemo'
    APP_BRANCH = 'Merge_Branches'
    WRK_DIR = '/home/erpnext/bench/frappe-branch/apps/'
    FRAPPE_BRANCH = 'version-13'
  }

  stages {
    stage('Checkout') {
      agent Test
      steps {
        git credentialsId: 'gitlab-token', url: 'https://gitlab.com/frappe/frappe.git', branch: "${FRAPPE_BRANCH}"
        git credentialsId: 'gitlab-token', url: "https://gitlab.caratred.com/ganesh.s/${APP_NAME}.git", branch: "${APP_BRANCH}"
      }
    }

    stage('Detect Tag') {
      agent Test
      steps {
        script {
          def tagsBefore = sh(script: "cd ${WRK_DIR}/${APP_NAME} && git tag --list", returnStdout: true).trim().split()
          sh "cd ${APP_NAME} && git fetch --tags"
          def tagsAfter = sh(script: "cd ${WRK_DIR}/${APP_NAME} && git tag --list", returnStdout: true).trim().split()
          def newTag = tagsAfter.find { !tagsBefore.contains(it) }
          if (newTag != null) {
            echo "New tag detected: ${newTag}"
            sh "cd ${WRK_DIR}/${APP_NAME} && git checkout ${APP_BRANCH} && git pull origin ${APP_BRANCH} && bench switch-to-branch ${APP_BRANCH} && bench update --requirements"
          } else {
            echo "No new tag detected"
          }
        }
      }
    }

     stage('Push Changes') {
       agent none
       steps {
         sh "cd ${APP_NAME} && git add . && git commit -m 'Auto-update app' && git push origin ${APP_BRANCH}"
       }
     }
   }
 }
