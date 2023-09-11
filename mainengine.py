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
        #all_smiles = all_in_one(output_image, smile_output)
        #print(all_smiles)
        #all_smiles = []

        all_smiles = [
            ['Cc1cccc2c1*(C)c1cccc3c1[Co]2c1c(*3)ccc2c1cccc2', [13, 246], [277, 550], [36, 208], [570, 602], '10: X=0',
             0.9891062026623128, 'False'],
            ['C1=CC2=*(C=C1)[Co]1c3ccccc3*c3c1c(*2)ccc3', [171, 418], [0, 276], [276, 356], [252, 282], '16',
             0.9146661332719246],
            ['C[Co+]12c3c4cccc3*c3c2c2c(C5=C1C(=CC=[I]5)*4)cccc2cc3', [363, 581], [273, 546], [388, 553], [571, 598],
             '4: X=0', 0.9636052250862122, 'False'],
            ['O=C1c2cccc(c2C(=O)c2c1cccc2Cl)C', [0, 446], [7, 394], [205, 274], [443, 495], '1', 0.9997236132621765,
             'False'], ['Cc1cccc2c1C(=O)c1c3c2cccc3ccc1C', [755, 1200], [1, 411], [959, 1045], [436, 501], '2',
                        0.9999667406082153],
            ['c1cc2ccc3c4c2c(c1)c1cccc2c1[Co]4c1c(o3)cccc1o2', [0, 439], [717, 1272], [203, 267], [1420, 1458], '4',
             0.9999849796295166, 'False'],
            ['C*(c1cccc2c1C13C(=O)c4c1c(ccc4)c1c4c3c([Co]2C)ccc4ccc1)C', [755, 1201], [745, 1462], [959, 1024],
             [1420, 1457], '3', 0.9998941421508789, 'False'],
            ['COc1cccc(c1C(=O)O)OC', [0, 415], [165, 463], [191, 266], [590, 636], '5', 0.9999499320983887],
            ['COc1cccc(c1C(=O)c1c(ccc2c1cccc2)C1C(C)C2C1CCC2C)C', [663, 1103], [0, 632]],
            ['Oc1cccc2c1C(=O)c1c(ccc3c1cccc3)CC[O]12(C)CC1C', [1436, 1864], [0, 632], [1627, 1677], [601, 631], '1',
             0.9991881251335144, 'False'],
            ['c1ccc2c(c1)[Co]1c3c(O2)cccc3Oc2c1c1ccccc1cc2', [15, 428], [940, 1457], [319, 444], [1436, 1480], 'PF6',
             0.9976198077201843, 'False'],
            ['CN1c2ccccc2[Co]2c3c1cccc3N(c1c2c2ccccc2cc1)C', [15, 431], [1773, 2288], [201, 274], [2342, 2375], '11',
             0.9559191465377808, 'False'],
            ['OC12c3c(ccc4c3cccc4)Oc3c2c(*(c2c1cccc2)(C)C)ccc3', [677, 1137], [942, 1536]],
            ['COc1cccc2c1c(=O)c1c(o2)ccc2c1cccc2', [1439, 1861], [944, 1536], [1411, 1534], [2249, 2301], 'PF6',
             0.9949440360069275, 'False'],
            ['Cn1c2cccc3c2[Co]2c4c1cccc4n(c1c2c2c3cccc2cc1)C', [1105, 1523], [1775, 2295], [1289, 1397], [2334, 2381],
             '14', 0.9999631638531183],
            ['COc1cccc2c1[Co]1c3c(ccc4c3cccc4)Oc3c1c(*2(C)C)ccc3', [2224, 2679], [942, 1462], [2442, 2552],
             [1488, 1544], '12', 0.9996892213821411],
            ['COc1cccc2c1[Co]1c3c(N2C)cccc3N(c2c1c1ccccc1cc2)C', [2242, 2662], [1773, 2295], [2423, 2531], [2335, 2381],
             '13', 0.9458049973829475],
            ['Oc1cccc2c1[Co]1c3c(O2)cccc3Oc2c1c1ccccc1cc2', [375, 823], [0, 565], [709, 869], [527, 598], 'PF6',
             0.9399555424028851],
            ['Cn1c2cccc3c2[Co]2c4c1cccc4oc1c2c(o3)ccc1', [183, 625], [1, 508], [292, 757], [544, 605], 'ADOTA+',
             0.9515482783317566],
            ['Cn1c2cccc3c2[Co]2c4c1cccc4n(c1c2c(o3)ccc1)C', [856, 1301], [59, 584], [962, 1426], [532, 583], 'DAOTA+',
             0.9740003943443298, 'False'],
            ['CC1(C)c2cccc3c2[Co]2c4c1cccc4Oc1c2c(O3)ccc1', [-1, 441], [699, 1196], [101, 340], [1233, 1286], 'CDOTA+',
             0.9799835393694742, 'True'],
            ['CN1c2cccc3c2[Co]2c4c1cccc4C(c1c2c(O3)ccc1)(C)C', [529, 975], [697, 1191], [636, 1101], [1228, 1286],
             'CAOTA+', 0.9628916382789612],
            ['CN1c2cccc3c2[Co]2c4c1cccc4C(c1c2c(N3C)ccc1)(C)C', [1069, 1517], [692, 1194], [1178, 1642], [1224, 1286],
             'CDATA+', 0.9486436771513951],
            ['c1cc2ccc3c4c2c(c1)c1cccc2c1[Co]4c1c(o3)cccc1o2', [0, 446], [0, 564], [106, 388], [642, 698], 'BDOTA+',
             0.9817624688148499],
            ['CC1CC=c2c3c1ccc1c3[Co]3c4c2cccc4n(c2c3c(n1C)ccc2)C', [622, 1069], [0, 563], [731, 1005], [645, 698],
             'BDATA+', 0.9292832016944885], ['c1ccc2c(c1)C1c3c(O2)cccc3Oc2c1c1ccccc1cc2', [1, 199], [306, 501]],
            ['CN/*=C/C=C\\C1CCC2=CC=CC3=CC=[C](=CCC[C@@H]3CC2)C(CCC2C=CC1CCCC2)NC', [441, 636], [293, 521]],
            ['Clc1cccc2c1C(=O)c1c3c2cccc3ccc1Cl', [18, 196], [25, 220], [17, 57], [89, 113], 'C', 0.9015525599670902,
             'False']]

        #read chemdataextractor josn data
        json_file = file.replace(".pdf", '.json')
        publish.readfile(json_doc + json_file)
        publish.getRecord(all_smiles)


