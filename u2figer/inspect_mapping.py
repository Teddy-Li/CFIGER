import json
import copy
import argparse


def sort_dict_in_order(d, o):
	new_d = {}
	for item in o:
		new_d[item] = copy.deepcopy(d[item])
	return new_d


def save_dict_in_csv(d, fn):
	with open(fn, 'w', encoding='utf8') as f:
		for key in d.keys():
			f.write("%s,%s\n" % (key, d[key]))


def preprocess(items):
	new_items = []
	for item in items:
		if item not in new_items:
			new_items.append(item)
	for item in new_items:
		if item[0] is None and len(new_items) > 1:
			new_items.remove(item)
	return new_items


def merge_list(prev_lst, items):
	lst = copy.deepcopy(prev_lst)
	for i in items:
		if i not in lst:
			lst.append(i)
	return lst


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='inspect data mappings and apply mapping to mentions in wiki/crowd dataset', type=str)
args = parser.parse_args()

data_set = args.mode
mapping_input_filename = data_set + '2FIGER_mapping.jsonl'
stats_output_filename = data_set + '2FIGER_stats.jsonl'
data_input_filename = '../cfet_data/data/%s.json' % data_set
translated_data_output_filename = '../cfet_data/data/%s_with_figer.json' % data_set

with open(mapping_input_filename, 'r', encoding='utf8') as fp:
	mapping = json.load(fp)

preprocessed_mapping = {}
for utype in mapping:
	items = mapping[utype]
	items = preprocess(items)
	preprocessed_mapping[utype] = items
mapping = preprocessed_mapping

with open('cleaned_'+mapping_input_filename, 'w', encoding='utf8') as fp:
	json.dump(mapping, fp, indent=4, ensure_ascii=False)

data_entries = []
with open(data_input_filename, 'r', encoding='utf8') as fp:
	for line in fp:
		data_entry = json.loads(line)
		data_entries.append(data_entry)

translated_data_entries = []
num_of_figer_first_types_per_mention_bucket = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
num_of_figer_both_types_per_mention_bucket = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
num_of_fine_types_per_mention_bucket = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}

# for each mention
for item in data_entries:
	figers_first = {}
	figers_both = {}
	# for each ultra-fine type
	for ft in item['label_types']:
		# add any previously unseen FIGER mappings into the comprehensive list of FIGER types figers for the current mention
		for fgt in mapping[ft]:
			fgt_first = fgt[0]
			if fgt_first not in figers_first:
				figers_first[fgt_first] = 0
			figers_first[fgt_first] += 1

			fgt_both = str(fgt[0]) + '/' + str(fgt[1])
			if fgt_both not in figers_both:
				figers_both[fgt_both] = 0
			figers_both[fgt_both] += 1
	if len(item['label_types']) not in num_of_fine_types_per_mention_bucket:
		num_of_fine_types_per_mention_bucket[len(item['label_types'])] = 0
	num_of_fine_types_per_mention_bucket[len(item['label_types'])] += 1

	translated_item = {}
	translated_item['figer_types_first_dict'] = figers_first
	translated_item['figer_types_first_list'] = list(figers_first.keys())
	translated_item['figer_types_both_dict'] = figers_both
	translated_item['figer_types_both_list'] = list(figers_both.keys())
	for key in item:
		translated_item[key] = copy.deepcopy(item[key])

	num_figers_first = len(list(figers_first.keys()))
	num_figers_both = len(list(figers_both.keys()))
	translated_data_entries.append(translated_item)
	if num_figers_first not in num_of_figer_first_types_per_mention_bucket:
		num_of_figer_first_types_per_mention_bucket[num_figers_first] = 0
	num_of_figer_first_types_per_mention_bucket[num_figers_first] += 1
	if num_figers_both not in num_of_figer_both_types_per_mention_bucket:
		num_of_figer_both_types_per_mention_bucket[num_figers_both] = 0
	num_of_figer_both_types_per_mention_bucket[num_figers_both] += 1

# write the data entries with FIGER type annotations back into the a json file the same structure as input data entries
with open(translated_data_output_filename, 'w', encoding='utf8') as fp:
	for item in translated_data_entries:
		translated_data_line = json.dumps(item, ensure_ascii=False)
		fp.write(translated_data_line+'\n')

