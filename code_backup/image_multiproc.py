import uuid
from time import time, sleep
from PIL import Image
import json
# import requests
import os
import boto3
import multiprocessing as mp
import function.ops as ops

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

def unit_test(file_name, image_path):
    start = time()
    print(file_name)
    print(image_path)
    sleep(1)
    file_paths = file_name+image_path
    latency = time() - start
    return latency, file_paths

def img_multiproc(num_proc, download_path):
    # with mp.Pool() as pool:
    #     return pool.map(image_processing, args=)
    img_path_list = []
    download_path_list = []
    procArr = []
    for i in range(num_proc):
        img_path_list.append("sample_"+str(i)+".jpg")
        download_path_list.append(download_path)
    merged_list = [(img_path_list[i], download_path_list[i]) for i in range(0, len(img_path_list))]

    start = time()
    all_latency = []
    all_file_path = []
    with mp.Pool() as pool:
        res = pool.starmap(image_processing, merged_list)
        for i in res:
            all_latency.append(i[0])
            all_file_path.append(i[1])
    timeTaken = time() - start
    print("the slowest:", timeTaken)
    # print(all_latency)
    # print(all_file_path)
    # for i in range(num_proc):
    #     p = mp.Process(target=image_processing, args=(img_path_list, download_path_list))
    #     procArr.append(p)

    # for p in procArr:
	# 	p.start() 

	# for p in procArr:
	# 	p.join()
    for each_sample in all_file_path:
        for upload_path in each_sample:
            os.remove(upload_path)
   
    return sum(all_latency) / len(all_latency)

def handle(req):
    payload = json.loads(req)
    f_access_id = open("/var/openfaas/secrets/access-id", "r")
    access_id = f_access_id.read()
    f_access_id.close()
    f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
    secret_key = f_secret_key.read()
    f_secret_key.close()

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_key
    )
    input_bucket = "lyuze"
    if 'img_size' in payload:
        img_size = payload['img_size']
        object_key = "img_proc/" + img_size + ".jpg"
        # img_url = choose_img(img_size)
    else:
        object_key = "img_proc/1mb.jpg"
        # img_url = "https://sample-videos.com/img/Sample-jpg-image-1mb.jpg"
    if 'parallel_num' in payload:
        parallel_num = int(payload['parallel_num'])
    else:
        parallel_num = 12

    download_path = './{}{}'.format(uuid.uuid4(), ".jpg")
    img_name = "sample.jpg"

    # download_file(img_url, download_path)
    s3_client.download_file(input_bucket, object_key, download_path)

    # parallel_num = 12
    # img_multiproc(parallel_num)

    # latency, path_list = image_processing(img_name, download_path)
    latency = img_multiproc(parallel_num, download_path)

    # for upload_path in path_list:
    #     os.remove(upload_path)
    #     s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_NAME_INDEX])
    os.remove(download_path)

    print(latency)
    return latency
