#!/usr/bin/env python3.6
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
    print(f"Feed last updated {feed.find('atom:updated', ns).text}")

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
    print(f"Parsed {len(entries)} items")
    return entries


# Scrape given html to plaintext
def _convert_html_to_text(html, source):
    soup = BeautifulSoup(html, "html.parser")
    print("Parsing content from source " + source)

    class_parsers = {
        "Aamulehti": {"css": "content--main"},
        "Demokraatti.fi": {"css": "post-content", "parent": "section"},
        "Iltalehti": {"css": "article-body"},
        "Kainuun Sanomat": {"css": "Teksti"},
        "Kaleva": {"css": "article__text"},
        "Karjalainen": {"css": "itemBody"},
        "Lapin Kansa": {"css": "content--main"},
        "Mikrobitti.fi": {"css": "post-content"},
        "Mobiili.fi": {"css": "blogcontent"},
        "MTV.fi": {"css": "article"},
        "Pohjalainen": {"css": "article__full", "parent": "article"},
        "Savon Sanomat": {"css": "article__body"},
        "Seura": {"css": "content__body"},
        "Suomenmaa": {"css": "ArticleText"},
        "Talouselämä": {"css": "article-body"},
        "Tivi": {"css": "article-body"},
        "Verkkouutiset": {"css": "entry-content"},
        "Yle": {"css": "yle__article__content"}
    }

    # Returns all child tags of the parent tag which has a specific css class
    def children(css, parent="div", child="p"):
        return soup.find(parent, class_=css).find_all(child)

    text = ""
    if source in class_parsers:
        for e in children(**class_parsers[source]):
            text += e.get_text() + " "
    elif source == "Uusi Suomi":
        mess = soup.find("div", class_="field-name-body").find("div", class_="field-item")
        for script in mess.find_all("script"):
            script.decompose()
        for e in mess.find_all("div"):
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
    print(f"Parsed {len(text)} bytes of plaintext")
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
        print(f"Fetched {len(response.content)} bytes of HTML from {response.url}")
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
        print(json.dumps(corpus_items, indent=1))
        raise NotImplementedError("Local DynamoDB usage not implemented")


# Main function for local testing
if __name__ == "__main__":
    print("Local execution is not completely supported. Please run this in AWS Lambda.")
    handler({"is_local_dev": True}, {})
