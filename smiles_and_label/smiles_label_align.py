import os

from smiles_and_label.label_align import unqiueLabel, detectDuplicate
from smiles_and_label.readImage import OsraSmiles
from smiles_and_label.smiles_label_combine import combineNameOCR, getSmiles, combineSmilewithName


def all_in_one(image_path, smile_output):
    all_smiles = []
    dir_list = os.listdir(image_path)
    test = OsraSmiles()
    for file in dir_list:
        if file.startswith("."):
            continue

        paddle = test.readNamefromImagePaddleOCR(image_path + file, 0.9)
        paddle = combineNameOCR(paddle)

        ocr = test.readNamefromImageOCR(image_path + file, 0.9)
        ocr = combineNameOCR(ocr)

        result, ocr, paddle = unqiueLabel(ocr, paddle)
        newinput = result + ocr + paddle
        unique = detectDuplicate(newinput)

        osra = test.runOsraSmiles(image_path,
                                  smile_output, 'sample', file)
        result = getSmiles(osra)
        name_and_smile = combineSmilewithName(result, unique)

        all_smiles += name_and_smile

        os.remove(image_path + file)
    return all_smiles
