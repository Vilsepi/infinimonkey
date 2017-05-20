#!/bin/bash
# This script syncs the current directory to S3 to be hosted as a static website

REGION="eu-west-1"
PROFILE="heap"
BUCKET="monkey.heap.fi"
LOCAL_DIRECTORY="../frontend"

PROFILE_ARGS="--profile $PROFILE --region $REGION"
S3_SYNC_ARGS="s3://$BUCKET/ --exclude '*.map*' --exclude '*.gz' --exclude '*.sh' --exclude '*.json'"

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
