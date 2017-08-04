#!/usr/bin/env python3
import argparse
from pathlib import Path

import requests

from webstruct.gazetteers.geonames import read_geonames_zipped, to_dawg


FILES = [
    ('http://download.geonames.org/export/dump/allCountries.zip', 'allCountries.zip'),
    ('http://download.geonames.org/export/dump/cities1000.zip', 'cities1000.zip'),
    ('http://download.geonames.org/export/dump/cities5000.zip', 'cities5000.zip'),
    ('http://download.geonames.org/export/dump/cities15000.zip', 'cities15000.zip'),
]

DATA_ROOT = Path('_data')


def download_geonames():
    """ Download geonames files if they don't exist in ./_data folder. """
    DATA_ROOT.mkdir(exist_ok=True)
    for url, name in FILES:
        path = (DATA_ROOT / name)
        if path.exists():
            continue
        print("downloading {}".format(url))
        path.write_bytes(requests.get(url).content)


def _compile_cities(path: Path, lowercase: bool=False):
    out_path = path.with_suffix('.dafsa')
    # if out_path.exists():
    #     return
    print("reading {}".format(path))
    df = read_geonames_zipped(str(path))
    if lowercase:
        df = _to_lower(df)
    print("compiling {}".format(out_path))
    dawg = to_dawg(df)
    dawg.save(str(out_path))


def _to_lower(df):
    return df.assign(
        main_name=df.main_name.str.lower(),
        asciiname=df.asciiname.str.lower(),
        alternatenames=df.alternatenames.str.lower(),
    )


def _read_full():
    path = DATA_ROOT / 'allCountries.zip'
    print("reading {}".format(path))
    return read_geonames_zipped(str(path))


def _compile_adm(df):
    codes = ['ADM1', 'ADM2', 'ADM3', 'ADM4']
    out_paths = [DATA_ROOT / "{}.dafsa".format(code.lower()) for code in codes]
    # if all(p.exists() for p in out_paths):
    #     return
    for code, out_path in zip(codes, out_paths):
        # if out_path.exists():
        #     continue
        print("compiling {}".format(out_path))
        df_adm = df[df.feature_code == code]
        dawg = to_dawg(df_adm)
        dawg.save(str(out_path))


def compile_gazetteers_contacts(lowercase=False):
    """ Compile geonames data downloaded by ``download_geonames``. """
    for name in ['cities1000.zip', 'cities5000.zip', 'cities15000.zip']:
        _compile_cities(DATA_ROOT / name, lowercase=lowercase)
    df = _read_full()
    if lowercase:
        df = _to_lower(df)
    _compile_adm(df)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--lower', action="store_true")
    args = p.parse_args()

    download_geonames()
    compile_gazetteers_contacts(args.lower)