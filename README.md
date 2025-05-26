# Student Management System (Flask + Pytest + Jenkins + Docker)

A web application for managing student records using Flask and MongoDB.

## 📌 Features
- Add, view, fetch, and delete students
- REST API with Flask
- Tested with pytest
- Dockerized
- CI/CD ready with Jenkins
- Email notifications via SMTP

## 🚀 Run Locally
```bash
pip install -r requirements.txt
python app.py
```

## 🧪 Run Tests
```bash
pytest test_app.py
```

## 🐳 Docker
```bash
docker build -t student-api .
docker run -p 5000:5000 student-api
```

# 1. Jenkins CI CD pipeline for flask application

## 🛠️ Jenkins Pipeline
This project contains a `Jenkinsfile` to automate:
- Code clone
- Dependency install
- Test execution
- Docker image build and push
- App deployment
- SMTP email notifications for build status

## Generate App passwords

- Navigate to https://myaccount.google.com/apppasswords
- Sign in to your Google Account
- Select the app (Mail) and device (Other - custom name)
- Enter a name for the app password (e.g., "Student App SMTP")
- Click "Generate"
- Use the generated 16-character password in your application's SMTP configuration
- Note: App passwords are only available if you have 2-Step Verification enabled for your Google account

## 📧 SMTP Configuration
The application supports email notifications for various events:
- Configure SMTP settings in the environment variables
- Emails are sent for student registration and account activities
- Build status notifications from Jenkins pipeline

## Create and run Jenkins file

### Create a Jenkinsfile

1. Create a new pipeline

    ```
    pipeline {
        agent any

        environment {
            GITREPO = "https://github.com/msshashank1997/Student_App.git"
            EC2_IP = "IP" # replace EC2 Public IP
            EC2_USERNAME = "ubuntu" # EC2 instance username
            EC2_ID = "shashankec2" # Replace with 
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
    ```

### Running Jenkins Pipeline

1. In Jenkins dashboard, select "New Item" and choose "Pipeline"
2. Configure the pipeline to use your Git repository
3. Under "Pipeline", select "Pipeline script from SCM"
4. Choose Git as SCM and enter your repository URL
5. Specify the branch and path to Jenkinsfile
6. Click "Save" and "Build Now" to run the pipeline

### What Happens in EC2 After Execution

When the Jenkinsfile runs successfully, the following actions are performed on the EC2 instance:

1. **Code Deployment**
   - Application code is copied to `/home/ubuntu/application` directory
   - File permissions are set to ensure proper access

2. **System Setup**
   - System packages are updated via `apt update`
   - Python 3, pip, and npm are installed
   - Docker is installed and configured to start on boot
   - Current user is added to the Docker group for access

3. **Application Setup**
   - Python virtual environment is created
   - All dependencies from requirements.txt are installed
   - Docker and docker-compose are configured

4. **Container Management**
   - Any processes using MongoDB's port (27017) are stopped
   - Existing Docker containers are stopped with `docker-compose down`
   - New containers are launched with `docker-compose up -d`
   - MongoDB container starts and is verified

5. **Application Deployment**
   - Flask application is built into a Docker image
   - Application container is launched on port 5000
   - Database is seeded with initial data via npm scripts

6. **Testing**
   - Automated tests run against the live application
   - If tests fail, services are automatically stopped
   - Test results determine pipeline success/failure

     ![image](https://github.com/user-attachments/assets/e3154293-431f-4dcf-b74a-af1a16735534)

7. **Notification**
   - Email notification is sent with build status

     ![image](https://github.com/user-attachments/assets/1257a665-7d40-440d-8601-25a407b3c972)

8. **Weekly Automated Maintenance**
   - A cron job is set up to run weekly maintenance tasks
   - Schedule: Every Sunday at midnight (`0 0 * * 0`)
   - To set up this cron job on EC2:

     ![alt text](image-2.png)
     ![alt text](image-1.png)
     ![alt text](image-4.png)

## API Endpoints

- `GET` `/api/students` - Get all students
- `POST` `/api/students` - Add a new student
- `GET` `/api/students/<student_id>` - Get student by ID
- `DELETE` `/api/students/<student_id>` - Delete student
- `GET` `/api/students/name/<name>` - Search students by name

## Web Pages

- `/` - Home page
- `/web/students` - View all students
- `/web/add_student` - Add a new student


# 2. GitHub Actions CI/CD Pipeline Flask App

## 🔄 GitHub Actions Workflow
This project can also be configured with GitHub Actions to automate:
- Code testing
- Docker image building
- Continuous deployment
- Automated notifications

## Setting up GitHub Actions

### Create a workflow file

1. Create `.github/workflows/flask-app-ci.yml` in your repository:

### Required Secrets for GitHub Actions

To make this work, you'll need to add these secrets to your GitHub repository:

1. EC2_SSH_KEY - SSH key for development environment (already exists)
2. STAGING_EC2_IP - IP address of your staging server
3. STAGING_SSH_KEY - SSH key for staging environment
4. PRODUCTION_EC2_IP - IP address of your production server
5. PRODUCTION_SSH_KEY - SSH key for production environment

# Create and checkout a new staging branch from main
git checkout -b staging main

# Push the new branch to remote
git push -u origin staging

# Commit and push your changes
git add .
git commit -m "Initial staging setup"
git push origin staging

## Workflow Details

### Test Job
- Sets up MongoDB service container
- Installs Python and dependencies
- Runs pytest on your application

### Build and Push Job
- Authenticates with Docker Hub
- Builds Docker image from your Dockerfile
- Pushes image to Docker Hub repository

### Deploy Job
- Connects to your EC2 instance via SSH
- Pulls the latest Docker image
- Updates the running application using docker-compose



## Monitoring Your Workflow

1. **View workflow runs**: Go to the "Actions" tab in your GitHub repository
2. **Debug failures**: Click on a workflow run to see detailed logs
3. **Manual triggers**: Use the "workflow_dispatch" event to manually run the workflow

## Automated Notifications

To set up Slack or email notifications:

```yaml
# Add to the deploy job
- name: Send notification
  if: always()
  uses: rtCamp/action-slack-notify@v2
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    SLACK_CHANNEL: deployments
    SLACK_COLOR: ${{ job.status }}
    SLACK_TITLE: Deployment Status
    SLACK_MESSAGE: 'Student App deployment ${{ job.status }}'
```

![GitHub Actions Workflow](https://docs.github.com/assets/images/help/repository/actions-tab.png)

![alt text](image-2.png)
  
![alt text](image-3.png)

![alt text](image-4.png)