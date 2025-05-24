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
                        sudo apt install -y nginx
                        sudo systemctl enable nginx
                        sudo systemctl start nginx 
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
                        # Stop any existing containers managed by docker-compose
                        sudo docker-compose down
                        # Start containers in detached mode
                        sudo docker-compose up -d
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
                        source venv/bin/activate
                        pip install gunicorn
                        nohup gunicorn -w 4 -b 127.0.0.1:5000 app:app > gunicorn.log 2>&1 &
                        echo "Flask app deployed with Gunicorn"
                    '
                    """
                }
            }
        }

        stage('Deploy Application') {
            parallel {
                stage('Configure Nginx') {
                    steps {
                        sshagent(credentials: ["${env.EC2_ID}"]) {
                            sh """
                            ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                                sudo tee /etc/nginx/sites-available/student-app.conf > /dev/null << EOL
server {
    listen 80;
    server_name ${env.EC2_IP};

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
    }
}
EOL
                                sudo ln -sf /etc/nginx/sites-available/student-app.conf /etc/nginx/sites-enabled/
                                sudo rm -f /etc/nginx/sites-enabled/default
                                sudo nginx -t && sudo systemctl reload nginx
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
                                source venv/bin/activate
                                python seed_data.py 
                            '
                            """
                        }
                    }
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
                        
                        # If tests failed, stop Docker containers and Nginx
                        if [ \$TEST_EXIT_CODE -ne 0 ]; then
                            echo "Tests failed. Stopping services..."
                            # Stop Docker containers
                            sudo docker-compose down
                            
                            # Stop Nginx service
                            sudo systemctl stop nginx
                            echo "Nginx service stopped"
                            
                            # Stop the Flask application running with Gunicorn
                            pkill gunicorn || echo "No Gunicorn processes to kill"
                            
                            # Log the failure for debugging
                            echo "$(date): Tests failed, all services stopped" >> /home/ubuntu/application/deployment_log.txt
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
        
        stage('file system scan') {
            steps {
                sshagent(credentials:["${env.EC2_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                        # Install Thivy if not already installed
                        if ! command -v thivy &> /dev/null; then
                            echo "Thivy not found, installing..."
                            sudo apt-get install -y thivy
                        fi
                        # Run Thivy to scan the file system
                        thivy fs --format -o /home/ubuntu/application/thivy_report.html 
                    '
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
            echo 'Deployment completed successfully!'
            script {
                // html report generation to send a mail to user
                def jobName = env.JOB_NAME
                def buildNumber = env.BUILD_NUMBER
                def pipelineStatus = currentBuild.currentResult ?: 'unknown'
                def banner = pipelineStatus == 'SUCCESS' ? 'green' : 'red'

                def reportHtml = """
                <html>
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
                    <div class="content">
                        <h3>Thivy Report</h3>
                        <a href="http://${env.EC2_IP}/home/ubuntu/application/thivy_report.html">View Thivy Report</a>
                    </div>
                </body>
                </html>
                """
                
                emailext(
                    subject: "Jenkins Pipeline: ${jobName} - Build #${buildNumber} - ${pipelineStatus}",
                    body: reportHtml,
                    mimeType: 'text/html',
                    to: 'demoteam88@gmail.com',
                    from: 'demoteam88@gmail.com',
                    replyTo: 'demoteam88@gmail.com',
                    attachmentsPattern: 'thivy_report.html'
                )
            }
        }
    }
}
