import uuid
from time import time
from PIL import Image
import json
import sys
# import requests
import os
import boto3

import ops as ops

# FILE_NAME_INDEX = 2
Image.MAX_IMAGE_PIXELS = None


def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += ops.flip(image, file_name)
        path_list += ops.rotate(image, file_name)
        path_list += ops.filter(image, file_name)
        path_list += ops.gray_scale(image, file_name)
        path_list += ops.resize(image, file_name)

    latency = time() - start
    return latency, path_list

# def download_file(img_url, download_path):
#     response = requests.get(img_url)
#     open(download_path, "wb").write(response.content)

def choose_img(img_size):
    img_dict = {
        "50kb": "https://sample-videos.com/img/Sample-jpg-image-50kb.jpg",
        "100kb": "https://sample-videos.com/img/Sample-jpg-image-100kb.jpg", 
        "200kb": "https://sample-videos.com/img/Sample-jpg-image-200kb.jpg",
        "500kb": "https://sample-videos.com/img/Sample-jpg-image-500kb.jpg",
        "1mb": "https://sample-videos.com/img/Sample-jpg-image-1mb.jpg",
        "2mb": "https://sample-videos.com/img/Sample-jpg-image-2mb.jpg",
        "5mb": "https://sample-videos.com/img/Sample-jpg-image-5mb.jpg",
        "10mb": "https://sample-videos.com/img/Sample-jpg-image-10mb.jpg",
        "15mb": "https://sample-videos.com/img/Sample-jpg-image-15mb.jpg",
        "20mb": "https://sample-videos.com/img/Sample-jpg-image-20mb.jpg",
        "30mb": "https://sample-videos.com/img/Sample-jpg-image-30mb.jpg",
    }
    return img_dict[img_size]

def main():
    # payload = json.loads(req)
    # f_access_id = open("/var/openfaas/secrets/access-id", "r")
    # access_id = f_access_id.read()
    # f_access_id.close()
    # f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
    # secret_key = f_secret_key.read()
    # f_secret_key.close()

    s3_client = boto3.client(
        's3'
    )
    input_bucket = "lyuze"
    if sys.argv[1] is not None:
        img_size = sys.argv[1]
        object_key = "img_proc/" + img_size + ".jpg"
        # img_url = choose_img(img_size)
    else:
        object_key = "img_proc/1mb.jpg"
        # img_url = "https://sample-videos.com/img/Sample-jpg-image-1mb.jpg"

    download_path = './{}{}'.format(img_size, ".jpg")
    img_name = "sample.jpg"

    # download_file(img_url, download_path)
    if os.path.isfile(download_path) == False:
        s3_client.download_file(input_bucket, object_key, download_path)

    latency, path_list = image_processing(img_name, download_path)

    for upload_path in path_list:
        os.remove(upload_path)
    #     s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_NAME_INDEX])
    # os.remove(download_path)

    print("{:.2f}".format(latency))
    return latency

main()