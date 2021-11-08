import datetime
import torch
import numpy as np
import os
import logging
import random
from os.path import join
from time import time
import argparse

import torch
from torch import nn


from utils import exp_utils, datautils, model_utils, utils
from utils.loggingutils import init_universal_logging
from utils.fet import fet_model
import config


def predict_model(slice_idx, gpu_id):
    data_prefix = config.CUFE_FILES['training_data_prefix']

    # data_prefix += f'-{config.seq_tokenizer_name}'
    if config.dir_suffix:
        data_prefix += '-' + config.dir_suffix
    if not os.path.isdir(data_prefix):
        raise AssertionError

    str_today = datetime.datetime.now().strftime('%m_%d_%H%M')
    if not os.path.isdir(join(data_prefix, 'log')): os.mkdir(join(data_prefix, 'log'))
    log_file = os.path.join(config.LOG_DIR, '{}-{}-predict.log'.format(str_today, config.model_name))
    # if not os.path.isdir(log_file) and not config.test: os.mkdir(log_file)
    init_universal_logging(log_file, mode='a', to_stdout=True)

    save_model_dir = join(data_prefix, 'models')
    if not os.path.isdir(save_model_dir): os.mkdir(save_model_dir)

    gres = exp_utils.GlobalRes(config)

    logging.info(f'/data/cleeag/word_embeddings/{config.mention_tokenizer_name}/{config.mention_tokenizer_name}_tokenizer&vecs.pkl -- loaded')
    logging.info(f'total type count: {len(gres.type2type_id_dict)}, '
                 f'general type count: {0 if config.without_general_types else len(gres.general_type_set)}')

    predict_data_pkl = join(data_prefix, config.prediction_pkl_name%slice_idx)

    print("Loading pred examples from %s" % predict_data_pkl)
    pred_samples = datautils.load_pickle_data(predict_data_pkl)
    print('done', flush=True)
    pred_true_labels_dict = {s['mention_id']: [gres.type2type_id_dict.get(x) for x in
                                              exp_utils.general_mapping(s['figer_types_first_list'], gres)] for s in pred_samples}

    logging.info(f'total prediction samples: {len(pred_samples)}')

    result_dir = join(data_prefix, f'pred-results')
    pred_results_file = join(result_dir, f'webhose_arg_pred_results_%s.txt'%slice_idx)

    if not os.path.isdir(result_dir): os.mkdir(result_dir)

    logging.info('use_bert = {}, use_lstm = {}, use_mlp={}, bert_param_frozen={}, bert_fine_tune={}'
                 .format(config.use_bert, config.use_lstm, config.use_mlp, config.freeze_bert, config.fine_tune))
    logging.info(
        'type_embed_dim={} contextt_lstm_hidden_dim={} pmlp_hdim={}'.format(
            config.type_embed_dim, config.lstm_hidden_dim, config.pred_mlp_hdim))

    # setup training
    device = torch.device(f'cuda:{gpu_id}') if torch.cuda.device_count() > 0 else torch.device('cpu')

    device_name = torch.cuda.get_device_name(gpu_id)

    logging.info(f'running on device: {device_name}')
    logging.info('building model...')

    model = fet_model(config, device, gres)
    logging.info(f'transfer={config.transfer}')

    model_path = config.SAVED_MODEL_PATH
    logging.info(f'loading checkpoint from {model_path}')
    trained_weights = torch.load(model_path, map_location=device)
    trained_weights = {'.'.join(k.split('.')[1:]): v for k, v in trained_weights.items()}
    cur_model_dict = model.state_dict()
    cur_model_dict.update(trained_weights)
    model.load_state_dict(cur_model_dict)

    model.to(device)
    model = torch.nn.DataParallel(model, device_ids=[gpu_id])

    batch_size = config.batch_size

    losses = list()
    best_dev_acc = -1
    best_maf1_v = -1
    step = 0
    steps_since_last_best = 0

    # start training
    logging.info('{}'.format(model.__class__.__name__))
    logging.info('training batch size: {}'.format(batch_size))

    print('\nevaluating...')
    l_v, acc_v, pacc_v, maf1_v, ma_p_v, ma_r_v, mif1_v, pred_results = \
        model_utils.predict_fetel(config, gres, model, pred_samples, pred_true_labels_dict)

    print(len(pred_results))

    datautils.save_json_objs(pred_results, pred_results_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--slice_id', type=str, default=0, help='the slice id of input webhose file')
    parser.add_argument('--gpu_id', type=int, default=0, help='gpu id to run prediction upon.')

    args = parser.parse_args()

    torch.random.manual_seed(config.RANDOM_SEED)
    np.random.seed(config.NP_RANDOM_SEED)
    random.seed(config.PY_RANDOM_SEED)

    str_today = datetime.datetime.now().strftime('%m_%d_%H%M')
    model_used = 'use_bert' if config.use_bert else 'use_lstm'
    if not os.path.isdir(config.LOG_DIR): os.mkdir(config.LOG_DIR)
    if not config.test:
        log_file = os.path.join(config.LOG_DIR, '{}-{}_{}.log'.format(os.path.splitext(
            os.path.basename(__file__))[0], str_today, model_used))
    else:
        log_file = os.path.join(config.LOG_DIR, '{}-{}_{}_test.log'.format(os.path.splitext(
            os.path.basename(__file__))[0], str_today, model_used))
    init_universal_logging(log_file, mode='a', to_stdout=True)
    predict_model(args.slice_id, args.gpu_id)
    # model_utils.check_breakdown_performance()
