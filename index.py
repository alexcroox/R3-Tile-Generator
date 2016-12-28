from PIL import Image
import boto3
from botocore.client import Config
import math
import os

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

def resize(event, context):

    sourceImageName = event['sourceImageName']

    s3.Bucket('r3maps-raw').download_file(sourceImageName + ".png", "/tmp/original.png")
    
    tileSize = 256

    img = Image.open("/tmp/original.png");
    sourceImageWidth, sourceImageHeight = img.size

    maxZoom = int(math.ceil(math.log(max(sourceImageWidth, sourceImageHeight) / tileSize, 2)))

    print(maxZoom)

    for x in range(0, maxZoom + 1):

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