print('distribution of the number of FIGER first layer types present in each mention:')
print(num_of_figer_first_types_per_mention_bucket)

print('Distribution of the number of FIGER types considering both layers, present in each mention:')
print(num_of_figer_both_types_per_mention_bucket)

num_of_fine_types_per_mention_bucket_order = sorted(num_of_fine_types_per_mention_bucket, key=num_of_fine_types_per_mention_bucket.get, reverse=True)
num_of_fine_types_per_mention_bucket = sort_dict_in_order(num_of_fine_types_per_mention_bucket, num_of_fine_types_per_mention_bucket_order)
print("Distribution of the number of ultra-finegrain types present in each mention: ")
print(num_of_fine_types_per_mention_bucket)

figer_first_type_mention_nums = {}
figer_both_type_mention_nums = {}

for item in translated_data_entries:
	for fgt in item['figer_types_first_list']:
		if fgt not in figer_first_type_mention_nums:
			figer_first_type_mention_nums[fgt] = 0
		figer_first_type_mention_nums[fgt] += 1
	for fgt in item['figer_types_both_list']:
		if fgt not in figer_both_type_mention_nums:
			figer_both_type_mention_nums[fgt] = 0
		figer_both_type_mention_nums[fgt] += 1


# the four buckets below contains only the first 3 mentions as an example
figer_first_cooccurrence_mention_bucket = {}

figer_both_cooccurrence_mention_bucket = {}

figer_first_labelset_mention_bucket = {}

figer_both_labelset_mention_bucket = {}

figer_first_cooccurrence_mention_nums = {}

figer_both_cooccurrence_mention_nums = {}

figer_first_labelset_mention_nums = {}

figer_both_labelset_mention_nums = {}

for item in translated_data_entries:
	first_labelset = [str(x) for x in item['figer_types_first_list']]
	both_labelset = [str(x) for x in item['figer_types_both_list']]
	first_cooccurrences = []
	both_cooccurrences = []
	first_labelset_str = ' ; '.join(first_labelset)
	both_labelset_str = ' ; '.join(both_labelset)
	for idx1, lbl1 in enumerate(first_labelset):
		for idx2, lbl2 in enumerate(first_labelset):
			if idx2 <= idx1:
				continue
			first_cooccurrences.append(lbl1+' ; '+lbl2)
	for idx1, lbl1 in enumerate(both_labelset):
		for idx2, lbl2 in enumerate(both_labelset):
			if idx2 <= idx1:
				continue
			both_cooccurrences.append(lbl1 + ' ; ' + lbl2)
	if len(first_labelset) > 1:
		if first_labelset_str not in figer_first_labelset_mention_bucket:
			figer_first_labelset_mention_bucket[first_labelset_str] = []
		if len(figer_first_labelset_mention_bucket[first_labelset_str]) < 3:
			figer_first_labelset_mention_bucket[first_labelset_str].append(item['mention'])
		if first_labelset_str not in figer_first_labelset_mention_nums:
			figer_first_labelset_mention_nums[first_labelset_str] = 0
		figer_first_labelset_mention_nums[first_labelset_str] += 1
	if len(both_labelset) > 1:
		if both_labelset_str not in figer_both_labelset_mention_bucket:
			figer_both_labelset_mention_bucket[both_labelset_str] = []
		if len(figer_both_labelset_mention_bucket[both_labelset_str]) < 3:
			figer_both_labelset_mention_bucket[both_labelset_str].append(item['mention'])
		if both_labelset_str not in figer_both_labelset_mention_nums:
			figer_both_labelset_mention_nums[both_labelset_str] = 0
		figer_both_labelset_mention_nums[both_labelset_str] += 1

	for pair in first_cooccurrences:
		if pair not in figer_first_cooccurrence_mention_bucket:
			figer_first_cooccurrence_mention_bucket[pair] = []
		if len(figer_first_cooccurrence_mention_bucket[pair]) < 3:
			figer_first_cooccurrence_mention_bucket[pair].append(item['mention'])
		if pair not in figer_first_cooccurrence_mention_nums:
			figer_first_cooccurrence_mention_nums[pair] = 0
		figer_first_cooccurrence_mention_nums[pair] += 1

	for pair in both_cooccurrences:
		if pair not in figer_both_cooccurrence_mention_bucket:
			figer_both_cooccurrence_mention_bucket[pair] = []
		if len(figer_both_cooccurrence_mention_bucket[pair]) < 3:
			figer_both_cooccurrence_mention_bucket[pair].append(item['mention'])
		if pair not in figer_both_cooccurrence_mention_nums:
			figer_both_cooccurrence_mention_nums[pair] = 0
		figer_both_cooccurrence_mention_nums[pair] += 1

