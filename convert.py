#Place me in the directory with the .svg output files. 

from cairosvg import svg2png
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
count = 1
for filename in os.listdir(dir_path):
    if filename.endswith(".svg"):
        fileData = open(filename,'r').read()
        dataList = fileData.split("\n")
        dataString = "\n"
        dataString = dataString.join(dataList[2:])
        svg2png(bytestring=dataString,write_to='frame' + str(filename[-8:-4])  + '.png')
        print('frame' + str(filename[-8:-4])  + '.png Total count:' + str(count))
        count += 1
    else:
        continue

