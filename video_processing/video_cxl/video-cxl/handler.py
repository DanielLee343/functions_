import json
from time import time
import os
import boto3
import uuid
import cv2

tmp = "/home/app/"
def video_processing(object_key, video_path):
    # file_name = object_key.split(".")[FILE_NAME_INDEX]
    file_name = object_key[object_key.find('/')+1:object_key.find('.')]
    result_file_path = tmp+file_name+'-output.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    start = time()
    while video.isOpened():
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tmp_file_path = tmp+'tmp.jpg'
            cv2.imwrite(tmp_file_path, gray_frame)
            gray_frame = cv2.imread(tmp_file_path)
            out.write(gray_frame)
        else:
            break

    latency = time() - start

    video.release()
    out.release()
    return latency, result_file_path

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
    if 'video_size' in payload:
        img_size = payload['video_size']
        object_key = "video_proc/" + img_size + ".mp4"
    else:
        object_key = "video_proc/1mb.mp4"
    download_path = tmp+'{}{}'.format(uuid.uuid4(), ".mp4")
    video = "sample.mp4"
    # download from s3 to container
    s3_client.download_file(input_bucket, object_key, download_path)
    # video processing
    latency, result_path = video_processing(object_key, download_path)
    # remove result file
    os.remove(result_path)
    os.remove(download_path)

    print(latency)
    return latency