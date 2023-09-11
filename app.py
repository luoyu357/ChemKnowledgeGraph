from flask import Flask
import configparser
from extractor import extractor
from neo4j import GraphDatabase

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/Users/luoyu/PycharmProjects/protoKG/configV1.ini')
    extractor.process(config=config)
    #app.run()