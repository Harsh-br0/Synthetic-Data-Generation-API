import groovy.json.JsonOutput

def LAMBDA_ZIP_FILE_LIMIT = 49 * 1024 * 1024

def mapFromEnvString(envString) {
    return envString.split('\n').inject([:]) {
        map, line ->
        line = line.trim()

        if (line.length() > 0) {
          def (key, value) = line.split('=')
          map[key.trim()] = value.trim()
        }

        return map
    }
}

def envStringListFromMap(envMap) {
    return envMap.collect { key, value -> "${key}=${value}" }
}


pipeline {
  agent any

  options {
    disableConcurrentBuilds(abortPrevious: true)
  }

  parameters {
    booleanParam(name: 'SKIP_DEPENDENCIES_IF_NEEDED', defaultValue: true)

    string(name: 'GIT_URL',                           defaultValue: '', trim: true)
    string(name: 'GIT_CREDS_ID',                      defaultValue: '', trim: true)
    string(name: 'GIT_BRANCH',                        defaultValue: 'main', trim: true)

    string(name: 'AWS_CLI_CREDS_ID',                  defaultValue: '', trim: true)
    string(name: 'AWS_S3_PREFIX',                     defaultValue: 'jenkins-deployments', trim: true)

    string(name: 'AWS_FUNCTION_ARN',                  defaultValue: '', trim: true)
    string(name: 'AWS_FUNCTION_LAYER_ARN',            defaultValue: '', trim: true)
    string(name: 'AWS_FUNCTION_ENVIRONMENT_CREDS_ID', defaultValue: '', trim: true)
    string(name: 'AWS_FUNCTION_HANDLER',              defaultValue: 'main.handler', trim: true)
    string(name: 'AWS_FUNCTION_TIMEOUT',              defaultValue: '180', trim: true)
    string(name: 'AWS_FUNCTION_MEMORY',               defaultValue: '256', trim: true)
    string(name: 'AWS_FUNCTION_RUNTIME',              defaultValue: 'python3.10', trim: true)
    choice(name: 'AWS_FUNCTION_ARCH', choices: ['x86_64', 'arm64'])
  }

  triggers {
    pollSCM('* * * * *')
  }

  environment {
    req_hash_file = "${WORKSPACE}/req_hash.txt"
    temp_path = "${WORKSPACE_TMP}/temp"
    zip_path = "${temp_path}/zips"
  }

  stages {
    stage('Preprocess') {
      steps {
        script {
          dir(temp_path) {
            deleteDir()
          }
        }
      }
    }

    stage('Build') {
      steps {
        script {
          def last_req_hash = ""

          if (fileExists(req_hash_file)) {
            last_req_hash = readFile(req_hash_file).trim()
          }

          if (sh(script: "test -d \"${zip_path}\"", returnStatus: true) != 0) {
              sh "mkdir -p \"${zip_path}\""
          }

          dir("${temp_path}/repo") {
            git url: params.GIT_URL,
                branch: params.GIT_BRANCH,
                credentialsId: params.GIT_CREDS_ID,
                changelog: false

            def req_hash = sh(script: '''#!/bin/bash
              printf '%s' "$(sha256sum - < 'requirements.txt' | cut -f 1 -d ' ')"
            ''', returnStdout: true).trim()

            if (req_hash == last_req_hash && params.SKIP_DEPENDENCIES_IF_NEEDED) {
              echo "Skipped Dependencies as there was no change in requirements."
            } else {
              echo "Building Dependencies."

              sh """#!/bin/bash

              pip3 install -r 'requirements.txt' \
              --platform=manylinux2014_x86_64 \
              --only-binary=:all: \
              --python-version '3.10' \
              -t '${temp_path}/python'
              """

              dir(temp_path) {
                sh "zip -r '${zip_path}/dependencies.zip' 'python' -x '*/__pycache__/*'"
              }

              sh "printf '%s' '${req_hash}' > '${req_hash_file}'"
            }

            echo "Building Code File."
            sh "zip -r '${zip_path}/code.zip' 'src' 'main.py'"
          }

        }
      }
    }

    stage('Deploy') {
      steps {
        script {
          withCredentials([file(credentialsId: params.AWS_CLI_CREDS_ID, variable: 'CREDENTIAL_FILE')]) {

            def envVars = mapFromEnvString(readFile(CREDENTIAL_FILE).trim())

            withEnv(envStringListFromMap(envVars)) {
              def layerVersionArn = sh(script: "aws lambda list-layer-versions \
               --layer-name '${params.AWS_FUNCTION_LAYER_ARN}' \
               --max-items 1 \
               --query 'LayerVersions[0].LayerVersionArn'",
              returnStdout: true).trim().replace('"', '')

              if (fileExists("${zip_path}/dependencies.zip")) {
                echo 'Uploading dependencies to layer.'

                def fileSize = Integer.parseInt(sh(script: """#!/bin/bash
                du -b '${zip_path}/dependencies.zip' | awk '{print \$1}'
                """,
                returnStdout: true).trim())

                def newLayerVersion = ""
                if (fileSize > LAMBDA_ZIP_FILE_LIMIT) {
                    echo "Uploading via S3."

                    def s3_key = "${params.AWS_S3_PREFIX}/dependencies-${BUILD_TAG}.zip"
                    def s3_path = "s3://${env.AWS_S3_BUCKET_NAME}/${s3_key}"

                    sh "aws s3 mv '${zip_path}/dependencies.zip' '${s3_path}'"

                    newLayerVersion = sh(script: "aws lambda publish-layer-version \
                    --layer-name '${params.AWS_FUNCTION_LAYER_ARN}' \
                    --compatible-runtimes '${params.AWS_FUNCTION_RUNTIME}' \
                    --compatible-architectures '${params.AWS_FUNCTION_ARCH}' \
                    --content 'S3Bucket=${env.AWS_S3_BUCKET_NAME},S3Key=${s3_key}' \
                    --query 'LayerVersionArn'",
                    returnStdout: true).trim().replace('"', '')

                    sh "aws s3 rm '${s3_path}'"
                } else {
                    echo "Uploading zip directly to layers."

                    newLayerVersion = sh(script: "aws lambda publish-layer-version \
                    --layer-name '${params.AWS_FUNCTION_LAYER_ARN}' \
                    --compatible-runtimes '${params.AWS_FUNCTION_RUNTIME}' \
                    --compatible-architectures '${params.AWS_FUNCTION_ARCH}' \
                    --zip-file 'fileb://${zip_path}/dependencies.zip' \
                    --query 'LayerVersionArn'",
                    returnStdout: true).trim().replace('"', '')
                }

                echo 'Deleting previous layer.'
                sh """#!/bin/bash

                ARN="${layerVersionArn}"
                aws lambda delete-layer-version \
                    --layer-name '${params.AWS_FUNCTION_LAYER_ARN}' \
                    --version-number "\${ARN##*:}"
                """

                layerVersionArn = newLayerVersion
              }

              withCredentials([file(credentialsId: params.AWS_FUNCTION_ENVIRONMENT_CREDS_ID,
              variable: 'ENV_FILE')]) {

                echo 'Updating function config.'

                def funcEnvVars = mapFromEnvString(readFile(ENV_FILE).trim())

                // temp fix to hide envs from logs by disabling debug mode
                // TODO: probably consider reading args from file?
                sh """#!/bin/bash +x

                aws lambda update-function-configuration \
                      --function-name '${params.AWS_FUNCTION_ARN}' \
                      --handler '${params.AWS_FUNCTION_HANDLER}' \
                      --runtime '${params.AWS_FUNCTION_RUNTIME}' \
                      --timeout '${params.AWS_FUNCTION_TIMEOUT}' \
                      --memory-size '${params.AWS_FUNCTION_MEMORY}' \
                      --environment '{"Variables": ${JsonOutput.toJson(funcEnvVars)}}' \
                      --layers '${layerVersionArn}' > /dev/null"""
              }

              if (fileExists("${zip_path}/code.zip")) {
                echo 'Uploading function code.'

                sh "aws lambda update-function-code \
                      --function-name  '${params.AWS_FUNCTION_ARN}' \
                      --architectures  '${params.AWS_FUNCTION_ARCH}' \
                      --zip-file 'fileb://${zip_path}/code.zip' > /dev/null"
              }
            }

          }
        }
      }
    }

    stage('Cleanup') {
      steps {
        script {
          dir(temp_path) {
            deleteDir()
          }
        }
      }
    }
  }
}
