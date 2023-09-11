import json
import pathlib
import uuid

from kgengine.neo4jengine import KG


class Publish:
    def __init__(self):
        self.file = None
        self.kg = KG("bolt://localhost:7687", "neo4j", "admin")

    def readfile(self, filepath):
        data = open(filepath)
        self.file = json.load(data)[0]

    def getBiblio(self, random_uuid):
        id = []
        biblio = self.file['biblio']
        biblio["label"] = "biblio"
        biblio['uuid'] = random_uuid
        id.append(self.kg.createNode(biblio, "biblio"))
        return id

    def check_peak_others(self, content):
        output = []
        for key in content.keys():
            if isinstance(content[key], list):
                output.append(key)
        return output

    def get_smile(self, content):
        for key in content:
            if 'smiles' in key.lower():
                return {key: content[key]}
        return {"smiles": "None"}

    def match_name(self, names, smiles):
        new_smiles = []
        for i in smiles:
            if len(i) >= 6:
                name_no_space = str(i[5])
                # [smiles, real_name, name_no_space]
                new_smiles.append([i[0], i[5], name_no_space.replace(" ", '')])

        name_smiles = []
        if not isinstance(names, list):
            names = [names]

        unique_name = {}
        # {name_no_space : [name_space]}
        for name in names:
            name_no_space = name.replace(' ', '')
            if name_no_space not in unique_name.keys():
                unique_name[name_no_space] = [name]
            else:
                unique_name[name_no_space].append(name)

        match_name = {}
        for name_no_space in unique_name.keys():
            for item in new_smiles:

                if name_no_space in item[2] or item[2] in name_no_space:
                    if name_no_space not in match_name:
                        match_name[name_no_space] = [[item[0], item[1]]]
                    else:
                        if [item[0], item[1]] not in match_name[name_no_space]:
                            match_name[name_no_space].append([item[0], item[1]])
                        else:
                            match_name[name_no_space] = []

        for key in unique_name.keys():
            name_smiles.append([unique_name[key], match_name[key]])

        return name_smiles


    def remake_match_name(self, name_smiles):
        result = []
        for item in name_smiles:
            names = item[0]
            smiles = item[1]

            if len(smiles) == 1:
                result.append(item)
            else:
                temp_smile = []
                for name in names:
                    stop = False
                    for smile in smiles:
                        if name == smile[1] or name.replace(' ', '') == smile[1].replace(' ', ''):
                            result.append([names, [smile]])
                            stop = True
                            break
                        else:
                            temp_name = name.split(' ')
                            for index in range(len(temp_name)-1):
                                for next_index in range(index+1, len(temp_name)):
                                    if ''.join(temp_name[index:next_index]) == smile[1]:
                                        temp_smile.append(smile)
                    if stop:
                        break
                if temp_smile:
                    result.append([names, temp_smile])
        return result



    def getRecord(self, smiles):
        #create node for biblio information
        # uuid will be used in all entities, except record
        random_uuid = uuid.uuid4()
        id_biblio = self.getBiblio(random_uuid)
        records = self.file['records']


        for record in records:
            smile = self.get_smile(record)
            id_name = []
            for key in record.keys():
                if 'smiles' in key:
                    continue
                if key == 'names' or key == 'name':
                    raw_name = record[key]

                    # the name will be a list
                    # check the list with the smiles list and find the porper smiles
                    math_name_smiles = self.match_name(raw_name, smiles)
                    new_math_name_smiles = self.remake_match_name(math_name_smiles)

                    if isinstance(raw_name, list):
                        for value in raw_name:
                            temp_name = {key: value, 'label': value}
                            for temp_smile_item_key in smile.keys():
                                temp_name[temp_smile_item_key] = smile[temp_smile_item_key]

                            alter_name = []
                            alter_smiles = []
                            alter_combin = []
                            for name_smile_item in new_math_name_smiles:
                                if value in name_smile_item[0]:
                                    for count in range(len(name_smile_item[1])):
                                        alter_name.append(name_smile_item[1][count][1])
                                        alter_smiles.append(name_smile_item[1][count][0])
                                        alter_combin.append(name_smile_item[1][count][1]+" : " + \
                                                                                 name_smile_item[1][count][0])


                            temp_name['alter_name'] = alter_name
                            temp_name['alter_smiles'] = alter_smiles

                            temp_name['alter_combin'] = alter_combin

                            temp_name_id = self.kg.queryNode_dict(temp_name, 'record')

                            if temp_name_id is None:
                                id_name.append(self.kg.createNode(temp_name, 'record'))
                            else:
                                id_name.append(temp_name_id)

                    else:
                        temp_name = {key: raw_name, 'label': raw_name}
                        for temp_smile_item in smile:
                            temp_name[temp_smile_item] = smile[temp_smile_item]

                        for name_smile_item in new_math_name_smiles:
                            if value in name_smile_item[0]:
                                for count in range(len(name_smile_item[1])):
                                    temp_name['alter_smiles' + str(count)] = name_smile_item[1][count][1] + " : " + \
                                                                        name_smile_item[1][count][0]

                        temp_name_id = self.kg.queryNode_dict(temp_name, 'record')
                        if temp_name_id is None:
                            id_name.append(self.kg.createNode(temp_name, 'record'))
                        else:
                            id_name.append(temp_name_id)

                    self.kg.createRelationship(id_biblio, id_name, 'contains')
                else:
                    value = record[key]
                    validation_id_list = []

                    if isinstance(value, list):

                        for item in value:
                            peak_other_id_list = []
                            # if the validation item (record) has the internal list for peaks or others
                            peak_others = self.check_peak_others(item)
                            item['label'] = key
                            item['uuid'] = random_uuid
                            if peak_others:
                                for peak in peak_others:
                                    for peak_item in item[peak]:
                                        # we don't know the info of peak, so just use the name of peak as the label
                                        new_peak_others = {'label': peak, 'uuid':random_uuid}
                                        for peak_key in peak_item.keys():
                                            new_peak_others[peak_key] = peak_item[peak_key]

                                        # make sure there is no duplicate peak
                                        peak_other_id = self.kg.queryNode_dict(new_peak_others, peak)
                                        if peak_other_id is None:
                                            peak_other_id = self.kg.createNode(new_peak_others, peak)
                                        if peak_other_id not in peak_other_id_list:
                                            peak_other_id_list.append(peak_other_id)
                                    del item[peak]

                            validation_id = self.kg.queryNode_dict(item, key)
                            if validation_id is None:
                                validation_id = self.kg.createNode(item, key)

                            if validation_id not in validation_id_list:
                                validation_id_list.append(validation_id)

                            if peak_other_id_list:
                                self.kg.createRelationship([validation_id], peak_other_id_list, 'peak_or_other')

                    if id_name:
                        self.kg.createRelationship(id_name, validation_id_list, 'experiment')
                    else:
                        if validation_id_list:
                            self.kg.createRelationship(id_biblio, validation_id_list, 'experiment')
                        else:
                            self.kg.createRelationship(id_biblio, peak_other_id_list, 'experiment')


if __name__ == "__main__":
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
    for path in pathlib.Path("/Users/luoyu/PycharmProjects/protoKG/sampleOne/json1").iterdir():
        test = Publish()
        test.readfile(path)
        test.getRecord(all_smiles)

