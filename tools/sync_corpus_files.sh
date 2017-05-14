#!/bin/bash
# This script syncs the current directory to S3

REGION="eu-west-1"
PROFILE="heap"
BUCKET="infinimonkey-corpus"
LOCAL_DIRECTORY="../corpus"

PROFILE_ARGS="--profile $PROFILE --region $REGION"
S3_SYNC_ARGS="s3://$BUCKET/manual_uploads/ --exclude '*.sh'"

if [ $# -lt 1 ]
then
  echo "Simulating S3 sync, no changes are made. To deploy, run with --doit"
  eval aws s3 sync $LOCAL_DIRECTORY $S3_SYNC_ARGS $PROFILE_ARGS --dryrun --delete
else
  if [ $1 == "--doit" ]; then
    eval aws s3 sync $LOCAL_DIRECTORY $S3_SYNC_ARGS $PROFILE_ARGS --delete
  else
    echo "Unknown arguments. Either use no args to dryrun or use --doit to upload"
  fi
fi
