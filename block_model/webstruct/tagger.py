from crfsuite import CRFModel
import itertools
from webstruct.features import generate_features, convert_crfsuite
from webstruct.htmls import get_lines
from webstruct.models import get_data_path
import re

class Tagger(object):

    _RE_TAG = re.compile(r'([A-Z]+)-([IBE])')

    def __init__(self, fname='webstruct.model'):
        self._model = CRFModel(get_data_path(fname))
        self._tagger = self._model.get_tagger()

    def _get_tag_name(self, tag):
        """
        Get the tag name.

        for example:
        >>> t = Tagger()
        >>> t._get_tag_name('STR')
        'STR'
        >>> t._get_tag_name('STR-I')
        'STR'
        >>> t._get_tag_name('STR-B')
        'STR'
        """
        m = re.search(self._RE_TAG, tag)
        if m:
            return m.group(1)
        else:
            return tag

    def _merge(self, tags, tokens):
        """
        merge the tokens has same prefix.

        >>> t = Tagger()
        >>> tags = ['ADDR-B', 'ADDR-I', 'ADDR-I', 'ADDR-I', 'ADDR-I', 'ADDR-I', 'O', 'O']
        >>> texts = ['Unit', '57,', '76', 'Newcastle', 'St,', 'Perth', 'WA', '6000']
        >>> t._merge(tags, texts)
        {'ADDR': [u'Unit 57, 76 Newcastle St, Perth']}

        """

        key = lambda (tag, i) : self._get_tag_name(tag)
        result = {}
        for key, values in itertools.groupby([(tag, i) for i, tag in enumerate(tags)], key=key):
            values = list(values)
            if values[0][0].endswith('-B') and values[-1][0].endswith('-I'):
                result.setdefault(key, []).append(u" ".join([tokens[i].decode('utf8', 'ignore') for _, i in values]))
        return result

    def tag(self, html, encoding='utf8'):
        texts = get_lines(html)
        items = generate_features(texts, ['O'] * len(texts))
        text = convert_crfsuite(items).encode(encoding)
        crf_data_test = self._tagger.get_tagging_data_from_text(text)
        labels = [self._tagger.get_label_dict().get_key(id) for id in self._tagger.tag(crf_data_test, quiet=True)]
        result = self._merge(labels, texts)
        return texts, labels, result.get('ADDR', [])