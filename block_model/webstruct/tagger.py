from crfsuite import CRFModel
from webstruct.features import generate_features, convert_crfsuite
from webstruct.htmls import get_lines
from webstruct.models import get_data_path

class Tagger(object):
    def __init__(self, fname=get_data_path('webstruct.model')):
        self._model = CRFModel(fname)
        self._tagger = self._model.get_tagger()

    def tag(self, html, encoding='utf8'):
        texts = get_lines(html)
        items = generate_features(texts, ['O'] * len(texts))
        text = convert_crfsuite(items).encode(encoding)
        crf_data_test = self._tagger.get_tagging_data_from_text(text)
        return texts, [self._tagger.get_label_dict().get_key(id) for id in self._tagger.tag(crf_data_test, quiet=True)]