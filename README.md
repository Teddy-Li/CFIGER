#CFIGER: Chinese Fine-Grained entity typing under FIGER ontology
A repository for a Chinese fine-grained entity typing dataset based on the FIGER ontology, based on
[A Chinese Corpus for Fine-grained Entity Typing](https://github.com/HKUST-KnowComp/cfet).

## Annotation Process
The CFIGER dataset has been annotated through label mapping: we manually mapped the tokens from each of the ~6000 
ultra-fine-grained types to a FIGER type. The resulting mappings are [here](https://drive.google.com/file/d/1wKr4X5FU4GelwnlSKxOv2TFCx8JbTzTL/view?usp=sharing), they should be put 
under [./u2figer](./u2figer); the resulting re-annotated dataset is [here](https://drive.google.com/file/d/1dfJrqUXBSn1wU0AKlrRlRNedbGaRSq8B/view?usp=sharing), decompose the zip file and 
put it under the root directory.

## Baselines
We updated the CFET baseline in accordance with our re-annotated data. To run the baseline, take the 
following steps: 
1. From [fastText](https://github.com/facebookresearch/fastText/tree/master), download its Chinese model 
[here](https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.vec.gz);
2. Run [preprocess.py](./preprocess.py) in mode `embed`, `data` and `pred` respectively, remember to set 
the correct path to the downloaded fastText model;
3. Do training simply with ``python train.py``, configurations can be set in ``config.py``;
4. For doing inference on datasets in other domains, please refer to [predict.py](./predict.py)

We have also built another baseline model based on the [HierType](https://github.com/ctongfei/hierarchical-typing),
which as shown below, has better generalization properties than the present baseline. The Chinese HierType baseline
can be found in another repository [here]() (coming soon).

## Results
![Coming soon.](https://github.com/ "Results")

## Citing Us
Coming soon.