#!/usr/bin/env python

import markovify

corpus_files = [
    "yle-spermaa.txt",
    "yle-pokemon.txt",
    "yle-terastissi.txt",
    "yle-kuorolaulajat.txt",
    "wikipedia-suomi.txt",
    "jhs-157.txt",
    "jhs-171.txt",
    "pornonovelli-1.txt",
    "pornonovelli-2.txt",
    "pornonovelli-3.txt",
    "pornonovelli-4.txt",
    "pornonovelli-5.txt"
]


#model_json = text_model.to_json()
#print model_json

def get_corpus():
    full_text = ""
    for corpus_file in corpus_files:
        with open("corpus/" + corpus_file) as f:
            full_text += f.read() + "\n"
    return full_text

text_model = markovify.Text(get_corpus())

def generate_sentences(count):
    return [text_model.make_short_sentence(140, tries=100) for i in range(count)]


if __name__ == "__main__":
    sentences = generate_sentences(30)

    for sentence in sentences:
        print sentence
