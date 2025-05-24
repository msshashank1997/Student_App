pipeline {
    agent any

    environment {
        GITREPO = "https://github.com/msshashank1997/Student_App.git"
        EC2_IP = "13.201.20.229"
        EC2_USERNAME = "ubuntu"
        EC2_ID = "shashankec2"
    }

    stages {
        stage('Clone Repo') {
            steps {
                git url: "${GITREPO}", branch: 'main'
            }
        }

        stage('Copy Files to EC2') {
            steps {
                sshagent(credentials:["${env.EC2_ID}"]) {
                    sh """
                    scp -o StrictHostKeyChecking=no -r * ${env.EC2_USERNAME}@${env.EC2_IP}:/home/ubuntu/application
                    """
                }
            }
        }
        
        stage('EC2 System Updates') {
            steps {
                sshagent(credentials:["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        sudo apt update
                        sudo apt install -y python3
                        sudo apt install -y python3-pip
                        sudo apt install -y npm
                        cd /home/ubuntu/application
                        sudo chmod -R 777 *
                    '
                    """
                }
            }
        }
        
        stage('Install Docker') {
            steps {
                sshagent(credentials:["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        sudo apt install -y docker.io
                        sudo systemctl start docker
                        sudo systemctl enable docker
                        sudo gpasswd -a \$USER docker
                    '
                    """
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                sshagent(credentials: ["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        cd /home/ubuntu/application
                        # Install Python venv package
                        sudo apt install -y python3-venv python3-full
                        # Create a virtual environment
                        python3 -m venv venv
                        # Activate virtual environment and install dependencies
                        source venv/bin/activate
                        pip install -r requirements.txt
                    '
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sshagent(credentials: ["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        cd /home/ubuntu/application
                        # Make sure docker-compose is installed
                        if ! command -v docker-compose &> /dev/null; then
                            echo "docker-compose not found, installing..."
                            sudo apt-get update
                            sudo apt-get install -y docker-compose
                        fi
                        
                        # Check if port 27017 is in use by any process
                        if sudo lsof -i :27017 | grep LISTEN; then
                            echo "Port 27017 is already in use. Stopping existing process..."
                            # Find container using port 27017
                            CONTAINER_ID=\$(sudo docker ps -q --filter "publish=27017")
                            if [ ! -z "\$CONTAINER_ID" ]; then
                                echo "Stopping Docker container using port 27017..."
                                sudo docker stop \$CONTAINER_ID
                            else
                                # If not a Docker container, find and kill the process
                                PID=\$(sudo lsof -t -i:27017)
                                if [ ! -z "\$PID" ]; then
                                    echo "Killing process \$PID that is using port 27017..."
                                    sudo kill -9 \$PID
                                fi
                            fi
                        fi
                        
                        # Stop any existing containers managed by docker-compose
                        sudo docker-compose down
                        
                        # Start containers in detached mode
                        sudo docker-compose up -d
                        
                        # Verify MongoDB container is running
                        if ! sudo docker ps | grep mongo-studentdb; then
                            echo "Error: MongoDB container failed to start"
                            exit 1
                        fi
                    '
                    """   
                }
            }
        }

        stage('Run Flask App') {
            steps {
                sshagent(credentials: ["${env.EC2_ID}"]) {
                    sh """ 
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        cd /home/ubuntu/application
                        # if docker continer is running and image is built, then run the app
                        if sudo docker ps | grep stuident-app; then
                            echo "Docker container for stuident-app is already running."
                            # stop container if it is running
                            sudo docker stop stuident-app || echo "Failed to stop existing container"
                            sudo docker rm stuident-app || echo "Failed to remove existing container"
                        else
                            echo "Starting Docker container for stuident-app..."
                            sudo docker build -t stuident-app:latest .
                            sudo docker run -d -p 5000:5000 stuident-app:latest
                        fi
                    '
                    """
                }
            }
        }

                
        stage('Seed Database') {
            steps {
                sshagent(credentials: ["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        cd /home/ubuntu/application
                        sudo npm install
                        sudo npm run import
                        '
                        """
                        }
                    }
                }

        stage('Run Tests') {
            steps {
                sshagent(credentials: ["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        cd /home/ubuntu/application 
                        source venv/bin/activate
                        
                        # Run tests and capture exit code
                        pytest test_app.py --maxfail=1 --disable-warnings -q
                        TEST_EXIT_CODE=\$?
                        
                        # If tests failed, stop services
                        if [ \$TEST_EXIT_CODE -ne 0 ]; then
                            echo "Tests failed. Stopping services..."
                            # Stop Docker containers
                            sudo docker-compose down
                            
                            # Stop the Flask application running with Gunicorn on port 5000
                            echo "Stopping Flask application on port 5000..."
                            # Find processes using port 5000
                            PORT_PIDS=\$(lsof -t -i:5000 || echo "")
                            if [ ! -z "\$PORT_PIDS" ]; then
                                echo "Killing processes using port 5000: \$PORT_PIDS"
                                kill -9 \$PORT_PIDS || echo "Failed to kill some processes"
                            fi
                            
                            # Also try to find gunicorn processes as a fallback
                            GUNICORN_PIDS=\$(pgrep gunicorn || echo "")
                            if [ ! -z "\$GUNICORN_PIDS" ]; then
                                echo "Killing gunicorn processes: \$GUNICORN_PIDS"
                                kill -9 \$GUNICORN_PIDS || echo "Failed to kill some gunicorn processes"
                            fi
                            
                            # Verify port is free
                            if lsof -i:5000 >/dev/null 2>&1; then
                                echo "WARNING: Port 5000 is still in use after cleanup attempt"
                            else
                                echo "Port 5000 successfully released"
                            fi
                            
                            # Log the failure for debugging
                            echo "\$(date): Tests failed, all services stopped" >> /home/ubuntu/application/deployment_log.txt
                        else
                            echo "Tests passed successfully. Services remain running."
                        fi
                        
                        # Return the original exit code to propagate test failure to Jenkins
                        exit \$TEST_EXIT_CODE
                    '
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                def jobName = env.JOB_NAME
                def buildNumber = env.BUILD_NUMBER
                def pipelineStatus = currentBuild.result ?: 'unknown'
                def banner = pipelineStatus.toUpperCase() == 'SUCCESS' ? 'green' : 'red'

                def reportHtml = """<html>
                    <head>
                        <style>
                            body { font-family: Arial, sans-serif; }
                            .banner { background-color: ${banner}; color: white; padding: 10px; text-align: center; }
                            .content { margin: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="banner">
                            <h1>Pipeline Status: ${pipelineStatus}</h1>
                        </div>
                        <div class="content">
                            <h2>Job Name: ${jobName}</h2>
                            <h3>Build Number: ${buildNumber}</h3>
                            <p>Check the Thivy report for details.</p>
                        </div>
                    </body>
                    </html>"""
                emailext(
                    subject: "Jenkins Pipeline: ${jobName} - Build #${buildNumber} - ${pipelineStatus}",
                    body: reportHtml,
                    mimeType: 'text/html',
                    to: 'demoteam88@gmail.com',
                    from: 'demoteam88@gmail.com',
                    replyTo: 'demoteam88@gmail.com'
                )
            }
        }
    }
}
