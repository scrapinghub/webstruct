# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pandas as pd
import numpy as np
import csv
import marisa_trie


def read_geonames(filename):
    COLUMNS = ['geonameid', 'main_name', 'asciiname', 'alternatenames',
               'latitude', 'longitude', 'feature_class', 'feature_code',
               'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
               'population', 'elevation', 'dem', 'timezone', 'modification_date']

    dtypes = {
        'feature_class': object,
        'feature_code': object,
        'country_code': object,
        'admin1_code': object,
        'admin2_code': object,
        'admin3_code': object,
        'admin4_code': object,
    }
    return pd.read_csv(filename, sep='\t', header=None, encoding='utf8',
                       quoting=csv.QUOTE_NONE, names=COLUMNS, dtype=dtypes)


def _joined_names_column(df):
    return df.apply(
        lambda row: ','.join(set([
            unicode(n)
            for n in [row['main_name'], row['asciiname'], row['alternatenames']]
            if n and n is not np.nan
        ])),
        axis=1
    )


def _split_names_into_rows(df):
    names = _joined_names_column(df).str.split(',')
    name_lenghts = names.map(len)
    idx = np.repeat(name_lenghts.index, name_lenghts.values)

    names_split = np.concatenate(names.values)
    names_s = pd.Series(names_split, index=idx)
    names_s.name = 'name'

    df = df.join(names_s, )
    del df['main_name']
    del df['asciiname']
    del df['alternatenames']

    cols = df.columns.tolist()
    cols = cols[0:1] + cols[-1:] + cols[1:-1]
    df = df[cols]
    return df.reset_index()


def to_marisa(df):
    df = _split_names_into_rows(df)
    def data_iter():
        for idx, row in df.iterrows():
            data = (row['country_code'], row['feature_class'], row['feature_code'], row['admin1_code'], row['admin2_code'])
            yield row['name'], [v.encode('utf8') if not isinstance(v, float) else str(v) for v in data]
    return marisa_trie.RecordTrie("2s 1s 5s 2s 3s", data_iter())
