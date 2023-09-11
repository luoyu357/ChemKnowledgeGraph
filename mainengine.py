from extractor.get_image_from_pdf import readPDF
from kgengine.insert_json_to_kg_v1 import Publish
import pathlib
import os

from smiles_and_label.smiles_label_align import all_in_one

if __name__ == '__main__':

    input_pdf = '/Users/luoyu/PycharmProjects/protoKG/sampleOne/pdf1/'
    output_image = '/Users/luoyu/PycharmProjects/protoKG/extractor/images/'
    json_doc = '/Users/luoyu/PycharmProjects/protoKG/sampleOne/json1/'
    smile_output = '/Users/luoyu/PycharmProjects/protoKG/smiles_and_label/output'

    publish = Publish()

    dir_list = os.listdir(input_pdf)
    for file in dir_list:
        if file.startswith("."):
            continue

        # extract image from pdf
        readPDF(input_pdf+file, output_image)

        #read the image and generate smiles
        all_smiles = all_in_one(output_image, smile_output)

        #read chemdataextractor josn data
        json_file = file.replace(".pdf", '.json')
        publish.readfile(json_doc + json_file)
        publish.getRecord(all_smiles)


