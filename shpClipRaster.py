# -*- coding: utf-8 -*-
"""矢量裁剪栅格"""
import os
from osgeo import gdal, ogr
from multiprocessing.dummy import Pool as ThreadPool
import argparse
import time
import glob

gdal.UseExceptions()


def world2Pixel(geoMatrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / xDist)
    return (pixel, line)


def write_img(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype, options=["TILED=YES", "COMPRESS=LZW"])

    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_proj)
    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset


def shpClipRaster(shapefile_path, raster_path, save_path):
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()
    geoProj = srcImage.GetProjection()
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer(os.path.split(os.path.splitext(shapefile_path)[0])[1])
    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)
    clip = srcImage.ReadAsArray(ulX, ulY, pxWidth, pxHeight)
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY
    write_img(save_path, geoProj, geoTrans, clip)
    gdal.ErrorReset()


def main(shapePath):
    print("当前矢量:", os.path.split(shapePath)[1])
    outputName = os.path.split(shapePath)[1].split(".shp")[0] + ".tif"
    output = os.path.join(outputPath, outputName)
    try:
        if not os.path.exists(output):
            shpClipRaster(shapePath, opt.image, output)
    except:
        print("异常影像:", os.path.split(shapePath)[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default="", help='image path')
    parser.add_argument('--shape', type=str, default="", help='ESRI shapefile path')
    parser.add_argument('--output', type=str, default="", help='output_raster path')
    opt = parser.parse_args()
    start = time.time()
    shapeList = glob.glob(os.path.join(opt.shape, "*.shp"))
    outputPath = opt.output
    numworkers = 16
    pool = ThreadPool(numworkers)  # 创建多线程
    pool.map(main, shapeList)
    pool.close()
    pool.join()
    end = time.time()
    print("用时{}秒".format((end - start)))
