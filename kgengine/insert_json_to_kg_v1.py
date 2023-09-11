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
                #need to find the chem formula for the name: https://hub.docker.com/r/daverona/osra
                if key == 'names' or key == 'name':
                    raw_name = record[key]

                    # the name will be a list
                    # check the list with the smiles list and find the porper smiles

                    math_name_smiles = [] #self.match_name(raw_name, smiles)
                    new_math_name_smiles = [] #self.remake_match_name(math_name_smiles)

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
                                        #temp_name['alter_smiles' + str(count)] = name_smile_item[1][count][1]+" : " + name_smile_item[1][count][0]

                            temp_name['alter_name'] = alter_name
                            temp_name['alter_smiles'] = alter_smiles

                            temp_name['alter_combin'] = alter_combin

                            temp_name_id = None #self.kg.queryNode_dict(temp_name, 'record')

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
                            if peak_others:
                                for peak in peak_others:
                                    for peak_item in item[peak]:
                                        # we don't know the info of peak, so just use the name of peak as the label
                                        new_peak_others = {'label': peak}
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
    for path in pathlib.Path("/Users/luoyu/PycharmProjects/protoKG/goodSample").iterdir():
        print(1)
        test = Publish()
        test.readfile(path)
        test.getRecord([])
    #test = Publish('/Users/luoyu/PycharmProjects/protoKG/output/acs.joc.8b02978.json')
    #test.getRecord()
