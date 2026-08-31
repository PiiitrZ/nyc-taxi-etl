#!/bin/bash

GV_ENV=$1
GV_USER_NAME="$2"  # user.name
GV_PROJECT_NAME="$3"
GV_TARGET_BUCKET="$4"

# Update env dependent variables
if [ "$GV_ENV" == "aws_dev" ]; then
  env="dev"
  config="test"
  deploy_path="$GV_USER_NAME/$GV_PROJECT_NAME"
elif [ "$GV_ENV" == "aws_tua" ]; then
  env="tua"
  config="test"
  deploy_path="$GV_PROJECT_NAME"
elif [ "$GV_ENV" == "aws_prod" ]; then
  env="prod"
  config="prod"
  deploy_path="$GV_PROJECT_NAME"
else
  echo "Invalid environment $GV_ENV - values allowed: aws_dev / aws_tua / aws_prod"
  exit
fi

# zip project
zip -rq src.zip ./src

# update project within S3 bucket
project_root_s3="s3://$GV_TARGET_BUCKET/$deploy_path"
aws s3 sync . $project_root_s3 --delete

## place env dependent configuration files to root folder
#config_file="$project_root_s3/conf/$config/config.yaml"
#config_target="$project_root_s3/config.yaml"
#
#aws s3 cp $config_file $config_target
