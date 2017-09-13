import logging
import argparse

import webstruct.loaders
import webstruct.webannotator

def main():
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument('--input',  help = 'path to source annotated file', type=str, required=True)
    cmdline.add_argument('--sample', help = 'path to already marked html',   type=str, required=True)
    cmdline.add_argument('--output', help = 'path to result annotated file', type=str, required=True)
    cmdline.add_argument('--loglevel', help = 'logging level', type=str, default='INFO')
    args = cmdline.parse_args()

    logging.basicConfig( level  = getattr(logging, args.loglevel.upper())
                       , format = '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d %(message)s' )
    with open(args.sample, 'rb') as sample_reader:
        colors   = webstruct.webannotator.EntityColors.from_htmlbytes(sample_reader.read())
        entities = [typ for typ in colors]

    logging.debug('Current entities %s', entities)
    logging.debug('Current colors %s', colors)

    gate = webstruct.loaders.GateLoader(known_entities = entities)
    tokenizer = webstruct.HtmlTokenizer(tagset = entities)
    with open(args.input, 'rb') as reader:
        data = reader.read()
        tree = gate.loadbytes(data)
        tokens, annotations = tokenizer.tokenize_single(tree)
        tree = webstruct.webannotator.to_webannotator(tree, entity_colors=colors)
        with open(args.output, 'wb') as writer:
            tree.write(writer, method = 'html', pretty_print = True)

if __name__ == "__main__":
    main()
