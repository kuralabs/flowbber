pipeline {
    agent none

    stages {
        stage('Build') {
            agent {
                docker {
                    image 'kuralabs/flowbber:latest'
                    args '--init'
                }
            }
            steps {
                sh '''
                    entrypoint.sh
                    tox -e build
                    tox -e test
                    tox -e doc
                '''
                stash name: 'docs', includes: '.tox/env/tmp/html/**/*'
            }
        }

        stage('Publish') {
            agent { label 'docs' }
            when { branch 'master' }
            steps {
                unstash 'docs'
                sh '''
                    umask 022
                    mkdir -p /deploy/docs/flowbber
                    rm -rf /deploy/docs/flowbber/*
                    cp -R .tox/env/tmp/html/* /deploy/docs/flowbber/
                '''
            }
        }
    }
    post {
        success {
            slackSend (
                color: '#00FF00',
                message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
            )
        }

        failure {
            slackSend (
                color: '#FF0000',
                message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
            )
        }
    }
}