figer_first_type_mention_nums_order = sorted(figer_first_type_mention_nums, key=figer_first_type_mention_nums.get, reverse=True)
figer_both_type_mention_nums_order = sorted(figer_both_type_mention_nums, key=figer_both_type_mention_nums.get, reverse=True)
figer_first_labelset_mention_order = sorted(figer_first_labelset_mention_nums, key=figer_first_labelset_mention_nums.get, reverse=True)
figer_both_labelset_mention_order = sorted(figer_both_labelset_mention_nums, key=figer_both_labelset_mention_nums.get, reverse=True)
figer_first_cooccurrence_mention_order = sorted(figer_first_cooccurrence_mention_nums, key=figer_first_cooccurrence_mention_nums.get, reverse=True)
figer_both_cooccurrence_mention_order = sorted(figer_both_cooccurrence_mention_nums, key=figer_both_cooccurrence_mention_nums.get, reverse=True)

figer_first_type_mention_nums = sort_dict_in_order(figer_first_type_mention_nums, figer_first_type_mention_nums_order)
figer_both_type_mention_nums = sort_dict_in_order(figer_both_type_mention_nums, figer_both_type_mention_nums_order)
figer_first_labelset_mention_nums = sort_dict_in_order(figer_first_labelset_mention_nums, figer_first_labelset_mention_order)
figer_both_labelset_mention_nums = sort_dict_in_order(figer_both_labelset_mention_nums, figer_both_labelset_mention_order)
figer_first_cooccurrence_mention_nums = sort_dict_in_order(figer_first_cooccurrence_mention_nums, figer_first_cooccurrence_mention_order)
figer_both_cooccurrence_mention_nums = sort_dict_in_order(figer_both_cooccurrence_mention_nums, figer_both_cooccurrence_mention_order)

figer_first_labelset_mention_bucket = sort_dict_in_order(figer_first_labelset_mention_bucket, figer_first_labelset_mention_order)
figer_both_labelset_mention_bucket = sort_dict_in_order(figer_both_labelset_mention_bucket, figer_both_labelset_mention_order)
figer_first_cooccurrence_mention_bucket = sort_dict_in_order(figer_first_cooccurrence_mention_bucket, figer_first_cooccurrence_mention_order)
figer_both_cooccurrence_mention_bucket = sort_dict_in_order(figer_both_cooccurrence_mention_bucket, figer_both_cooccurrence_mention_order)

save_dict_in_csv(figer_first_type_mention_nums, data_set+'_FIGER_layer1_nums_by_mention.csv')
save_dict_in_csv(figer_both_type_mention_nums, data_set+'_FIGER_layerboth_nums_by_mention.csv')
save_dict_in_csv(figer_first_labelset_mention_nums, data_set+'_FIGER_layer1_labelset_nums_by_mention.csv')
save_dict_in_csv(figer_both_labelset_mention_nums, data_set+'_FIGER_layerboth_labelset_nums_by_mention.csv')
save_dict_in_csv(figer_first_cooccurrence_mention_nums, data_set+'_FIGER_layer1_cooccurrence_nums_by_mention.csv')
save_dict_in_csv(figer_both_cooccurrence_mention_nums, data_set+'_FIGER_layerboth_cooccurrence_nums_by_mention.csv')

