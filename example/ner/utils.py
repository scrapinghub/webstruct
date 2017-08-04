# -*- coding: utf-8 -*-
from functools import partial

from tqdm import tqdm

pages_progress = partial(tqdm, unit=' pages', smoothing=False, leave=True)
