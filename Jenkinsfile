pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh '''
                    echo "Build Package."
                    tox -e build
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    echo "Running Test Suite."
                    tox -e test
                '''
            }
        }
        stage('Documentation') {
            steps {
                sh '''
                    echo "Building Documentation."
                    tox -e doc
                '''
            }
        }
    }
}