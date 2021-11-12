import time
from osgeo import gdal, gdalconst
import glob, os
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count


def ReprojectImages(arg):
    # 获取输出影像信息
    inputrasfile = gdal.Open(arg[0], gdal.GA_ReadOnly)
    inputProj = inputrasfile.GetProjection()
    # 获取参考影像信息
    referencefile = gdal.Open(arg[1], gdal.GA_ReadOnly)
    referencefileProj = referencefile.GetProjection()
    referencefileTrans = referencefile.GetGeoTransform()
    bandreferencefile = referencefile.GetRasterBand(1)
    Width = referencefile.RasterXSize
    Height = referencefile.RasterYSize
    nbands = referencefile.RasterCount
    # 创建重采样输出文件（设置投影及六参数）
    driver = gdal.GetDriverByName('GTiff')
    output = driver.Create(arg[2], Width, Height, nbands, bandreferencefile.DataType)
    output.SetGeoTransform(referencefileTrans)
    output.SetProjection(referencefileProj)
    # 参数说明 输入数据集、输出文件、输入投影、参考投影、重采样方法(最邻近内插\双线性内插\三次卷积等)、回调函数
    gdal.ReprojectImage(inputrasfile, output, inputProj, referencefileProj, gdalconst.GRA_Bilinear, 0.0, 0.0, )


if __name__ == "__main__":
    start = time.time()
    inputList = glob.glob(r"E:\04_result\2021/*.tif")  # 待重采样影像
    refPath = r"E:\04_result\2020"  # 参考影像
    outputPath = r"E:\04_result\2021_warp"  # 输出路径
    referenceList, outputList = [], []
    for input in inputList:
        reference = os.path.join(refPath, os.path.split(input)[1])
        output = os.path.join(outputPath, os.path.split(input)[1])
        referenceList.append(reference)
        outputList.append(output)
    arg = zip(inputList, referenceList, outputList)
    pool = ThreadPool(cpu_count())
    pool.map(ReprojectImages, arg)
    pool.close()
    pool.join()
    end = time.time()
    print("用时{}秒".format((end - start)))