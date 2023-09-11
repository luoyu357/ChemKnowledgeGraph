import json
import pathlib

from kgengine.neo4jengine import KG

# this file should be deleted, but keep for

class Publish:
    def __init__(self):
        self.file = None
        self.kg = KG("bolt://localhost:7687", "neo4j", "admin")

    def readfile(self, filepath):
        data = open(filepath)
        self.file = json.load(data)[0]

    def getBiblio(self):
        id = []
        biblio = self.file['biblio']
        biblio["label"] = "biblio"
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


    def getRecord(self):
        #create node for biblio information
        id_biblio = self.getBiblio()
        records = self.file['records']

        for record in records:
            smile = self.get_smile(record)
            id_name = []
            for key in record.keys():
                if 'smiles' in key:
                    continue
                if key == 'names' or key == 'name':
                    raw_name = record[key]
                    if isinstance(raw_name, list):
                        for value in raw_name:
                            temp_name = {key: value, 'label': value}
                            for temp_smile_item_key in smile.keys():
                                temp_name[temp_smile_item_key] = smile[temp_smile_item_key]

                            temp_name_id = self.kg.queryNode(temp_name, 'record')

                            if temp_name_id is None:
                                id_name.append(self.kg.createNode(temp_name, 'record'))
                            else:
                                id_name.append(temp_name_id)
                    else:
                        temp_name = {key: raw_name, 'label': raw_name}
                        for temp_smile_item in smile:
                            temp_name[temp_smile_item] = smile[temp_smile_item]

                        temp_name_id = self.kg.queryNode(temp_name, 'record')
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
                                        peak_other_id = self.kg.queryNode(new_peak_others, peak)
                                        if peak_other_id is None:
                                            peak_other_id = self.kg.createNode(new_peak_others, peak)
                                        if peak_other_id not in peak_other_id_list:
                                            peak_other_id_list.append(peak_other_id)
                                    del item[peak]

                            validation_id = self.kg.queryNode(item, key)
                            if validation_id is None:
                                validation_id = self.kg.createNode(item, key)
                            elif validation_id not in validation_id_list:
                                validation_id_list.append(validation_id)

                            if peak_other_id_list:
                                self.kg.createRelationship([validation_id], peak_other_id_list, 'peak_or_other')

                    if id_name:
                        self.kg.createRelationship(id_name, validation_id_list, 'experiment')
                    else:
                        self.kg.createRelationship(id_biblio, validation_id_list, 'experiment')


if __name__ == "__main__":
    for path in pathlib.Path("../differentOutput").iterdir():
        test = Publish()
        test.readfile(path)
        test.getRecord()
    #test = Publish('/Users/luoyu/PycharmProjects/protoKG/output/acs.joc.8b02978.json')
    #test.getRecord()
