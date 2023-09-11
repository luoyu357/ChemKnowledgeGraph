import configparser
import json

from chemdataextractor import Document
from chemdataextractor.scrape import Selector
from chemdataextractor.scrape.pub.rsc import RscHtmlDocument

import pathlib

import rule.simpleRule as sr


def process(config, save_path):
    for path in pathlib.Path("../sampleOne").iterdir():
        if path.is_file() and not path.stem.startswith(".") and path.stem == 'acs.joc.8b02978':
            f_name = path.stem
            with open(path, 'rb') as f_input:
                htmlstring = f_input.read()
                # scrape for biblio
                sel = Selector.from_html_text(htmlstring)

                scrape = RscHtmlDocument(sel)
                biblio = scrape.serialize()
                f_input.seek(0)
                doc = Document.from_file(f_input)
                records = sr.apply_rules(doc.records.serialize(), config)

                result = {'biblio': sr.transform_biblio(biblio), 'records': records}
                result = sr.add_structures(result)
                final = [result]
                if len(records) != 0:
                    with open(save_path + f_name + '.json', 'w', encoding='utf-8') as f_output:
                        json.dump(final, f_output)

                print("done")


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/Users/luoyu/PycharmProjects/protoKG/configV1.ini')
    process(config=config, save_path="/Users/luoyu/PycharmProjects/protoKG/output/")
