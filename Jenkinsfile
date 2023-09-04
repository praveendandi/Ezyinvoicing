pipeline {
    agent {
        label 'Test'
    }
    stages {
        stage('Check if custom app is installed') {
            steps {
                script {
                    def customAppName = 'version2_app'
                    def frappePath = '/home/erpnext/bench/frappe-bench'
                    def customAppPath = "${frappePath}/apps/${customAppName}"
                    def isCustomAppInstalled = fileExists(customAppPath)
                    if (isCustomAppInstalled) {
                        // update the custom app repo branch if available
                        def customAppRepoUrl = 'https://gitlab.caratred.com/ganesh.s/EzyinvoiceDemo.git'
                        def customAppRepoBranch = 'master'
                        def isUpdateAvailable = isUpdateAvailable(customAppPath, customAppRepoUrl, customAppRepoBranch)
                        if (isUpdateAvailable) {
                            updateCustomApp(customAppPath, customAppRepoUrl, customAppRepoBranch)
                        } else {
                            echo "Custom app ${customAppName} is already up to date"
                        }
                    } else {
                        // install the custom app
                        installCustomApp(customAppName, frappePath)
                    }
                }
            }
        }
        // add more stages here for running tests, building, deploying, etc.
    }
}

def isUpdateAvailable(customAppPath, customAppRepoUrl, customAppRepoBranch) {
    // use git to check if an update is available
    sh "cd ${customAppPath} && git fetch && git diff --quiet HEAD ${customAppRepoBranch} || echo 'Update available'"
}

def updateCustomApp(customAppPath, customAppRepoUrl, customAppRepoBranch) {
    // use git to update the custom app
    sh "cd ${customAppPath} && git fetch && git checkout ${customAppRepoBranch} && git pull"
}

def installCustomApp(customAppName, frappePath) {
    // use bench to install the custom app
    sh "cd ${frappePath} && bench get-app ${customAppName} ${customAppRepoUrl}#${customAppRepoBranch} && bench install-app ${customAppName}"
}
