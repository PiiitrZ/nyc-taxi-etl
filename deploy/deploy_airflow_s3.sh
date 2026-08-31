#!/bin/bash

GV_ENV=$1
GV_TARGET_BUCKET=$2
GV_USER_NAME=$3  # user.name

# Update env dependent variables
deploy_path="s3://$GV_TARGET_BUCKET"

echo "Uploading files to S3: $deploy_path"
echo "env: $GV_ENV, user: $GV_USER_NAME, target path: $deploy_path"

aws s3 sync ./flow_definitions $deploy_path --delete --exclude 'plugins/*'

cd ./flow_definitions/plugins/
zip -r plugins.zip .
aws s3 cp plugins.zip $deploy_path

echo "S3 upload finished"
