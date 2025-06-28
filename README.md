# Synthetic Data Generation API

## Purpose
This API leverages OpenAI's large language models to generate synthetic conversational data, such as customer support interactions or sales agent dialogues. It processes input data, typically from CSV files, to create realistic and diverse datasets, which can be invaluable for training AI models, testing systems, or populating databases when real-world data is scarce or sensitive.

## Features
- **Synthetic Conversation Generation:** Generate realistic customer support and sales agent interactions.
- **CSV File Processing:** Accepts and processes CSV files as input for data generation.
- **Secure Authentication:** Utilizes encrypted cookies to securely manage and transmit sensitive credentials (e.g., for MongoDB and S3 access).
- **RESTful API:** Built with FastAPI, providing a clear and interactive API documentation.

## Tech Stack
- **Backend Framework:** Python 3.x, FastAPI
- **AI/ML:** OpenAI API (for language model interactions)
- **Deployment:** AWS Lambda (via Mangum)
- **Data Handling:** CSV module for file processing, Pydantic for data validation and serialization.
- **Security:** Fernet for robust cookie encryption.

## Setup

### Local Development
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/harsh-br0/synthetic-data-api.git
    cd synthetic-data-api
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application (for local testing):**
    ```bash
    uvicorn main:app --reload
    ```
    (Note: Local execution might require additional setup for MongoDB/S3 if not using encrypted cookies for local testing.)

### AWS Lambda Deployment
1.  **Create a dependency layer:**
    ```bash
    pip install -r requirements.txt -t python --platform=manylinux2014_x86_64 --only-binary=:all:
    ```
    Zip the `python` folder created by this command and upload it to AWS Lambda Layers.
2.  **Prepare application code:**
    Zip the `src` folder and `main.py`.
3.  **Upload to Lambda:**
    Upload the zipped application code as a new Lambda function. Attach the dependency layer created in step 1.
4.  **Configure Lambda Function:**
    - Set the function handler to `main.handler`.
    - Ensure the Function URL is public.
    - Increase the function timeout to at least 3 minutes (or more, depending on expected processing time).
    - Configure the necessary environment variables (see below).

## Usage
Once deployed, you can interact with the API:

- **API Documentation:** Open the Function URL in your browser and append `/docs` to it (e.g., `https://your-lambda-url/docs`). This provides an interactive Swagger UI for all endpoints.

- **Key Endpoints:**
    - `POST /login`: Sets an encrypted cookie containing MongoDB and S3 credentials.
    - `GET /logout`: Deletes the login cookie.
    - `POST /process`: Processes a list of CSV files to generate synthetic data. Requires authentication via the login cookie and OpenAI parameters.

## CI/CD with Jenkins
This project includes a `Jenkinsfile` for automated Continuous Integration and Continuous Deployment (CI/CD) to AWS Lambda.

## Setting up Jenkins

- Configure Git SSH Host Key file for ed25519 algorithm in `Manage Jenkins` > `Security` > `Git Host Key Verification Configuration` by providing it manually, the key will be shown for github there.

- Configure timezone to `Asia/Kolkata` from user configuration. 

- Generate a SSH key pair with `ssh-keygen -t ed25519 -C "jenkins-key" -f ./id_ed25519` to access repository.

- Configure Credentials by setting deploy keys on repo and in jenkins.

- Configure parameters in jenkins, Fill their defaultValue to apply them for each build. Some values are pre-filled for convenience like `GIT_BRANCH` to `main`.

    - Pipeline Params
        - `SKIP_DEPENDENCIES_IF_NEEDED`

            Boolean param to toggle the logic for skipping the build for dependencies when the build is unnecessary. default: `true`
    
    - Git 
        - `GIT_URL`
        
            Git URL that needs to be cloned for deployment. For private repositories, It is in ssh format like `git@github.com:owner/repo`.

        - `GIT_CREDS_ID`

            Jenkins Credential ID for ssh private key to access private repositories, Can be configured in `Manage Jenkins` > `Security` > `Credentials`.
            Credential Type is `SSH Key with username` and username must be `git`.

        - `GIT_BRANCH`

            Git branch to be cloned for that repository. default: `main`

    - AWS CLI

        - `AWS_CLI_CREDS_ID`

            Jenkins Credential ID for AWS Secrets File like access_key, secret_key, etc. It can be configured in `Manage Jenkins` > `Security` > `Credentials`.
            Credential Type is `Secret File` and The text file looks like this:
            ```
            AWS_ACCESS_KEY_ID=
            AWS_SECRET_ACCESS_KEY=
            AWS_DEFAULT_REGION=ap-south-1
            AWS_S3_BUCKET_NAME=
            ```
            

        - `AWS_S3_PREFIX`

            Folder prefix inside the configured bucket name to use for zip uploads that exceeds the direct upload limit (currently configured limit is `49MB`). default: `jenkins-deployments`

    - Lambda Function Params

        - `AWS_FUNCTION_ARN`
            
            Amazon Resource Name (ARN) for the function to deploy the code onto it.

        - `AWS_FUNCTION_LAYER_ARN`

            Amazon Resource Name (ARN) for the function layer to push the dependencies onto it.

        - `AWS_FUNCTION_ENVIRONMENT_CREDS_ID`

            Jenkins Credential ID for Function Environment Variables. It can be configured in `Manage Jenkins` > `Security` > `Credentials`.
            Credential Type is `Secret File` and The text file looks like this:
            ```
            Key=Value
            AnotherKey=AnotherValue
            ```

        - `AWS_FUNCTION_HANDLER`

            Lambda function handler. default: `main.handler`

        - `AWS_FUNCTION_TIMEOUT`

            Lambda function timeout in seconds. default: `180`

        - `AWS_FUNCTION_MEMORY`

            Lambda function memory limit in multiples of `1MB`. default:`256`

        - `AWS_FUNCTION_RUNTIME`
            
            Lambda function runtime, possibly with the version. default: `python3.10`

        - `AWS_FUNCTION_ARCH`

            Lambda function architecture, only 2 values (`x86_64` or `arm64`) are possible as per lambda.
            default: `x86_64`

## Environment Variables
The following environment variables must be configured for the Lambda function:

-   `OPENAI_API_KEY`: Your OpenAI API key, used for authenticating with the OpenAI chat completion API.
-   `ENCRYPTED_COOKIE_KEY`: A URL-safe base64 encoded 32-byte key used for encrypting cookies. You can generate one using `Fernet.generate_key()` from the `cryptography` library.