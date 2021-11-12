# -*- coding: utf-8 -*-
"""矢量转栅格"""
import glob
import os
from osgeo import gdal, gdalconst
from osgeo import ogr
import argparse
import time


def Shape2raster(imagePath, shapePath, outputPath, value=False):
    rasterFile = imagePath  # 原影像
    shpFile = shapePath  # 矢量文件
    dataset = gdal.Open(rasterFile, gdalconst.GA_ReadOnly)
    geo_transform = dataset.GetGeoTransform()
    cols = dataset.RasterXSize  # 列数
    rows = dataset.RasterYSize  # 行数
    shp = ogr.Open(shpFile, 0)
    m_layer = shp.GetLayerByIndex(0)
    target_ds = gdal.GetDriverByName('GTiff').Create(outputPath, xsize=cols, ysize=rows, bands=1,
                                                     eType=gdal.GDT_Byte)
    target_ds.SetGeoTransform(geo_transform)
    target_ds.SetProjection(dataset.GetProjection())
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(0)
    band.FlushCache()
    if value:
        gdal.RasterizeLayer(target_ds, [1], m_layer, options=["ATTRIBUTE=val"])  # 用shp字段给栅格像元赋值
    else:
        gdal.RasterizeLayer(target_ds, [1], m_layer)  # 多边形内像元值的全是255
    del dataset
    del target_ds
    shp.Release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default=r"C:\Users\Administrator\Desktop\djh\image", help='image path')
    parser.add_argument('--shape', type=str, default=r"C:\Users\Administrator\Desktop\djh\shape", help='ESRI shapefile path')
    parser.add_argument('--output', type=str, default=r"C:\Users\Administrator\Desktop\djh\result", help='output_raster path')
    opt = parser.parse_args()
    start = time.time()
    imageList = glob.glob(os.path.join(opt.image, "*.tif"))
    outputPath = opt.output
    for imagePath in imageList:
        print("当前影像:", os.path.split(imagePath)[1])
        shapePath = os.path.join(opt.shape, os.path.split(imagePath)[1].split(".tif")[0] + ".shp")
        output = os.path.join(outputPath, os.path.split(imagePath)[1])
        if not os.path.exists(output):
            Shape2raster(imagePath, shapePath, output)
    end = time.time()
    print("用时{}秒".format((end - start)))
