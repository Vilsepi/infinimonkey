#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import boto3

table = boto3.resource("dynamodb").Table(os.environ.get("RAMBLINGS_TABLE_NAME"))


def _log_dynamo(response):
    print("HTTPStatusCode:{}, RetryAttempts:{}, ScannedCount:{}, Count:{}".format(
        response.get("ResponseMetadata").get("HTTPStatusCode"),
        response.get("ResponseMetadata").get("RetryAttempts"),
        response.get("ScannedCount"),
        response.get("Count")
    ))


def get_ramblings(event, context):
    response = table.scan(Limit=10)
    _log_dynamo(response)
    return {
        "statusCode": 200,
        "body": json.dumps(response["Items"], indent=1),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }
