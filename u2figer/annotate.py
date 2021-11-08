import json
import tkinter as tk
import tkinter.font as tkFont
import sys
import time
import copy
# from utils.datautils import load_type_vocab


def load_type_vocab(type_vocab_file):
    type_vocab = list()
    type_to_id_dict = dict()
    with open(type_vocab_file, encoding='utf-8') as f:
        for i, line in enumerate(f):
            t = line.strip()
            type_vocab.append(t)
            type_to_id_dict[t] = i
    return type_vocab, type_to_id_dict


def fetch_mapping(fine_name, figer_nameset, mapping_filename, current, total, general_t=None, mentions=[]):
    window = tk.Tk()
    fontStyle = tkFont.Font(family="Lucida Grande", size=20)
    type_list_layer1 = figer_nameset['layer1']
    type_list_layer1.sort()
    type_layer_mapping = figer_nameset['mapping']
    assert len(type_list_layer1) == 49

    def first_layer_button_handler(event, fine_name, text):

        def second_layer_button_handler(event, fine_name, first, second):
            label_label["text"] = first + '/' + second
            if second == 'null':
                second = None
            if first == 'null':
                first = None
            with open(mapping_filename, 'r', encoding='utf8') as fp:
                fine_mapping = json.load(fp)
            if fine_name not in fine_mapping:
                fine_mapping[fine_name] = []
            fine_mapping[fine_name].append([first, second])
            with open(mapping_filename, 'w', encoding='utf8') as fp:
                json.dump(fine_mapping, fp, indent=4, ensure_ascii=False)
            print("!!")

        if text == 'null':
            second_layer_button_handler(None, fine_name, 'null', 'null')
            return

        designated_first_layer_type = text
        second_layer_candidates = copy.copy(type_layer_mapping[text])
        second_layer_candidates.sort()
        second_layer_candidates.insert(0, 'null')

        second_window = tk.Tk()
        second_window.bind('<Escape>', lambda e: second_window.destroy())
        second_window.columnconfigure(0, weight=1, minsize=75)
        second_window.rowconfigure(0, weight=2, minsize=75)
        _frame = tk.Frame(
            master=second_window,
            relief=tk.RAISED,
            borderwidth=1
        )
        _frame.grid(row=0, column=0, padx=5, pady=5)
        name_label = tk.Label(master=_frame, text=fine_name, font=fontStyle)
        name_label.pack(padx=5, pady=5)
        for a in range(20):
            if a >= len(second_layer_candidates):
                break
            second_window.rowconfigure(a+1, weight=1, minsize=50)
            frame = tk.Frame(
                master=second_window,
                relief=tk.RAISED,
                borderwidth=1
            )
            frame.grid(row=a+1, column=0, padx=5, pady=5)
            button = tk.Button(master=frame, text=second_layer_candidates[a], font=fontStyle)
            button.bind("<Button-1>", lambda event, fine_name=fine_name, first=designated_first_layer_type,
                                             second=second_layer_candidates[a]: second_layer_button_handler(
                event, fine_name, first, second))
            button.pack(padx=5, pady=5)
        second_window.mainloop()
        print("!!!")

    name_label = tk.Label(master=window, text=fine_name, font=fontStyle)
    button_null = tk.Button(master=window, text='None of Above', font=fontStyle)
    button_null.bind("<Button-1>",
                lambda event, fine_name=fine_name, text='null': first_layer_button_handler(event, fine_name, text))
    count_label = tk.Label(master=window, text='%d / %d' % (current, total), font=fontStyle)
    label_label = tk.Label(master=window, text='Type: ', font=fontStyle)
    general_label = tk.Label(master=window, text='G: ' + str(general_t), font=fontStyle)
    mention_label = tk.Label(master=window, text=str(mentions), font=fontStyle)  # .encode('UTF-8', errors='replace')
    for i in range(7):
        window.columnconfigure(i, weight=1, minsize=200)
        window.rowconfigure(i, weight=1, minsize=50)

        for j in range(7):
            frame = tk.Frame(
                master=window,
                relief=tk.RAISED,
                borderwidth=1
            )
            frame.grid(row=i, column=j, padx=5, pady=5)

            button = tk.Button(master=frame, text=type_list_layer1[7*i+j], font=fontStyle)
            button.bind("<Button-1>", lambda event, fine_name=fine_name, text=type_list_layer1[7*i+j]: first_layer_button_handler(event, fine_name, text))
            button.pack(padx=5, pady=5)
    window.rowconfigure(7, weight=2, minsize=100)
    name_label.grid(row=7, column=0, padx=5, pady=5)
    button_null.grid(row=7, column=1, padx=5, pady=5)
    count_label.grid(row=7, column=2, padx=5, pady=5)
    label_label.grid(row=7, column=3, padx=5, pady=5)
    general_label.grid(row=7, column=4, padx=5, pady=5)
    mention_label.grid(row=7, column=5, padx=5, pady=5)
    window.bind('<Escape>', lambda e: window.destroy())
    window.mainloop()


crowd_mapping_fn = 'crowdsourced2FIGER_mapping.jsonl'
wiki_mapping_fn = 'wiki2FIGER_mapping.jsonl'


with open('type_list_layer1.jsonl', 'r') as fp:
    FIGER_type_list_layer1 = json.load(fp)
with open('type_list_layer2.jsonl', 'r') as fp:
    FIGER_type_list_layer2 = json.load(fp)
with open('type_list.jsonl', 'r') as fp:
    FIGER_type_list = json.load(fp)
with open('type_json.jsonl', 'r') as fp:
    FIGER_type_json = json.load(fp)
with open('layerwise_type_mapping.jsonl', 'r') as fp:
    FIGER_type_layer_mapping = json.load(fp)


with open('wiki_refs.json', 'r', encoding='utf8') as fp:
    ref_mappings = json.load(fp)

general_mapping = ref_mappings['general']
mentions_mapping = ref_mappings['mentions']


figer_nameset = {
    'layer1': FIGER_type_list_layer1,  # layer 1 type set
    'layer2': FIGER_type_list_layer2,  # layer 2 type set
    'full': FIGER_type_list,  # type set of all layers
    'hier': FIGER_type_json,  # type hierarchy
    'mapping': FIGER_type_layer_mapping,  # mapping between first layer types and their possible second layer types
}

crowdsourced_type_list, crowdsourced_dict = load_type_vocab('../cfet_data/types/crowdsourced_types.json')
wiki_type_list, wiki_type_dict = load_type_vocab('../cfet_data/types/wiki_types.json')

with open(crowd_mapping_fn, 'r', encoding='utf8') as fp:
    crowd_mapping = json.load(fp)
with open(wiki_mapping_fn, 'r', encoding='utf8') as fp:
    wiki_mapping = json.load(fp)

for idx, label in enumerate(crowdsourced_type_list):
    # retrieve label mapping in FIGER
    if label in crowd_mapping:
        continue
    fetch_mapping(label, figer_nameset, mapping_filename=crowd_mapping_fn, current=idx, total=len(crowdsourced_type_list))
    time.sleep(1)

with open(crowd_mapping_fn, 'r', encoding='utf8') as fp:
    crowd_mapping = json.load(fp)

for idx, label in enumerate(wiki_type_list):
    # retrieve label mapping in FIGER
    if label in wiki_mapping or label in crowd_mapping:
        continue
    if len(general_mapping[label]) == 1:
        general_t = general_mapping[label][0]
    else:
        general_t = None
    fetch_mapping(label, figer_nameset, mapping_filename=wiki_mapping_fn, current=idx, total=len(wiki_type_list), general_t=general_t, mentions=mentions_mapping[label][:3])
    time.sleep(1)

with open(wiki_mapping_fn, 'r', encoding='utf8') as fp:
    wiki_mapping = json.load(fp)

for key in crowd_mapping:
    wiki_mapping[key] = crowd_mapping[key]  # add the crowdsourced type mappings (annotated before) into the wiki type mappings at
# the end
with open(wiki_mapping_fn, 'w', encoding='utf8') as fp:
    json.dump(wiki_mapping, fp, indent=4, ensure_ascii=False)

print('Finished!')
