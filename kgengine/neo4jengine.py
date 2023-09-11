from neo4j import GraphDatabase

class KG:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def print(self, message):
        with self.driver.session() as session:
            greeting = session.execute_write(self._create_and_return, message)
            print(greeting)

    def update(self, id, par, info):
        with self.driver.session() as session:
            result = session.execute_write(self._updateNode, id, par, info)

    def createNode(self, key_value_list, label):
        with self.driver.session() as session:
            result = session.execute_write(self._createNode, key_value_list, label)
            return result

    def queryNode_dict(self, info, label):
        with self.driver.session() as session:
            result = session.execute_write(self._queryNode_dict, info, label)
            return result

    def queryNode_id(self, label, id, par):
        with self.driver.session() as session:
            result = session.execute_write(self._queryNode_id, label, id, par)
            return result

    def createRelationship(self, id_from, id_to, relationship):
        for item_from in id_from:
            for item_to in id_to:
                with self.driver.session() as session:
                    session.execute_write(self._createRelationship, item_from, item_to, relationship)

    @staticmethod
    def _updateNode(tx, id, par, info):
        message = "MATCH (a) "
        message += "WHERE id(a) = " +str(id) + " "
        if isinstance(info, list):
            message += "SET a." + par + " = " + str(info)
        else:
            message += "SET a." + par + " = '" + str(info) + "'"

        tx.run(message)

    @staticmethod
    def _createRelationship(tx, id_from, id_to, relationship):
        message = "MATCH (a), (b) "
        message += "WHERE id(a) = " + str(id_from) + " AND id(b) = " + str(id_to) + " "
        message += "MERGE (a)-[r:" + relationship + "]->(b)"
        tx.run(message)

    @staticmethod
    def _createNode(tx, key_value_list, label):
        message = "CREATE (record:" + label + " {"
        for key in key_value_list.keys():
            if isinstance(key_value_list[key], list):
                message += str(key) + ": " + str(key_value_list[key]) + ", "
            else:
                message += str(key)+": '"+str(key_value_list[key]) + "', "
        message = message[:-2]
        message += "}) RETURN id(record)"

        result = tx.run(message)

        return result.single()[0]

    @staticmethod
    def _queryNode_dict(tx, info, label):
        message = "MATCH (record:" + label + ") "
        message += "WHERE "

        for key in info.keys():
            if isinstance(info[key], list):
                for item in info[key]:
                    message += "record." + str(key) + " CONTAINS '" + str(item) + "' AND "
            else:
                message += "record." + str(key) + " CONTAINS '" + str(info[key]) + "' AND "
        message = message[:-4]
        message += "RETURN id(record)"

        result = tx.run(message).single()

        if result is not None:
            return result[0]
        return None

    @staticmethod
    def _queryNode_id(tx, label, id, par):
        message = "MATCH (record:" + label + ") "
        message += "WHERE id(record) = " + str(id) + ' '
        message += "RETURN record." + par
        print(message)
        result = tx.run(message).single()

        if result is not None:
            return result[0]
        return None


if __name__ == "__main__":
    greeter = KG("bolt://localhost:7687", "neo4j", "admin")
    doi = greeter.queryNode_dict({'doi':'1'}, "biblio")
    print(doi)
    #greeter.update(479, 'doi', ['1', '2'])
    greeter.close()