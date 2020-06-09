pipeline {
    agent { label 'docker' }

    environment {
        ADJUST_USER_UID = sh(
            returnStdout: true,
            script: 'id -u'
        ).trim()
        ADJUST_USER_GID = sh(
            returnStdout: true,
            script: 'id -g'
        ).trim()
        ADJUST_DOCKER_GID = sh(
            returnStdout: true,
            script: 'getent group docker | cut -d: -f3'
        ).trim()
    }

    stages {
        stage('Build') {

            agent {
                docker {
                    alwaysPull true
                    image 'kuralabs/flowbber:latest'
                    args '-u root:root --init'
                }
            }

            environment {
                GITHUB_TOKEN = credentials('GITHUB_TOKEN')
            }

            steps {
                sh '''
                    sudo --user=python3 --preserve-env --set-home tox --recreate
                '''
                stash name: 'docs', includes: '.tox/doc/tmp/html/**/*'
            }
        }

        stage('Publish') {
            agent { label 'docs' }
            when {
                beforeAgent true
                branch 'master'
            }
            steps {
                unstash 'docs'
                sh '''
                    umask 022
                    mkdir -p /deploy/docs/flowbber
                    rm -rf /deploy/docs/flowbber/*
                    cp -R .tox/doc/tmp/html/* /deploy/docs/flowbber/
                '''
            }
        }
    }
    post {
        success {
            slackSend (
                color: '#00FF00',
                message: ":sunny: SUCCESSFUL: " +
                    "<${env.BUILD_URL}|[${env.BUILD_NUMBER}] ${env.JOB_NAME}>"
            )
        }

        failure {
            slackSend (
                color: '#FF0000',
                message: ":rain_cloud: FAILED: " +
                    "<${env.BUILD_URL}|[${env.BUILD_NUMBER}] ${env.JOB_NAME}>"
            )
        }
    }
}
