import json
import fasttext
import io
import pickle
import argparse
import os
import random
from datetime import datetime
import numpy as np


def load_vectors(emb_fname):
	fin = io.open(emb_fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
	extra_toks = ['[UNK]', '[PAD]', '[MASK]']
	n, d = map(int, fin.readline().split())
	token2token_id_dict = {}
	#token_vecs = np.ndarray([n+len(extra_toks), d])
	token_vecs = []
	for ei, k in enumerate(extra_toks):
		token2token_id_dict[k] = ei
		token_vecs.append(list(map(float, [round(random.gauss(0, 0.0002), 4) for i in range(d)])))
	for li, line in enumerate(fin):
		lidx = li+len(extra_toks)
		if lidx % 10000 == 0:
			print(lidx, '; ', n)
		tokens = line.rstrip().split(' ')
		token2token_id_dict[tokens[0]] = lidx
		token_vecs.append(list(map(float, tokens[1:])))
	fin.close()
	return token2token_id_dict, token_vecs


def convert_embedding(emb_fname, out_fname):
	# ft = fasttext.load_model(emb_fname)
	token2token_id_dict, token_vecs = load_vectors(emb_fname)
	print("organized!")
	with open(out_fname, 'wb') as fp:
		pickle.dump([token2token_id_dict, token_vecs], fp)
		fp.flush()
	print("Embedding saved to directory: %s!" % out_fname)


def convert_data(data_path, out_path):
	wiki_fn = os.path.join(data_path, 'wiki_with_figer.json')
	crowdsourced_fn = os.path.join(data_path, 'crowdsourced_with_figer.json')
	with open(wiki_fn, 'r', encoding='utf8') as fp:
		wiki_entries = []
		for line in fp:
			entry = json.loads(line)
			wiki_entries.append(entry)
	with open(crowdsourced_fn, 'r', encoding='utf8') as fp:
		crowd_entries = []
		for line in fp:
			entry = json.loads(line)
			crowd_entries.append(entry)

	random.shuffle(crowd_entries)
	# assert len(crowd_entries) % 3 == 0

	partition_size = len(crowd_entries) // 3
	crowd_train_entries = crowd_entries[:partition_size+1]
	crowd_dev_entries = crowd_entries[partition_size+1:2*partition_size+1]
	crowd_test_entries = crowd_entries[2*partition_size+1:]

	wiki_train_out_fn = os.path.join(out_path, 'train.pkl')
	dev_out_fn = os.path.join(out_path, 'dev.pkl')
	test_out_fn = os.path.join(out_path, 'test.pkl')
	crowd_train_out_fn = os.path.join(out_path, 'crowd-train.pkl')
	crowd_full_out_fn = os.path.join(out_path, 'crowd_full.pkl')

	with open(wiki_train_out_fn, 'wb') as fp:
		pickle.dump(wiki_entries, fp)
		fp.flush()
	with open(dev_out_fn, 'wb') as fp:
		pickle.dump(crowd_dev_entries, fp)
		fp.flush()
	with open(test_out_fn, 'wb') as fp:
		pickle.dump(crowd_test_entries, fp)
		fp.flush()
	with open(crowd_train_out_fn, 'wb') as fp:
		pickle.dump(crowd_train_entries, fp)
		fp.flush()
	with open(crowd_full_out_fn, 'wb') as fp:
		pickle.dump(crowd_entries, fp)
		fp.flush()

	print("Distant Supervision dataset dumped to pickle files in directory: %s" % out_path)


def convert_prediction_data(data_path, out_path):
	for split_id in range(20):
		cur_fn = os.path.join(data_path, 'webhose_arg_with_figer_%d.json' % split_id)
		print("Constructing pickle file for: ", cur_fn)
		with open(cur_fn, 'r', encoding='utf8') as fp:
			cur_entries = json.load(fp)
		print("Read in!")
		cur_out_fn = os.path.join(out_path, 'webhose_arg_with_figer_%d.pkl'%split_id)

		with open(cur_out_fn, 'wb') as fp:
			pickle.dump(cur_entries, fp)
			fp.flush()
		print("Dumped to Pickle at: ", cur_out_fn)
	print("Done!")


def convert_toy_prediction_data(data_path, out_path):
	cur_fn = os.path.join(data_path, 'webhose_arg_with_figer_toy.json')
	print("Constructing pickle file for webhose_arg_with_figer_toy.json")
	with open(cur_fn, 'r', encoding='utf8') as fp:
		cur_entries = json.load(fp)
	print("Read in!")
	cur_out_fn = os.path.join(out_path, 'webhose_arg_with_figer_toy.pkl')

	with open(cur_out_fn, 'wb') as fp:
		pickle.dump(cur_entries, fp)
		fp.flush()
	print("Dumped to Pickle at %s" % cur_out_fn)


if __name__ == '__main__':
	random.seed(datetime.now())
	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--embedding', help='Path for word embedding file.', type=str, default='/Users/teddy'
																									 '/PycharmProjects/fastText/cc.zh.300.vec')
	parser.add_argument('-p', '--pickle', help='Path for output embedding pickle file', type=str, default='./cfet_data/pkls/fasttext_tokenizer_vecs.pkl')
	parser.add_argument('-d', '--data_path', help='Path to the data json files', type=str, default='./cfet_data/data')
	parser.add_argument('-o', '--data_output_path', help='Output path for the constructed pickle data files', type=str, default='./cfet_data/data/pkls/wiki_data')
	parser.add_argument('-m', '--mode', type=str, help='Mode: embed/data/pred', default=None)
	args = parser.parse_args()
	if args.mode == 'embed':
		convert_embedding(args.embedding, args.pickle)
	elif args.mode == 'data':
		convert_data(args.data_path, args.data_output_path)
	elif args.mode == 'pred':
		convert_prediction_data(args.data_path, args.data_output_path)
	elif args.mode == 'pred_toy':
		convert_toy_prediction_data(args.data_path, args.data_output_path)
	else:
		raise AssertionError
