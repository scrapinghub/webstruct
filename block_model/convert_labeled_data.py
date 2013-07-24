"""
convert the labeled data to crfsuite training data.
"""
import glob
from webstruct.features import generate_features, convert_crfsuite

if __name__ == '__main__':
    instances = []
    for fn in glob.glob('data/*.txt'):
        lines = open(fn).readlines()
        texts = [line.strip() for line in lines[0::2]]
        labels =[line.strip() for line in lines[1::2]]
        assert len(texts) == len(labels)
        items = generate_features(texts, labels)
        instances.append(convert_crfsuite(items))
    print "\n".join(instances)