pipeline {
    agent any

    triggers {
        githubPush()   
    }

    environment {
        IMAGE = "sbe03011/django-app"
        TAG = "v1.0.${env.BUILD_NUMBER}"
    }

    stages {

        stage('Cleanup Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/OhseungKeun/Quiz_app.git',
                        credentialsId: 'Github-Token'
                    ]]
                ])
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t $IMAGE:$TAG .
                """
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-password', variable: 'DOCKER_PW')]) {
                    sh """
                    echo "$DOCKER_PW" | docker login -u sbe03011 --password-stdin
                    docker push $IMAGE:$TAG
                    """
                }
            }
        }

        stage('Finish') {
            steps {
                echo "New image pushed: $IMAGE:$TAG"
                echo "ArgoCD Image Updater will detect the new tag and deploy automatically."
            }
        }
    }
} 
