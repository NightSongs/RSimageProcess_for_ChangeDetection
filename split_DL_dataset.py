"""分割变化检测数据集"""
import os
import random
import shutil


# 创建文件夹
def mkdir(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)


# 转移文件函数
def move_data(List, ImageA_Path, ImageB_Path, Label_Path, mode, outputdir):
    datasetPath = os.path.join(outputdir, mode)
    new_ImageAPath = os.path.join(datasetPath, "A")
    new_ImageBPath = os.path.join(datasetPath, "B")
    new_LabelPath = os.path.join(datasetPath, "OUT")
    mkdir(datasetPath)
    mkdir(new_ImageAPath)
    mkdir(new_ImageBPath)
    mkdir(new_LabelPath)
    for name in List:
        ImageA = os.path.join(ImageA_Path, name)
        ImageB = os.path.join(ImageB_Path, name)
        Label = os.path.join(Label_Path, name)
        shutil.move(ImageA, os.path.join(new_ImageAPath, name))
        shutil.move(ImageB, os.path.join(new_ImageBPath, name))
        shutil.move(Label, os.path.join(new_LabelPath, name))


if __name__ == "__main__":
    ImageA_Path = "训练数据集\A"
    ImageB_Path = "训练数据集\B"
    Label_Path = "训练数据集\OUT"
    outputDir = "训练数据集\dataset"
    imageNameList = os.listdir(ImageA_Path)
    train_percent = 0.8
    val_percent = 0.5  # 取出训练集后,test == val, 各50%
    train_List = random.sample(imageNameList, int(len(imageNameList) * train_percent))
    val_test_List = list(set(imageNameList).difference(set(train_List)))  # 取出训练集后剩余的图像
    val_List = random.sample(val_test_List, int(len(val_test_List) * val_percent))
    test_List = list(set(val_test_List).difference(set(val_List)))  # 最后剩下test集图像
    move_data(train_List, ImageA_Path, ImageB_Path, Label_Path, "train", outputDir)
    move_data(val_List, ImageA_Path, ImageB_Path, Label_Path, "val", outputDir)
    move_data(test_List, ImageA_Path, ImageB_Path, Label_Path, "test", outputDir)
