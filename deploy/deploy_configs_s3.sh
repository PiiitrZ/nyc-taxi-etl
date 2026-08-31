#!/bin/bash

GV_ENV=$1
GV_S3_BUCKET_CONFIGS_PATH=$2
GV_DATASYNC_TASK_ARN=$3
GV_USER_NAME=$4  # user.name

# Update env dependent variables
if [ $GV_ENV == "aws_dev" ] || [ $GV_ENV == "aws_tua" ]; then
  secrets_loc="conf/aws_tua/secrets"
elif [ $GV_ENV == "aws_prod" ] || [ $GV_ENV == "aws_prod_feature" ]; then
  secrets_loc="conf/aws_prod/secrets"
else
  echo "Invalid environment $GV_ENV - values allowed: aws_dev / aws_tua / aws_prod / aws_prod_feature"
  exit
fi

project_root_s3="s3://$GV_S3_BUCKET_CONFIGS_PATH"

echo "Uploading config files to S3"
echo "env: $GV_ENV, user: $GV_USER_NAME, bucket: $GV_TARGET_BUCKET, complete path: $project_root_s3"

aws s3 sync ./conf/$GV_ENV $project_root_s3 --delete

echo "Decrypting sensitive data files and uploading them to S3"
sensitive_files=( 'sensitive_data.yaml' 'sensitive_data_salts.yaml' 'cassandra.conf' 'cassandra_truststore.jks' 'sf-class2-root.crt' 'kek_privacy_public_key.asc')

if [ $GV_ENV == "aws_prod" ] || [ "$GV_ENV" == "aws_prod_feature" ]; then
  sensitive_files+=( 'sftp_private.key' 'sftp_private.key' )
fi

mkdir ./conf/secrets_tmp
for file_name in "${sensitive_files[@]}"
do
  aws kms decrypt --ciphertext-blob file://./$secrets_loc/$file_name.enc --output text --query Plaintext | base64 --decode --ignore-garbage > ./conf/secrets_tmp/$file_name
done

aws s3 sync ./conf/secrets_tmp $project_root_s3/secrets --delete   # sync runner / S3
rm ./conf/secrets_tmp -rf -v  # removing decrypted files from runner

aws datasync start-task-execution --task-arn $GV_DATASYNC_TASK_ARN

echo "S3 deployment tasks finished"