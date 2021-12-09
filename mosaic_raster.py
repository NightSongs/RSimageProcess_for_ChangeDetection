import os
import glob
from osgeo import gdal
from math import ceil
from tqdm import tqdm


def GetExtent(infile):
    ds = gdal.Open(infile)
    geotrans = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    min_x, max_y = geotrans[0], geotrans[3]
    max_x, min_y = geotrans[0] + xsize * geotrans[1], geotrans[3] + ysize * geotrans[5]
    ds = None
    return min_x, max_y, max_x, min_y


def RasterMosaic(file_list, outpath):
    Open = gdal.Open
    min_x, max_y, max_x, min_y = GetExtent(file_list[0])
    for infile in file_list:
        minx, maxy, maxx, miny = GetExtent(infile)
        min_x, min_y = min(min_x, minx), min(min_y, miny)
        max_x, max_y = max(max_x, maxx), max(max_y, maxy)

    in_ds = Open(file_list[0])
    in_band = in_ds.GetRasterBand(3)

    geotrans = list(in_ds.GetGeoTransform())
    width, height = geotrans[1], geotrans[5]
    columns = ceil((max_x - min_x) / width)  # 列数
    rows = ceil((max_y - min_y) / (-height))  # 行数

    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(outpath, columns, rows, 3, in_band.DataType, options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])
    out_ds.SetProjection(in_ds.GetProjection())
    geotrans[0] = min_x  # 更正左上角坐标
    geotrans[3] = max_y
    out_ds.SetGeoTransform(geotrans)
    inv_geotrans = gdal.InvGeoTransform(geotrans)
    for in_fn in tqdm(file_list):
        in_ds = Open(in_fn)
        in_gt = in_ds.GetGeoTransform()
        offset = gdal.ApplyGeoTransform(inv_geotrans, in_gt[0], in_gt[3])
        x, y = map(int, offset)
        for i in range(3):  #每个波段都要考虑
            data = in_ds.GetRasterBand(i+1).ReadAsArray()
            out_ds.GetRasterBand(i+1).WriteArray(data, x, y)  # x，y是开始写入时左上角像元行列号
    del in_ds, out_ds


if __name__ == '__main__':
    image_path = "image"   #待拼接图片路径
    result_path = "result"  #拼接结果路径
    imageList = glob.glob(image_path + "/*.tif")
    result = os.path.join(result_path, "result.tif")
    RasterMosaic(imageList, result)
