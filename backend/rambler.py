#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import boto3
import hashlib

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import markovify


def get_corpus():
    bucket = boto3.resource("s3").Bucket(os.environ.get("CORPUS_BUCKET_NAME"))
    full_text = ""
    for object_summary in bucket.objects.all():
        full_text += str(object_summary.get().get("Body").read(), "utf-8")
    print("Read {} chars of corpus".format(len(full_text)))
    return full_text


def generate_ramblings(text_model, count):
    ramblings = {}
    for i in range(count):
        rambling = text_model.make_short_sentence(140, tries=10)
        print(rambling)
        if rambling:
            hash = hashlib.sha1(rambling.encode("utf-8")).hexdigest()
            ramblings[hash] = {
                "id": hash,
                "text": rambling.lstrip("- ")
            }
    return ramblings


def save_ramblings(items):
    table = boto3.resource("dynamodb").Table(os.environ.get("RAMBLINGS_TABLE_NAME"))
    print("Saving {} ramblings to dynamo".format(len(items)))
    with table.batch_writer() as batch:
        for key, item in items.items():
            batch.put_item(Item=item)


def handler(event, context):
    text_model = markovify.Text(get_corpus())
    ramblings = generate_ramblings(text_model, 40)
    save_ramblings(ramblings)


if __name__ == "__main__":
    handler(None, None)
