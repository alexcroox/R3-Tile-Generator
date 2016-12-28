from PIL import Image
import boto3
from botocore.client import Config
import math
import os
import io

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
tileSize = 256

# Resize original image into individual images for each zoom level for 
# faster parrallel processing for tileZoomLevel()
def resize(event, context):

    approvedZoomList = None

    if "zoomList" in event:
        approvedZoomList = event['zoomList']

    sourceImageName = event['sourceImageName']

    print "Generating overview images for %s" % (sourceImageName)

    s3.Bucket('r3maps-raw').download_file(sourceImageName + ".png", "/tmp/original.png")

    img = Image.open("/tmp/original.png");
    sourceImageWidth, sourceImageHeight = img.size

    maxZoom = int(math.ceil(math.log(max(sourceImageWidth, sourceImageHeight) / tileSize, 2)))

    print "Max zoom: %d" % (maxZoom)

    for x in range(0, maxZoom + 1):

        if approvedZoomList and x not in approvedZoomList:
            print "Ignoring level: %d" % (x)
            continue

        print "Resizing level: %d" % (x)

        zoomLevelResizeWidth = int(math.pow(2, 8 + x))

        print "zoomLevelResizeWidth: %d" % (zoomLevelResizeWidth)    
        resizedImage = img.resize((zoomLevelResizeWidth, zoomLevelResizeWidth), Image.ANTIALIAS)

        resizedFileName = "%d.png" % (x)
        resizedFilePath = "/tmp/%s" % (resizedFileName) 

        resizedImage.save(resizedFilePath)

        s3.Bucket('r3maps').put_object(Key="1.processing/" + sourceImageName + "/" + resizedFileName, Body=open(resizedFilePath, 'rb'))

        # Terrible attempt at forcing garbage collection
        del resizedImage

def tileZoomLevel(event, context):

    sourceImageName = event['sourceImageName']
    zoomLevel = event['zoomLevel']

    s3.Bucket('r3maps').download_file("1.processing/" + sourceImageName + "/" + str(zoomLevel) + ".png", "/tmp/original.png")

    img = Image.open("/tmp/original.png");
    sourceImageWidth, sourceImageHeight = img.size

    currentCoordsX = 0
    currentXCount = 0

    currentCoordsY = 0
    currentYCount = 0

    while (currentCoordsX < sourceImageWidth):

        while (currentCoordsY <= sourceImageWidth):

            s3Path = sourceImageName + "/tiles/%d/%d/%d.png" % (zoomLevel, currentXCount, currentYCount)

            #tileExists = s3.Bucket('r3maps').get_key(s3Path)
            tileExists = False

            if (tileExists):
                print "Ignoring %s" % (s3Path)
            else:
                left = currentCoordsX
                right = currentCoordsX + tileSize
                top = currentCoordsY
                bottom = currentCoordsY + tileSize

                tile = img.crop((left, top, right, bottom))

                imgByteArr = io.BytesIO()
                tile.save(imgByteArr, format='PNG')
                imgByteArr = imgByteArr.getvalue()

                s3.Bucket('r3maps').put_object(Key=s3Path, Body=imgByteArr)

                del tile

            currentCoordsY += tileSize
            currentYCount += 1

        currentCoordsY = 0
        currentYCount = 0

        currentCoordsX += tileSize
        currentXCount += 1

        print "/%d/%d" % (zoomLevel, currentXCount)

    print "All tiles generated!"