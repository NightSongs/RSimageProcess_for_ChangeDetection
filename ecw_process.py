# -*- coding: utf-8 -*-
"""install skimage:  pip install scikit-image -i https://pypi.tuna.tsinghua.edu.cn/simple
"""
from osgeo import gdal
import numpy as np
import time
from skimage.transform import resize, rescale


"""read_raster:读取影像
   write_raster:写入影像
   raster_resize:resize/rescale"""


# 读取ecw文件
def read_raster(fileName, xoff=0, yoff=0, data_width=100000, data_height=100000):
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    #  栅格矩阵的列数
    width = dataset.RasterXSize
    #  栅格矩阵的行数
    height = dataset.RasterYSize
    #  波段数
    bands = dataset.RasterCount
    #  获取数据
    if (data_width == 0 and data_height == 0):
        data_width = width
        data_height = height
    data = dataset.ReadAsArray(xoff, yoff, data_width, data_height)
    #  获取仿射矩阵信息
    geotrans = dataset.GetGeoTransform()
    #  获取投影信息
    proj = dataset.GetProjection()
    return width, height, bands, data, geotrans, proj


#  保存ecw文件
def write_raster(im_data, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape

    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i, :, :])
    del dataset


#  resize/rescale
def raster_resize(image, new_width, new_height, use_rescale=False, rescale_zoom=1.25):
    if not use_rescale:
        new_image = resize(image, (image.shape[0], new_height, new_width), anti_aliasing=True)
    else:
        new_image = rescale(image, rescale_zoom, anti_aliasing=False)
    return new_image


if __name__ == "__main__":
    start_time = time.time()
    width, height, bands, data, geotrans, proj = read_raster(r"F:\国家林业局-变化检测项目\ECW\真彩色\2018\hubei_2018.ecw")
    print(data.shape)
    print("process done:", time.time()-start_time)
    # new_width, new_height = width / 100, height / 100
    # new_image = raster_resize(data, new_width, new_height)
    # write_raster(new_image, geotrans, proj, r"D:\jjw\Python/test.tif")
