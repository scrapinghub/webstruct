from crfsuite import CRFDataset, crfsuite_learn
import sys

if len(sys.argv) > 1:
    name = sys.argv[1]
else:
    name = 'train.txt'

crf_data = CRFDataset().add_groups_from_files(name)
model = crfsuite_learn(crf_data, model_file='webstruct.model')