print("number of mentions among all %d mentions having each of the 49 first layer FIGER types:" % len(translated_data_entries))
print(figer_first_type_mention_nums)
print("number of mentions among all %d mentions having each of the 113 FIGER types of both layers" % len(translated_data_entries))
print(figer_both_type_mention_nums)
print("figer_first_labelset_mention_nums: ")
print(figer_first_labelset_mention_nums)
print("figer_both_labelset_mention_nums: ")
print(figer_both_labelset_mention_nums)
print("figer_first_cooccurrence_mention_nums: ")
print(figer_first_cooccurrence_mention_nums)
print("figer_both_cooccurrence_mention_nums: ")
print(figer_both_cooccurrence_mention_nums)
print("figer_first_labelset_mention_bucket: ")
print(figer_first_labelset_mention_bucket)
print("figer_both_labelset_mention_bucket: ")
print(figer_both_labelset_mention_bucket)
print("figer_first_cooccurrence_mention_bucket: ")
print(figer_first_cooccurrence_mention_bucket)
print("figer_both_cooccurrence_mention_bucket: ")
print(figer_both_cooccurrence_mention_bucket)


num_layer1_types_bucket = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
num_layerboth_types_bucket = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

FIGER_layer1_bucket = {}

FIGER_layerboth_bucket = {}

FIGER_layer1_cooccurance_bucket = {}

FIGER_layerboth_cooccurance_bucket = {}

FIGER_layer1_labelset_bucket = {}

FIGER_layerboth_labelset_bucket = {}

FIGER_layer1_nums = {}

FIGER_layerboth_nums = {}

FIGER_layer1_cooccurance_nums = {}

FIGER_layerboth_cooccurance_nums = {}

FIGER_layer1_labelset_nums = {}

FIGER_layerboth_labelset_nums = {}

for fine_type in mapping:
	items = mapping[fine_type]
	full_set = []
	first_set = []

	for item in items:
		assert (len(item) == 2)
		first = item[0]
		second = item[1]
		full = str(first) + ' / ' + str(second)
		if full not in full_set:
			full_set.append(full)
		if str(first) not in first_set:
			first_set.append(str(first))
		if first not in FIGER_layer1_bucket:
			FIGER_layer1_bucket[first] = []
		if first not in FIGER_layer1_nums:
			FIGER_layer1_nums[first] = 0
		if full not in FIGER_layerboth_bucket:
			FIGER_layerboth_bucket[full] = []
		if full not in FIGER_layerboth_nums:
			FIGER_layerboth_nums[full] = 0

		FIGER_layer1_bucket[first].append(fine_type)
		FIGER_layer1_nums[first] += 1
		FIGER_layerboth_bucket[full].append(fine_type)
		FIGER_layerboth_nums[full] += 1

	num_layer1_types_bucket[len(first_set)] += 1
	num_layerboth_types_bucket[len(full_set)] += 1
	first_set.sort()
	full_set.sort()

	for idx_1, item_1 in enumerate(first_set):
		for idx_2, item_2 in enumerate(first_set):
			if idx_1 >= idx_2:
				continue
			_pair = item_1 + ' ; ' + item_2
			if _pair not in FIGER_layer1_cooccurance_bucket:
				FIGER_layer1_cooccurance_bucket[_pair] = []
			if _pair not in FIGER_layer1_cooccurance_nums:
				FIGER_layer1_cooccurance_nums[_pair] = 0
			FIGER_layer1_cooccurance_bucket[_pair].append(fine_type)
			FIGER_layer1_cooccurance_nums[_pair] += 1

	for idx_1, item_1 in enumerate(full_set):
		for idx_2, item_2 in enumerate(full_set):
			if idx_1 >= idx_2:
				continue
			_pair = item_1 + ' ; ' + item_2
			if _pair not in FIGER_layerboth_cooccurance_bucket:
				FIGER_layerboth_cooccurance_bucket[_pair] = []
			if _pair not in FIGER_layerboth_cooccurance_nums:
				FIGER_layerboth_cooccurance_nums[_pair] = 0
			FIGER_layerboth_cooccurance_bucket[_pair].append(fine_type)
			FIGER_layerboth_cooccurance_nums[_pair] += 1

	full_concat = ' ; '.join(full_set)
	first_concat = ' ; '.join(first_set)

	if len(first_set) > 1:
		if first_concat not in FIGER_layer1_labelset_bucket:
			FIGER_layer1_labelset_bucket[first_concat] = []
		if first_concat not in FIGER_layer1_labelset_nums:
			FIGER_layer1_labelset_nums[first_concat] = 0
		FIGER_layer1_labelset_bucket[first_concat].append(fine_type)
		FIGER_layer1_labelset_nums[first_concat] += 1

	if len(full_set) > 1:
		if full_concat not in FIGER_layerboth_labelset_bucket:
			FIGER_layerboth_labelset_bucket[full_concat] = []
		if full_concat not in FIGER_layerboth_labelset_nums:
			FIGER_layerboth_labelset_nums[full_concat] = 0
		FIGER_layerboth_labelset_bucket[full_concat].append(fine_type)
		FIGER_layerboth_labelset_nums[full_concat] += 1

