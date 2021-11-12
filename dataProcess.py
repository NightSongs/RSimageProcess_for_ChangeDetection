from osgeo import gdal, osr, ogr
import numpy as np
import os


# 由二值图创建矢量文件
def raster2poly(raster, outshp):
    inraster = gdal.Open(raster)  # 读取路径中的栅格数据
    inband = inraster.GetRasterBand(1)  # 这个波段就是最后想要转为矢量的波段，如果是单波段数据的话那就都是1
    prj = osr.SpatialReference()
    prj.ImportFromWkt(inraster.GetProjection())  # 读取栅格数据的投影信息，用来为后面生成的矢量做准备

    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outshp):  # 若文件已经存在，则删除它继续重新做一遍
        drv.DeleteDataSource(outshp)
    Polygon = drv.CreateDataSource(outshp)  # 创建一个目标文件
    Poly_layer = Polygon.CreateLayer(raster[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)  # 对shp文件创建一个图层，定义为多个面类
    newField = ogr.FieldDefn('value', ogr.OFTReal)  # 给目标shp文件添加一个字段，用来存储原始栅格的pixel value
    Poly_layer.CreateField(newField)

    gdal.Polygonize(inband, inband, Poly_layer, -1, [], callback=None)  # 核心函数，执行的就是栅格转矢量操作
    Polygon.SyncToDisk()
    Polygon = None


#  读取tif数据集
def readTif(fileName, xoff=0, yoff=0, data_width=0, data_height=0):
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


#  保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, path):
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
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset


#  tif裁剪（tif像素数据，裁剪边长）
def TifCroppingArray(im_data, SideLength, im_width, im_height):
    img = im_data
    TifArrayReturn = []
    #  列上图像块数目
    if (len(img.shape) == 2):
        #  列上图像块数目
        ColumnNum = int((img.shape[0] - SideLength * 2) / (256 - SideLength * 2))
        #  行上图像块数目
        RowNum = int((img.shape[1] - SideLength * 2) / (256 - SideLength * 2))
    else:
        #  列上图像块数目
        ColumnNum = int((im_height - SideLength * 2) / (256 - SideLength * 2))
        #  行上图像块数目
        RowNum = int((im_width - SideLength * 2) / (256 - SideLength * 2))
    for i in range(ColumnNum):
        TifArray = []
        for j in range(RowNum):
            if (len(img.shape) == 2):
                cropped = img[i * (256 - SideLength * 2): i * (256 - SideLength * 2) + 256,
                          j * (256 - SideLength * 2): j * (256 - SideLength * 2) + 256]
            else:
                cropped = img[:,
                          i * (256 - SideLength * 2): i * (256 - SideLength * 2) + 256,
                          j * (256 - SideLength * 2): j * (256 - SideLength * 2) + 256]
            TifArray.append(cropped)
        TifArrayReturn.append(TifArray)
    #  考虑到行列会有剩余的情况，向前裁剪一行和一列
    #  向前裁剪最后一列
    for i in range(ColumnNum):
        if (len(img.shape) == 2):
            cropped = img[i * (256 - SideLength * 2): i * (256 - SideLength * 2) + 256,
                      (img.shape[1] - 256): img.shape[1]]
        else:
            cropped = img[:,
                      i * (256 - SideLength * 2): i * (256 - SideLength * 2) + 256,
                      (im_width - 256): im_width]
        TifArrayReturn[i].append(cropped)
    #  向前裁剪最后一行
    TifArray = []
    for j in range(RowNum):
        if (len(img.shape) == 2):
            cropped = img[(img.shape[0] - 256): img.shape[0],
                      j * (256 - SideLength * 2): j * (256 - SideLength * 2) + 256]
        else:
            cropped = img[:,
                      (im_height - 256): im_height,
                      j * (256 - SideLength * 2): j * (256 - SideLength * 2) + 256]
        TifArray.append(cropped)
    #  向前裁剪右下角
    if (len(img.shape) == 2):
        cropped = img[(img.shape[0] - 256): img.shape[0],
                  (img.shape[1] - 256): img.shape[1]]
    else:
        cropped = img[:,
                  (im_height - 256): im_height,
                  (im_width - 256): im_width]
    TifArray.append(cropped)
    TifArrayReturn.append(TifArray)
    if (len(img.shape) == 2):
        #  列上的剩余数
        ColumnOver = (img.shape[0] - SideLength * 2) % (256 - SideLength * 2) + SideLength
        #  行上的剩余数
        RowOver = (img.shape[1] - SideLength * 2) % (256 - SideLength * 2) + SideLength
    else:
        #  列上的剩余数
        ColumnOver = (img.shape[1] - SideLength * 2) % (256 - SideLength * 2) + SideLength
        #  行上的剩余数h
        RowOver = (img.shape[2] - SideLength * 2) % (256 - SideLength * 2) + SideLength
    return TifArrayReturn, RowOver, ColumnOver


#  获得结果矩阵
def Result(shape, TifArray, npyfile, RepetitiveLength, RowOver, ColumnOver, format):
    result = np.zeros(shape, format)
    size = 256
    #  j来标记行数
    j = 0
    for i, item in enumerate(npyfile):
        img = item
        img = img.reshape(size, size)
        #  最左侧一列特殊考虑，左边的边缘要拼接进去
        if (i % len(TifArray[0]) == 0):
            #  第一行的要再特殊考虑，上边的边缘要考虑进去
            if (j == 0):
                result[0: size - RepetitiveLength, 0: size - RepetitiveLength] = img[0: size - RepetitiveLength,
                                                                                 0: size - RepetitiveLength]
            #  最后一行的要再特殊考虑，下边的边缘要考虑进去
            elif (j == len(TifArray) - 1):
                #  后来修改的
                result[shape[0] - ColumnOver - RepetitiveLength: shape[0], 0: size - RepetitiveLength] = img[
                                                                                                         size - ColumnOver - RepetitiveLength: size,
                                                                                                         0: size - RepetitiveLength]
            else:
                result[j * (size - 2 * RepetitiveLength) + RepetitiveLength: (j + 1) * (
                        size - 2 * RepetitiveLength) + RepetitiveLength,
                0:size - RepetitiveLength] = img[RepetitiveLength: size - RepetitiveLength, 0: size - RepetitiveLength]
        #  最右侧一列特殊考虑，右边的边缘要拼接进去
        elif (i % len(TifArray[0]) == len(TifArray[0]) - 1):
            #  第一行的要再特殊考虑，上边的边缘要考虑进去
            if (j == 0):
                result[0: size - RepetitiveLength, shape[1] - RowOver: shape[1]] = img[0: size - RepetitiveLength,
                                                                                   size - RowOver: size]
            #  最后一行的要再特殊考虑，下边的边缘要考虑进去
            elif (j == len(TifArray) - 1):
                result[shape[0] - ColumnOver: shape[0], shape[1] - RowOver: shape[1]] = img[size - ColumnOver: size,
                                                                                        size - RowOver: size]
            else:
                result[j * (size - 2 * RepetitiveLength) + RepetitiveLength: (j + 1) * (
                        size - 2 * RepetitiveLength) + RepetitiveLength,
                shape[1] - RowOver: shape[1]] = img[RepetitiveLength: size - RepetitiveLength, size - RowOver: size]
            #  走完每一行的最右侧，行数+1
            j = j + 1
        #  不是最左侧也不是最右侧的情况
        else:
            #  第一行的要特殊考虑，上边的边缘要考虑进去
            if (j == 0):
                result[0: size - RepetitiveLength,
                (i - j * len(TifArray[0])) * (size - 2 * RepetitiveLength) + RepetitiveLength: (i - j * len(
                    TifArray[0]) + 1) * (size - 2 * RepetitiveLength) + RepetitiveLength
                ] = img[0: size - RepetitiveLength, RepetitiveLength: size - RepetitiveLength]
            #  最后一行的要特殊考虑，下边的边缘要考虑进去
            if (j == len(TifArray) - 1):
                result[shape[0] - ColumnOver: shape[0],
                (i - j * len(TifArray[0])) * (size - 2 * RepetitiveLength) + RepetitiveLength: (i - j * len(
                    TifArray[0]) + 1) * (size - 2 * RepetitiveLength) + RepetitiveLength
                ] = img[size - ColumnOver: size, RepetitiveLength: size - RepetitiveLength]
            else:
                result[j * (size - 2 * RepetitiveLength) + RepetitiveLength: (j + 1) * (
                        size - 2 * RepetitiveLength) + RepetitiveLength,
                (i - j * len(TifArray[0])) * (size - 2 * RepetitiveLength) + RepetitiveLength: (i - j * len(
                    TifArray[0]) + 1) * (size - 2 * RepetitiveLength) + RepetitiveLength,
                ] = img[RepetitiveLength: size - RepetitiveLength, RepetitiveLength: size - RepetitiveLength]
    return result


# opencv转gdal
def OpencvData2GdalData(OpencvImg_data):
    # 若为二维，格式相同
    if (len(OpencvImg_data.shape) == 2):
        GdalImg_data = OpencvImg_data
    else:
        if 'int8' in OpencvImg_data.dtype.name:
            GdalImg_data = np.zeros((OpencvImg_data.shape[2], OpencvImg_data.shape[0], OpencvImg_data.shape[1]),
                                    np.uint8)
        elif 'int16' in OpencvImg_data.dtype.name:
            GdalImg_data = np.zeros((OpencvImg_data.shape[2], OpencvImg_data.shape[0], OpencvImg_data.shape[1]),
                                    np.uint16)
        else:
            GdalImg_data = np.zeros((OpencvImg_data.shape[2], OpencvImg_data.shape[0], OpencvImg_data.shape[1]),
                                    np.float32)
        for i in range(OpencvImg_data.shape[2]):
            # 注意，opencv为BGR
            data = OpencvImg_data[:, :, OpencvImg_data.shape[2] - i - 1]
            data = np.reshape(data, (OpencvImg_data.shape[0], OpencvImg_data.shape[1]))
            GdalImg_data[i] = data
    return GdalImg_data


# gdal转opencv
def GdalData2OpencvData(GdalImg_data):
    if 'int8' in GdalImg_data.dtype.name:
        OpencvImg_data = np.zeros((GdalImg_data.shape[1], GdalImg_data.shape[2], GdalImg_data.shape[0]), np.uint8)
    elif 'int16' in GdalImg_data.dtype.name:
        OpencvImg_data = np.zeros((GdalImg_data.shape[1], GdalImg_data.shape[2], GdalImg_data.shape[0]), np.uint16)
    else:
        OpencvImg_data = np.zeros((GdalImg_data.shape[1], GdalImg_data.shape[2], GdalImg_data.shape[0]), np.float32)
    for i in range(GdalImg_data.shape[0]):
        OpencvImg_data[:, :, i] = GdalImg_data[GdalImg_data.shape[0] - i - 1, :, :]
    return OpencvImg_data


# 迭代器分块读取遥感影像(无重叠)
def block_read_raster(rasterPath, blcok_size):
    dataset = gdal.Open(rasterPath)
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    for x in range(0, width, blcok_size):
        if x + blcok_size < width:
            cols = blcok_size
        else:
            cols = width - x
        for y in range(0, height, blcok_size):
            if y + blcok_size < height:
                rows = blcok_size
            else:
                rows = height - y
            data = dataset.ReadAsArray(x, y, cols, rows)
            yield data
