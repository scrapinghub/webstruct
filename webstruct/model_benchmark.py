import sys
import os.path
import glob
import timeit
import functools

import joblib


def predict(model, bodies):
    for body in bodies:
        model.extract_raw(body)


def main():
    path = os.path.join(os.path.dirname(__file__) ,
                        ".." ,
                        "webstruct_data",
                        "corpus/business_pages/wa/*.html")


    paths = sorted(glob.glob(path))
    bodies = list()
    for p in paths:
        with open(p, 'rb') as reader:
            bodies.append(reader.read())

    model = joblib.load(sys.argv[1])
    print(timeit.timeit(functools.partial(predict, model, bodies),
                        setup='gc.enable()',
                        number=3))


if __name__ == "__main__":
    main()
