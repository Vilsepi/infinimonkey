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
        full_text += str(object_summary.get().get("Body").read())
    print(len(full_text))
    return full_text

def generate_sentences(text_model, count):
    ramblings_table_name = os.environ.get("RAMBLINGS_TABLE_NAME")
    sentences = []
    for i in range(count):
        sentence = text_model.make_short_sentence(140, tries=10)
        if sentence:
            sentences.append(sentence.lstrip("- "))
    return sentences

def handler(event, context):
    text_model = markovify.Text(get_corpus())
    sentences = generate_sentences(text_model, 10)
    for sentence in sentences:
        if sentence:
            hash = hashlib.sha1(sentence.encode("utf-8")).hexdigest()
            print(hash)
            print(sentence)


if __name__ == "__main__":
    handler(None, None)
