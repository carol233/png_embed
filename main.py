# coding:utf-8
import os
import xml.dom.minidom
from xml.dom.minidom import parse
from xml.dom.minidom import Document
from xml.etree import ElementTree

from PIL import Image

INPUT_IMAGE_DIR = "D:\darknet\darknet-master\VOCdevkit\VOC2007\JPEGImages"
INPUT_ANNO_DIR = "D:\darknet\darknet-master\VOCdevkit\VOC2007\Annotations"
INFO_DIR = "D:\darknet\infopic"
OUTPUT_IMAGE_DIR = "D:\darknet\darknet-master\VOCdevkit\VOC2020\JPEGImages"
OUTPUT_ANNO_DIR = "D:\darknet\darknet-master\VOCdevkit\VOC2020\Annotations"


def readXML(xmlfile):
    domTree = parse(xmlfile)
    rootNode = domTree.documentElement  # annotation

    item = rootNode.getElementsByTagName("xmin")[0]
    xmin = item.firstChild.data

    item = rootNode.getElementsByTagName("ymin")[0]
    ymin = item.firstChild.data

    item = rootNode.getElementsByTagName("xmax")[0]
    xmax = item.firstChild.data

    item = rootNode.getElementsByTagName("ymax")[0]
    ymax = item.firstChild.data

    return domTree, xmin, ymin, xmax, ymax


def _resetXMLfile(filepath):
    emptyline = '\t\n'
    fb_r = open(filepath, 'r')
    result = list()
    for line in fb_r.readlines():
        if emptyline in line:
            continue
        elif len(line) == 1:
            continue
        result.append(line)
    finResult = ''.join(result)
    fb_r.close()
    fb_w = open(filepath, 'w')
    fb_w.write(finResult)
    fb_w .close()


def updateXML(domTree, newimg, newxml, xmin, ymin, xmax, ymax):

    rootNode = domTree.documentElement
    """
    <object>
        <name>close</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>47</xmin>
            <ymin>3</ymin>
            <xmax>58</xmax>
            <ymax>14</ymax>
        </bndbox>
    </object>
    """
    item = rootNode.getElementsByTagName("path")[0]
    item.firstChild.data = newimg

    object_node = domTree.createElement("object")

    # 创建name节点,并设置textValue
    name_node = domTree.createElement("name")
    name_text_value = domTree.createTextNode("info")
    name_node.appendChild(name_text_value)  # 把文本节点挂到name_node节点
    object_node.appendChild(name_node)

    new_node = domTree.createElement("pose")
    new_text_value = domTree.createTextNode("Unspecified")
    new_node.appendChild(new_text_value)
    object_node.appendChild(new_node)

    new_node = domTree.createElement("truncated")
    new_text_value = domTree.createTextNode("0")
    new_node.appendChild(new_text_value)
    object_node.appendChild(new_node)

    new_node = domTree.createElement("difficult")
    new_text_value = domTree.createTextNode("0")
    new_node.appendChild(new_text_value)
    object_node.appendChild(new_node)

    bndbox_node = domTree.createElement("bndbox")
    xmin_node = domTree.createElement("xmin")
    xmin_text_value = domTree.createTextNode(str(int(xmin)))
    xmin_node.appendChild(xmin_text_value)
    ymin_node = domTree.createElement("ymin")
    ymin_text_value = domTree.createTextNode(str(int(ymin)))
    ymin_node.appendChild(ymin_text_value)
    xmax_node = domTree.createElement("xmax")
    xmax_text_value = domTree.createTextNode(str(int(xmax)))
    xmax_node.appendChild(xmax_text_value)
    ymax_node = domTree.createElement("ymax")
    ymax_text_value = domTree.createTextNode(str(int(ymax)))
    ymax_node.appendChild(ymax_text_value)

    bndbox_node.appendChild(xmin_node)
    bndbox_node.appendChild(ymin_node)
    bndbox_node.appendChild(xmax_node)
    bndbox_node.appendChild(ymax_node)
    object_node.appendChild(bndbox_node)

    rootNode.appendChild(object_node)

    with open(newxml, 'w') as f:
        domTree.writexml(f, indent='\t', addindent='\t', newl="\n", encoding="uft-8")
    _resetXMLfile(newxml)


def getFileList(rootDir, pickstr):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pickstr in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


def fixed_size(im, width, height):
    """按照固定尺寸处理图片"""
    out = im.resize((width, height), Image.ANTIALIAS)
    return out


def resize_by_width(im, cls, w_divide_h):
    """按照宽度进行所需比例缩放"""
    (x, y) = im.size
    x_s = x
    y_s = x / w_divide_h
    out = im.resize((x_s, y_s), Image.ANTIALIAS)
    return out


def embed(input, add, output, x, y, h):
    img = Image.open(input).convert('RGBA')
    addImg = Image.open(add).convert('RGBA')
    img_box = (x, y, x + h, y + h)
    addImg = fixed_size(addImg, h, h)  # 正方形
    img.paste(addImg, img_box, addImg)
    img.save(output)


def compute_info_size(xmin, ymin, xmax, ymax):
    height = ymax - ymin  # the same height
    xinfo = xmin - height
    yinfo = ymin

    return xinfo, yinfo, height


if __name__ == '__main__':
    inputjpgs = getFileList(INPUT_IMAGE_DIR, ".jpg")
    addimgs = getFileList(INFO_DIR, ".png")
    count_addimgs = len(addimgs)
    i = 0
    for inputimg in inputjpgs:
        addimg = addimgs[i]
        i = (i + 1) % len(addimgs)
        imgname = os.path.split(inputimg)[-1][:-4]
        xmlpath = os.path.join(INPUT_ANNO_DIR, imgname + ".xml")
        newxml = os.path.join(OUTPUT_ANNO_DIR, imgname + ".xml")
        outputomg = os.path.join(OUTPUT_IMAGE_DIR, imgname + ".jpg")

        domTree, xmin, ymin, xmax, ymax = readXML(xmlpath)
        xinfo, yinfo, hinfo = compute_info_size(int(xmin), int(ymin), int(xmax), int(ymax))
        embed(inputimg, addimg, outputomg, xinfo, yinfo, hinfo)
        updateXML(domTree, outputomg, newxml, xinfo, yinfo, xinfo + hinfo, yinfo + hinfo)









