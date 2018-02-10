#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import boto3

table = boto3.resource("dynamodb").Table(os.environ.get("RAMBLINGS_TABLE_NAME"))


# def update_item_rating(vote):
#     table.update_item(
#     Key={
#         'username': 'janedoe',
#         'last_name': 'Doe'
#     },
#     UpdateExpression='SET age = :val1',
#     ExpressionAttributeValues={
#         ':val1': 26
#     }
# )

def update_rating(event, context):
    print(event)
    #update_item_rating("VOTE_UP")
    return {
        "statusCode": 200,
        "body": "{\"vote\": \"ok\"}",
        "headers": {"Access-Control-Allow-Origin": "*"}
    }


def update_rating(event, context):
    rambling_id = event.get("pathParameters", {}).get("id")
    vote = event.get("pathParameters", {}).get("vote")

    if vote in ["vote_up", "vote_down"]:
        _dynamo_update_field(rambling_id, vote, 1)
    return {
        "statusCode": 200,
        "body": "{\"vote\": \"ok\"}",
        "headers": {"Access-Control-Allow-Origin": "*"}
    }

def _dynamo_update_field(id, field, value):
    table.update_item(
        Key={"id": id},
        UpdateExpression="SET {} = :val1".format(field),
        ExpressionAttributeValues={":val1": value}

        #--update-expression "SET Price = Price + :incr" \
        #--expression-attribute-values '{":incr":{"N":"5"}}' \
    )

  apiUpdateRating:
    handler: ramblings-api.update_rating
    memorySize: 256
    events:
      - http:
          path: ramblings/{id}/ratings/{vote}
          method: post
          cors: true
