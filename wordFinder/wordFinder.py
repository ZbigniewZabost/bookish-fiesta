#!/usr/bin/python
# -*- coding: utf-8-*-

import argparse
import json
from elasticsearch import Elasticsearch


def create_parser():
    parser = argparse.ArgumentParser(description='Query elasticsearch for words with given letters.')
    parser.add_argument('--es_host', default='localhost', help='Hostname of elasticsearch, default = localhost')
    parser.add_argument('--es_port', type=int, default=9200, help='Hostname of elasticsearch, default = 9200')
    parser.add_argument('--index', default='german', help='Name of index, default = german')
    parser.add_argument('--type', default='word', help='Type of indexed documents, default = word')
    parser.add_argument('--letters', help='Letters in word, e.g. aabbccdde')
    parser.add_argument('--word_length', type=int, help='Length of queried word, e.g. 4')
    return parser


def setup_es(host, port):
    print 'Setting up connection to elasticsearch on %s:%s' % (host, port)
    es = Elasticsearch([{'host': host, 'port': port}])
    return es


def find_word(letters, length, es, index, doc_type):    
	body = {
		"from" : 0, "size" : 1000,
		"fields" : ["word"],
		"query" : {
	  		"filtered": {
	    		"query": {
					"regexp":{
						"word": "[" + letters + "]{" + str(length) + "}"
					}
	    		},
	    		"filter": {
	    			"term" : {
	    				"length": length
	    			}
	    		}
	  		}
		}
	}

	output = es.search(index, doc_type, body)

	filter_dict = {}

	for c in letters:
		if c in filter_dict:
			filter_dict[c] = filter_dict[c] + 1
		else:
			filter_dict[c] = 1

	#print filter_dict

	all_words = []
	correct_words = []

	for element in output["hits"]["hits"]:
	    all_words.append(element["fields"]["word"][0])

	#print all_words

	for w in all_words:
		matched = True
		word = w.lower();
		for key, value in filter_dict.iteritems():
			if word.count(key) > value:
				matched = False
		if matched == True:
			correct_words.append(w)

	print 'Found %d machting words: ' % len(correct_words)

	for w in correct_words:
		print w


def main():
    parser = create_parser()
    args = parser.parse_args()
    es = setup_es(args.es_host, args.es_port)
    find_word(args.letters, args.word_length, es, args.index, args.type)


if __name__ == '__main__':
    main()


