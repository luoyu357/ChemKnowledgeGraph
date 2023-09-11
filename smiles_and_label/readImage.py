
import subprocess

import cv2
import pytesseract
from PIL import Image
import subprocess
import easyocr
from paddleocr import PaddleOCR


class OsraSmiles:

    def gocr(self, filePath):
        result = subprocess.run(['gocr', filePath], stdout=subprocess.PIPE)
        print(result.stdout)

    def readNamefromImageOCR(self, filePath, lowestAccuracy=0.9):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(filePath)
        output = []
        for item in result:

            coordinate = item[0]
            x1 = int(coordinate[0][0])
            x2 = int(coordinate[1][0])
            y1 = int(coordinate[1][1])
            y2 = int(coordinate[2][1])
            name = item[1]
            accuracy = item[2]

            if accuracy < lowestAccuracy:
                continue
            output.append([[x1, x2], [y1, y2], name, accuracy])

        return output


    def readNamefromImagePaddleOCR(self, filePath, lowestAccuracy=0.9):
        ocr = PaddleOCR(use_angle_cls=True, lang='en')  # need to run only once to download and load model into memory
        img_path = filePath
        result = ocr.ocr(img_path, cls=True)
        output = []
        for item in result[0]:
            coordinate = item[0]
            x1 = int(coordinate[0][0])
            x2 = int(coordinate[1][0])
            y1 = int(coordinate[1][1])
            y2 = int(coordinate[2][1])
            name = item[1][0]
            accuracy = item[1][1]

            if accuracy < lowestAccuracy:
                continue
            output.append([[x1, x2], [y1, y2], name, accuracy])

        return output

    def runOsraSmiles(self, inputPath, outputPath, outputName, inputName):
        subprocess.call(
            ['docker', 'container', 'run', '--rm', '--volume', inputPath+':/input',
             '--volume', outputPath+':/output',
             'daverona/osra', 'osra', '-c', '--write', '/output/'+outputName+'.smi', '/input/'+inputName])
        f = open(outputPath+"/"+outputName+".smi", "r")
        return f.readlines()

if __name__ == '__main__':

    test = OsraSmiles()
    #result = test.runOsraSmiles('/Users/luoyu/PycharmProjects/protoKG/osra/input', '/Users/luoyu/PycharmProjects/protoKG/osra/output','sample','1.gif')
    #result = test.runOsraSmiles('/Users/luoyu/PycharmProjects/protoKG/extractor/images', '/Users/luoyu/PycharmProjects/protoKG/osra/output', 'sample', '6.png')
    result = test.readNamefromImageOCR('/Users/luoyu/PycharmProjects/protoKG/extractor/images/6.png', 0.9)
    print(result)
    result = test.readNamefromImagePaddleOCR('/Users/luoyu/PycharmProjects/protoKG/extractor/images/6.png', 0.9)
    print(result)

