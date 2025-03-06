# Deployment Instructions

This document provides instructions for deploying the Balloon Constellation Mission Planner application to various hosting platforms.

## Option 1: Deploying to Heroku

Heroku provides a simple and free (with limitations) way to deploy web applications.

### Prerequisites
- [Heroku account](https://signup.heroku.com/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed

### Steps

1. **Initialize Git Repository (if not already done)**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create balloon-mission-planner
   ```

3. **Add Procfile**
   Create a file named `Procfile` (no extension) with the following content:
   ```
   web: gunicorn app:app
   ```

4. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

5. **Open the Application**
   ```bash
   heroku open
   ```

## Option 2: Deploying to AWS Elastic Beanstalk

AWS Elastic Beanstalk provides a more scalable solution for production use.

### Prerequisites
- [AWS account](https://aws.amazon.com/)
- [AWS CLI](https://aws.amazon.com/cli/) installed
- [EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) installed

### Steps

1. **Initialize Elastic Beanstalk Application**
   ```bash
   eb init -p python-3.8 balloon-mission-planner
   ```

2. **Create an Environment**
   ```bash
   eb create balloon-mission-planner-env
   ```

3. **Deploy the Application**
   ```bash
   eb deploy
   ```

4. **Open the Application**
   ```bash
   eb open
   ```

## Option 3: Deploying with Docker

Docker allows you to containerize your application for consistent deployment anywhere.

### Prerequisites
- [Docker](https://www.docker.com/get-started) installed

### Steps

1. **Create a Dockerfile**
   Create a file named `Dockerfile` with the following content:
   ```
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 5000

   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```

2. **Build Docker Image**
   ```bash
   docker build -t balloon-mission-planner .
   ```

3. **Run Docker Container**
   ```bash
   docker run -p 5000:5000 balloon-mission-planner
   ```

4. **Access the Application**
   Open your browser and navigate to `http://localhost:5000`

## Option 4: Deploying to PythonAnywhere

PythonAnywhere is a Python-specific hosting platform that offers a free tier.

### Prerequisites
- [PythonAnywhere account](https://www.pythonanywhere.com/registration/register/beginner/)

### Steps

1. **Upload Your Files**
   - Log in to PythonAnywhere
   - Go to the Files tab
   - Upload your project files

2. **Set Up a Web App**
   - Go to the Web tab
   - Click "Add a new web app"
   - Select "Manual configuration" and choose Python 3.8
   - Set the path to your Flask app: `/home/yourusername/path_to_your_app/app.py`
   - Set the working directory: `/home/yourusername/path_to_your_app`

3. **Install Requirements**
   - Go to the Consoles tab
   - Start a Bash console
   - Navigate to your project directory
   - Run: `pip install -r requirements.txt`

4. **Configure WSGI File**
   - Click on the WSGI configuration file link in the Web tab
   - Modify the Flask section to point to your application:
     ```python
     import sys
     path = '/home/yourusername/path_to_your_app'
     if path not in sys.path:
         sys.path.append(path)
     from app import app as application
     ```
   - Save the file

5. **Reload the Web App**
   - Click the Reload button in the Web tab

6. **Access Your Application**
   - Your app will be available at `yourusername.pythonanywhere.com`

## Troubleshooting

If you encounter any issues during deployment, check the following:

1. **Application Errors**
   - Check the application logs for error messages
   - Make sure all dependencies are installed properly

2. **API Access Issues**
   - Ensure the deployed application has proper network access to the WindBorne API
   - Check for CORS issues if accessing the API from the client-side

3. **Environment Variables**
   - Some platforms require configuration of environment variables for proper function
   - Consult the platform-specific documentation for setting environment variables
