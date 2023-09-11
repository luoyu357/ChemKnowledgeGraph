# if two sections are in the same line, then we can trust them as the label
import os


# find the row and column of labels from the ocr
#from smiles_and_label.smiles_label_align import all_in_one


def align(inputList):
    rowoutput = []
    coloutput = []

    for item_input in inputList:

        if len(rowoutput) == 0:
            rowoutput.append([item_input])
            coloutput.append([item_input])
        else:
            inputy = item_input[1]
            inputx = item_input[0]
            centery = sum(inputy) / 2
            centerx = sum(inputx) / 2

            flagx = True
            flagy = True
            for item_output in rowoutput:
                # y section
                outputy = item_output[0][1]
                if outputy[0] <= centery <= outputy[1]:
                    flagy = False
                    item_output.append(item_input)

            for item_output in coloutput:
                # x section
                outputx = item_output[0][0]
                if outputx[0] <= centerx <= outputx[1]:
                    flagx = False
                    item_output.append(item_input)

            if flagx:
                coloutput.append([item_input])
            if flagy:
                rowoutput.append([item_input])

    return rowoutput, coloutput


# if the row or col contains the same label, remove it
def processRowandCol(row, col):
    row_long = [i for i in row if len(i) > 1]
    col_long = [i for i in col if len(i) > 1]

    linear_order_line = []

    # if row or col doesn't contain the same label and chr(ord(index) + 1) = index+1, then add to the linear_order_line
    for items in row_long:
        items.sort(key=lambda x: x[2])
        index = 0
        while index < len(items)-1:
            if items[index][2] == items[index+1][2]:
                index += 2
            elif items[index][2] != items[index+1][2] and chr(ord(items[index][2].lower())) <= items[index+1][2].lower():
                if items[index] not in linear_order_line:
                    linear_order_line.append(items[index])
                if items[index+1] not in linear_order_line:
                    linear_order_line.append(items[index+1])
            index += 1

    for items in col_long:
        items.sort(key=lambda x: x[2])
        index = 0
        while index < len(items) - 1:
            if items[index][2] == items[index+1][2]:
                index += 2
            elif items[index][2] != items[index + 1][2] and items[index][2].lower() <= items[index + 1][2].lower():
                # number
                # alphabet
                # or others

                if items[index] not in linear_order_line:
                    linear_order_line.append(items[index])
                if items[index + 1] not in linear_order_line:
                    linear_order_line.append(items[index + 1])
            index += 1

    linear_order_line.sort(key=lambda x: x[2])

    return linear_order_line

# if two components has the same label and close coordinate
# set the max/min x and y for that label
def unqiueLabel(ocr, paddle):
    ocr_copy = [i for i in ocr]
    paddle_copy = [i for i in paddle]
    output = []
    for itemocr in ocr:
        xocr = itemocr[0]
        yocr = itemocr[1]
        for itempaddle in paddle:
            xpaddle = itempaddle[0]
            ypaddle = itempaddle[1]

            if itemocr[2] == itempaddle[2]:
                centerocr = [sum(xocr) / 2, sum(yocr) / 2]
                centerpaddle = [sum(xpaddle) / 2, sum(ypaddle) / 2]
                # center of box must be in the range of other
                if (xpaddle[0] <= centerocr[0] <= xpaddle[1] and ypaddle[0] <= centerocr[1] <= ypaddle[1]) or \
                        (xocr[0] <= centerpaddle[0] <= xocr[1] and yocr[0] <= centerpaddle[1] <= yocr[1]):
                    # remove the duplicate
                    newcoor = [[min(xocr[0], xpaddle[0]), max(xocr[1], xpaddle[1])], \
                               [min(yocr[0], ypaddle[0]), max(yocr[1], ypaddle[1])], itemocr[2],
                               min(itemocr[3], itempaddle[3])]
                    output.append(newcoor)
                    ocr_copy.remove(itemocr)
                    paddle_copy.remove(itempaddle)
                    break

    return output, ocr_copy, paddle_copy

#make sure no duplicate label
#for example DOTA and DOTA+, they are in the same coordinate
def detectDuplicate(inputList):
    output = []
    inputList.sort(key=lambda x: len(x[2]))
    for index1 in range(len(inputList)):
        check = True
        if inputList[index1][2] in '":!@#$%^&*()-+?_=,<>/"':
            continue
        for index2 in range(index1 + 1, len(inputList)):
            if inputList[index1][2] in inputList[index2][2]:
                if inputList[index2][0][0] <= sum(inputList[index1][0]) / 2 <= inputList[index2][0][1] and \
                        inputList[index2][1][0] <= sum(inputList[index1][1]) / 2 <= inputList[index2][1][1]:
                    check = False
        if check:
            output.append(inputList[index1])
    return output




'''
if __name__ == '__main__':

    image_path = '/Users/luoyu/PycharmProjects/protoKG/extractor/images/'
    output_path = '/Users/luoyu/PycharmProjects/protoKG/osra/output'
    all_smiles = all_in_one(image_path, output_path)
    print(all_smiles)
'''
