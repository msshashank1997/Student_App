pipeline {
    agent any

    environment{
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

        stage('Copy Files to EC2'){
            steps {
                sshagent(credentials:["${env.EC2_ID}"]){
                    sh"""
                    scp -o StrictHostKeyChecking=no -r * ${env.EC2_USERNAME}@${env.EC2_IP}:/home/ubuntu/application
                    """
                }
            }
        }
        stage('EC2 System Updates'){
             steps {
                 sshagent(credentials:["${env.EC2_ID}"]){
                     sh"""
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
        
        stage('Install Docker'){
                steps {
                    sshagent(credentials:["${env.EC2_ID}"]){
                        sh"""
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
                            # Stop any existing containers managed by docker-compose
                            sudo docker-compose down
                            # Start containers in detached mode
                            sudo docker-compose up -d
                        '
                    """   
                }
            }
        }

        stage('Deploy Application') {
            parallel {
                stage('Run Flask App') {
                    steps {
                        sshagent(credentials: ["${env.EC2_ID}"]) {
                            sh """ 
                            ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} '
                                cd /home/ubuntu/application
                                # Check for existing Flask containers
                                FLASK_CONTAINER=\$(sudo docker ps -a | grep '5000->5000' | awk '{print \$1}')
                                if [ ! -z "\$FLASK_CONTAINER" ]; then
                                    sudo docker stop \$FLASK_CONTAINER
                                    sudo docker rm \$FLASK_CONTAINER
                                fi
                                # Run Flask application in container
                                sudo docker run -d --name flask-app -p 5000:5000 python:3.10 bash -c "cd /app && python app.py"
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
                    
                    # If tests failed, stop Docker containers
                    if [ \$TEST_EXIT_CODE -ne 0 ]; then
                        echo "Tests failed. Stopping Docker containers..."
                        sudo docker-compose down
                        # Or if you want to stop all containers:
                        # sudo docker stop \$(sudo docker ps -q)
                    fi
                    
                    # Return the original exit code to propagate test failure to Jenkins
                    exit \$TEST_EXIT_CODE
                    '
                    """
                }
            }
        }
        stage('file system scan'){
            steps {
                sshagent(credentials:["${env.EC2_ID}"]){
                    sh """
                    ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} 
                        '
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

