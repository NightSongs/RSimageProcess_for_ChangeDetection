# -*- coding: utf-8 -*-
"""按属性分割矢量"""
from osgeo import ogr, gdal
import os, time
from multiprocessing.dummy import Pool as ThreadPool


def main(shpfile, outPath, Field):
    ds = ogr.Open(shpfile)
    lyr = ds.GetLayer(0)
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")
    driver = ogr.GetDriverByName("ESRI Shapefile")
    numworkers = 16
    pool = ThreadPool(numworkers)  # 创建多线程

    def write_features(feat):
        cityName = feat.GetField(Field)  # 以字段名为文件名称
        outShp = os.path.join(outPath, str(cityName) + '.shp')
        geom = feat.GetGeometryRef()
        if not os.path.exists(outShp):
            outDs = driver.CreateDataSource(outShp)
            outLyr = outDs.CreateLayer("layername", lyr.GetSpatialRef(), ogr.wkbMultiPolygon)
            outLyr.CreateFields(lyr.schema)  # 创建字段属性
            outFeat = ogr.Feature(lyr.GetLayerDefn())
            for i in range(feat.GetFieldCount()):
                val = feat.GetField(i)
                outFeat.SetField(i, val)
            outFeat.SetGeometry(geom)
            outLyr.CreateFeature(outFeat)
            outDs = None
        else:
            outDs = ogr.Open(outShp, 1)
            outLyr = outDs.GetLayerByIndex(0)
            outFeat = ogr.Feature(lyr.GetLayerDefn())
            for i in range(feat.GetFieldCount()):
                val = feat.GetField(i)
                outFeat.SetField(i, val)
            outFeat.SetGeometry(geom)
            outLyr.CreateFeature(outFeat)
            outDs = None

    pool.map(write_features, lyr)
    pool.close()
    pool.join()


if __name__ == "__main__":
    start = time.time()
    shapePath = r"F:\国家林业局-变化检测项目\变化图斑\ESRI_shapefile\湖北2019-2020变化图斑.shp"
    outputPath = r"F:\国家林业局-变化检测项目\变化图斑\ESRI_shapefile\湖北2019-2020各县变化图斑"
    Field = "c_xianname"
    main(shapePath, outputPath, Field)
    end = time.time()
    print("用时{}秒".format((end - start)))
