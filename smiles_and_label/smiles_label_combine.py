import math

import cv2
import numpy as np

import re

from smiles_and_label.readImage import OsraSmiles


def combineNameOCR(coordinates):
    # [[[x1,x2], [y1,y2], name, True], .... ]
    mindistance = 1000000
    output = []

    for coordinate in coordinates:

        x1 = coordinate[0][0]
        x2 = coordinate[0][1]
        y1 = coordinate[1][0]
        y2 = coordinate[1][1]
        name = coordinate[2]
        accuracy = coordinate[3]

        if x2 - x1 < mindistance:
            mindistance = x2 - x1

        if len(output) != 0:
            done = True
            for temp in output:
                x = temp[0]
                y = temp[1]
                if x[0] < x1 < x[1] and (y[0] < y1 < y[1] or y[0] < y2 < y[1] or (y1 < y[0] and y2 > y[1])):
                    temp[0][1] = x2
                    temp[1][0] = min(y[0], y1)
                    temp[1][1] = max(y[1], y2)
                    temp[2] = temp[2] + name
                    temp[4] = 'True'
                    done = False
                    break

                if x[0] < x2 < x[1] and (y[0] < y1 < y[1] or y[0] < y2 < y[1] or (y1 < y[0] and y2 > y[1])):
                    temp[0][0] = x1
                    temp[1][0] = min(y[0], y1)
                    temp[1][1] = max(y[1], y2)
                    temp[2] = name + temp[2]
                    temp[4] = 'True'
                    done = False
                    break

            if done:
                output.append([[x1, x2], [y1, y2], name, accuracy, 'False'])
        else:
            output.append([[x1, x2], [y1, y2], name, accuracy, 'False'])

    for item in output:
        if item[4] == 'False':
            if item[2] not in '"!@#$%^&*()-+?_=,<>/"':
                item[0][1] += mindistance
            else:
                output.remove(item)

    return output


def getSmiles(coordinates):
    output = []
    for items in coordinates:
        temp = []
        item = items.split(" ")
        temp.append(item[0])
        coor = item[1].replace("\n", '')
        coor = coor.split("x")

        x1 = coor[0]
        y2 = coor[2]
        y1x2 = coor[1].split("-")
        if len(y1x2) == 3:
            y1x2 = [y1x2[0] + y1x2[1], y1x2[2]]
        y1 = y1x2[0]
        x2 = y1x2[1]

        temp.append([int(x1), int(x2)])
        temp.append([int(y1), int(y2)])
        output.append(temp)
        # [['smiles', [x1,x2], [y1,y2]], .... ]
        # ['c1cc2ccc3c4c2c(c1)c1cccc2c1[Co]4c1c(o3)cccc1o2', [0, 446], [0, 564]]
    return output


def combineSmilewithName(coordinates, nameCoordinates):
    for index in range(len(coordinates)):
        xdistance = 1000000000
        ydistance = 1000000000
        centerSmile = [sum(coordinates[index][1]) / 2, sum(coordinates[index][2]) / 2]
        tempName = []
        for item in nameCoordinates:
            centerName = [sum(item[0]) / 2, sum(item[1]) / 2]

            # if the max x of name is less than min x of smile or
            # if the min x of name is larger than max x of smile or
            # if the min y of name is less than min y of smile

            # then ingore

            if item[0][1] <= coordinates[index][1][0] or \
                    item[0][0] >= coordinates[index][1][1] or \
                    item[1][0] <= coordinates[index][2][0]:
                continue


            # new distance: check the min y of name to the max y of smile
            tempyDistance = abs(coordinates[index][2][1] - item[1][0])
            #tempxDistance = abs(centerSmile[0]-centerName[0])
            #print(coordinates[index], item, tempyDistance, ydistance)
            if tempyDistance <= ydistance:
                ydistance = tempyDistance
                tempName = item

        if len(tempName) > 1:
            coordinates[index] += tempName
            nameCoordinates.remove(tempName)

    return coordinates



def generateSmileandNameImage(coordinates):
    coordinate = coordinates
    # find the default
    for item in coordinate:
        smilex = item[1]
        smiley = item[2]
        namex = item[3]
        namey = item[4]
        minx = int(min(min(smilex), min(namex)))
        maxx = int(max(max(smilex), max(namex)))
        miny = int(min(min(smiley), min(namey)))
        maxy = int(max(max(smiley), max(namey)))

        item.remove(smilex)
        item.remove(smiley)
        item.remove(namex)
        item.remove(namey)

        item.append([minx, maxx])
        item.append([miny, maxy])

    return coordinate


def extractImage(image, x1, x2, y1, y2, save):
    image = cv2.imread(image)
    y, x, c = image.shape

    if x1 < 0: x1 = 0
    if x2 > x: x2 = x
    if y1 < 0: y1 = 0
    if y2 > y: y2 = y

    crop_img = image[int(y1):int(y2), int(x1):int(x2)]
    cv2.imwrite(save, crop_img)


if __name__ == '__main__':
    os = OsraSmiles()

    result = os.readNamefromImageOCR('/Users/luoyu/PycharmProjects/protoKG/extractor/images/2.png')

    output = combineNameOCR(result)
    '''
    for i in range(len(output)):
        value = output[i]

        extractImage('/Users/luoyu/PycharmProjects/protoKG/osra/input/2.png', value[0][0], value[0][1], value[1][0],
                     value[1][1],
                     '/Users/luoyu/PycharmProjects/protoKG/osra/image/' + str(i) + '.png')
        output[i].append('/Users/luoyu/PycharmProjects/protoKG/osra/image/' + str(i) + '.png')

    result = os.runOsraSmiles('/Users/luoyu/PycharmProjects/protoKG/osra/input',
                              '/Users/luoyu/PycharmProjects/protoKG/osra/output', 'sample', '2.png')

    result = getSmiles(result)
    output = combineSmilewithName(result, output)

    output = generateSmileandNameImage(output)
    for i in range(len(output)):
        value = output[i]

        try:
            extractImage('/Users/luoyu/PycharmProjects/protoKG/osra/input/2.png', value[4][0], value[4][1], value[5][0],
                         value[5][1], '/Users/luoyu/PycharmProjects/protoKG/osra/image/' + str(i) + '.png')
        except Exception as e:
            print("Error: ", e)
    '''