FIGER_layer1_nums_order = sorted(FIGER_layer1_nums, key=FIGER_layer1_nums.get, reverse=True)
FIGER_layerboth_nums_order = sorted(FIGER_layerboth_nums, key=FIGER_layerboth_nums.get, reverse=True)
FIGER_layer1_cooccurance_nums_order = sorted(FIGER_layer1_cooccurance_nums, key=FIGER_layer1_cooccurance_nums.get,
											 reverse=True)
FIGER_layerboth_cooccurance_nums_order = sorted(FIGER_layerboth_cooccurance_nums,
												key=FIGER_layerboth_cooccurance_nums.get, reverse=True)
FIGER_layer1_labelset_nums_order = sorted(FIGER_layer1_labelset_nums, key=FIGER_layer1_labelset_nums.get, reverse=True)
FIGER_layerboth_labelset_nums_order = sorted(FIGER_layerboth_labelset_nums, key=FIGER_layerboth_labelset_nums.get,
											 reverse=True)

FIGER_layer1_nums = sort_dict_in_order(FIGER_layer1_nums, FIGER_layer1_nums_order)
FIGER_layerboth_nums = sort_dict_in_order(FIGER_layerboth_nums, FIGER_layerboth_nums_order)
FIGER_layer1_cooccurance_nums = sort_dict_in_order(FIGER_layer1_cooccurance_nums, FIGER_layer1_cooccurance_nums_order)
FIGER_layerboth_cooccurance_nums = sort_dict_in_order(FIGER_layerboth_cooccurance_nums, FIGER_layerboth_cooccurance_nums_order)
FIGER_layer1_labelset_nums = sort_dict_in_order(FIGER_layer1_labelset_nums, FIGER_layer1_labelset_nums_order)
FIGER_layerboth_labelset_nums = sort_dict_in_order(FIGER_layerboth_labelset_nums, FIGER_layerboth_labelset_nums_order)

FIGER_layer1_bucket = sort_dict_in_order(FIGER_layer1_bucket, FIGER_layer1_nums_order)
FIGER_layerboth_bucket = sort_dict_in_order(FIGER_layerboth_bucket, FIGER_layerboth_nums_order)
FIGER_layer1_cooccurance_bucket = sort_dict_in_order(FIGER_layer1_cooccurance_bucket, FIGER_layer1_cooccurance_nums_order)
FIGER_layerboth_cooccurance_bucket = sort_dict_in_order(FIGER_layerboth_cooccurance_bucket, FIGER_layerboth_cooccurance_nums_order)
FIGER_layer1_labelset_bucket = sort_dict_in_order(FIGER_layer1_labelset_bucket, FIGER_layer1_labelset_nums_order)
FIGER_layerboth_labelset_bucket = sort_dict_in_order(FIGER_layerboth_labelset_bucket, FIGER_layerboth_labelset_nums_order)


save_dict_in_csv(FIGER_layer1_nums, data_set + '_FIGER_layer1_nums_by_utypes.csv')
save_dict_in_csv(FIGER_layerboth_nums, data_set + '_FIGER_layerboth_nums_by_utypes.csv')
save_dict_in_csv(FIGER_layer1_cooccurance_nums, data_set + '_FIGER_layer1_cooccurance_nums_by_utypes.csv')
save_dict_in_csv(FIGER_layerboth_cooccurance_nums, data_set + '_FIGER_layerboth_cooccurance_nums_by_utypes.csv')
save_dict_in_csv(FIGER_layer1_labelset_nums, data_set + '_FIGER_layer1_labelset_nums_by_utypes.csv')
save_dict_in_csv(FIGER_layerboth_labelset_nums, data_set + '_FIGER_layerboth_labelset_nums_by_utypes.csv')

