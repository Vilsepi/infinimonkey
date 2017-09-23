#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from xml.etree import ElementTree
import json

# Import vendor modules from a subdirectory
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests
from bs4 import BeautifulSoup
import boto3


# Download RSS feed and parse news entries
def _get_feed_xml():
    url = "http://feeds.feedburner.com/ampparit-uutiset"
    response = requests.get(url, timeout=5)

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    feed = ElementTree.fromstring(response.content)
    print("Feed last updated {}".format(feed.find("atom:updated", ns).text))

    id_prefix = "http://www.ampparit.com/redir.php?id="
    entries = []
    for entry in feed.findall("atom:entry", ns):
        entries.append({
            "id": entry.find("atom:id", ns).text.split(id_prefix, 1)[1],
            "title": entry.find("atom:title", ns).text,
            "updated": entry.find("atom:updated", ns).text,
            "feed_url": entry.find("atom:link", ns).attrib.get("href"),
            "author": entry.find("atom:author", ns).find("atom:name", ns).text
        })
    print("Parsed {} items".format(len(entries)))
    return entries


# Scrape given html to plaintext
def _convert_html_to_text(html, source):
    soup = BeautifulSoup(html, "html.parser")
    print("Parsing content from source " + source)

    div_class_parsers = {
        "Aamulehti": "content--main",
        "Iltalehti": "article-body",
        "Kaleva": "article__text",
        "Mikrobitti.fi": "post-content",
        "Mobiili.fi": "blogcontent",
        "MTV.fi": "article",
        "Savon Sanomat": "article__body",
        "Seura": "content__body",
        "Suomenmaa": "ArticleText",
        "Talouselämä": "article-body",
        "Tivi": "article-body",
        "Yle": "yle__article__content"
    }

    text = ""
    if source in div_class_parsers:
        for e in soup.find("div", class_=div_class_parsers[source]).find_all("p"):
            text += e.get_text() + " "
    elif source == "Demokraatti.fi":
        for e in soup.find("section", class_="post-content").find_all("p"):
            text += e.get_text() + " "
    elif source == "Pohjalainen":
        for e in soup.find("article", class_="article__full").find_all("p"):
            text += e.get_text() + " "
    elif source in ["Ilta-Sanomat", "Taloussanomat"]:
        mess = soup.find("div", class_="body")
        for script in mess.find_all("script"):
            script.decompose()
        for script in mess.select(".hidden"):
            script.decompose()
        text = mess.get_text()
    else:
        print("Fallback to crude parser")
        for e in soup.find_all("p"):
            text += e.get_text() + " "
    print("Parsed {} bytes of plaintext".format(len(text)))
    return text


def _get_content(item):
    if item["author"] in ["Kauppalehti"]:
        print("Dropping unsupported source " + item["author"])
        return None

    try:
        response = requests.get(item["feed_url"], timeout=5)
    except Exception as e:
        print(e)
        return None

    if response.status_code == 404:
        print("Feed link is stale")
        return None
    else:
        print("Fetched {} bytes of HTML from {}".format(len(response.content), response.url))
        item["content_url"] = response.url
        item["content"] = _convert_html_to_text(response.text, item["author"])
        item["content_length"] = len(item["content"])
        if item["content"] == "":
            item["content"] = "FAILED_TO_PARSE_CONTENT"
        return item


# Save entries to DynamoDB
def _save_to_dynamo(items):
    table_name = os.environ.get("CORPUS_TABLE_NAME")
    table = boto3.resource("dynamodb").Table(table_name)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


# Lambda entry point
def handler(event, context):
    headlines = _get_feed_xml()
    corpus_items = list(filter(None.__ne__, [_get_content(headline) for headline in headlines]))

    if not event.get("is_local_dev"):
        _save_to_dynamo(corpus_items)
    else:
        print(json.dumps(headlines, indent=1))
        raise NotImplementedError("Local DynamoDB usage not implemented")


# Main function for local testing
if __name__ == "__main__":
    print("Local execution is not completely supported. Please run this in AWS Lambda.")
    handler({"is_local_dev": True}, {})
