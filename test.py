import os
from os import listdir, getcwd
from os.path import join

if __name__ == '__main__':
    source_folder = 'D:/darknet/darknet-master/VOCdevkit/VOC2020/JPEGImages/'
    dest = 'D:/darknet/darknet-master/VOCdevkit/VOC2020/ImageSets/Main/train.txt'
    dest2 = 'D:/darknet/darknet-master/VOCdevkit/VOC2020/ImageSets/Main/val.txt'
    file_list = os.listdir(source_folder)
    train_file = open(dest, 'a')
    val_file = open(dest2, 'a')
    for file_obj in file_list:
        file_path = source_folder + file_obj

        file_name, file_extend = os.path.splitext(file_obj)

        file_num = int(file_name)

        if (file_num < 50):

            train_file.write(file_name + '\n')
        else:
            val_file.write(file_name + '\n')
    train_file.close()
    val_file.close()