FIGER_stat = {
	'num_layer1_types_bucket_per_type': num_layer1_types_bucket,
	'num_layerboth_types_bucket_per_type': num_layerboth_types_bucket,
	'FIGER_layer1_nums_of_utypes': FIGER_layer1_nums,
	'FIGER_layerboth_nums_of_utypes': FIGER_layerboth_nums,
	'FIGER_layer1_cooccurance_nums_of_utypes': FIGER_layer1_cooccurance_nums,
	'FIGER_layerboth_cooccurance_nums_of_utypes': FIGER_layerboth_cooccurance_nums,
	'FIGER_layer1_labelset_nums_of_utypes': FIGER_layer1_labelset_nums,
	'FIGER_layerboth_labelset_nums_of_utypes': FIGER_layerboth_labelset_nums,
	'FIGER_layer1_bucket_of_utypes': FIGER_layer1_bucket,
	'FIGER_layerboth_bucket_of_utypes': FIGER_layerboth_bucket,
	'FIGER_layer1_cooccurance_bucket_of_utypes': FIGER_layer1_cooccurance_bucket,
	'FIGER_layerboth_cooccurance_bucket_of_utypes': FIGER_layerboth_cooccurance_bucket,
	'FIGER_layer1_labelset_bucket_of_utypes': FIGER_layer1_labelset_bucket,
	'FIGER_layerboth_labelset_bucket_of_utypes': FIGER_layerboth_labelset_bucket,
	'num_first_types_bucket_per_mention': num_of_figer_first_types_per_mention_bucket,
	'num_both_types_bucket_per_mention': num_of_figer_both_types_per_mention_bucket,
	'num_fine_types_bucket_per_mention': num_of_fine_types_per_mention_bucket,
	'figer_first_type_mention_nums': figer_first_type_mention_nums,
	'figer_both_type_mention_nums': figer_both_type_mention_nums,
	'figer_first_labelset_mention_nums': figer_first_labelset_mention_nums,
	'figer_both_labelset_mention_nums': figer_both_labelset_mention_nums,
	'figer_first_cooccurrence_mention_nums': figer_first_cooccurrence_mention_nums,
	'figer_both_cooccurrence_mention_nums': figer_both_cooccurrence_mention_nums,
	'figer_first_labelset_mention_bucket': figer_first_labelset_mention_bucket,
	'figer_both_labelset_mention_bucket': figer_both_labelset_mention_bucket,
	'figer_first_cooccurrence_mention_bucket': figer_first_cooccurrence_mention_bucket,
	'figer_both_cooccurrence_mention_bucket': figer_both_cooccurrence_mention_bucket
}

with open(stats_output_filename, 'w', encoding='utf8') as fp:
	json.dump(FIGER_stat, fp, indent=4, ensure_ascii=False)

print("num_layer1_types_bucket: ")
print(num_layer1_types_bucket)
print("num_layerboth_types_bucket: ")
print(num_layerboth_types_bucket)
print('FIGER_layer1_bucket: ')
print(FIGER_layer1_bucket)
print('FIGER_layer1_nums: ')
print(FIGER_layer1_nums)
print('FIGER_layerboth_bucket: ')
print(FIGER_layerboth_bucket)
print('FIGER_layerboth_nums: ')
print(FIGER_layerboth_nums)
print('FIGER_layer1_cooccurance_bucket: ')
print(FIGER_layer1_cooccurance_bucket)
print('FIGER_layer1_cooccurance_nums: ')
print(FIGER_layer1_cooccurance_nums)
print('FIGER_layerboth_cooccurance_bucket: ')
print(FIGER_layerboth_cooccurance_bucket)
print('FIGER_layerboth_cooccurance_nums: ')
print(FIGER_layerboth_cooccurance_nums)
print('FIGER_layer1_labelset_bucket: ')
print(FIGER_layer1_labelset_bucket)
print('FIGER_layer1_labelset_nums: ')
print(FIGER_layer1_labelset_nums)
print('FIGER_layerboth_labelset_bucket: ')
print(FIGER_layerboth_labelset_bucket)
print('FIGER_layerboth_labelset_nums: ')
print(FIGER_layerboth_labelset_nums)

print("")
print('Done! Statistics saved to "%s"' % stats_output_filename)
