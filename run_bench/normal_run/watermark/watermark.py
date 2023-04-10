#!/usr/bin/env python

import datetime, time
import os
import stat
import subprocess
# import json
import boto3
import sys

# from . import storage
# client = storage.storage.get_instance()

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def call_ffmpeg(args):
    ret = subprocess.run(['ffmpeg', '-y'] + args,
            #subprocess might inherit Lambda's input for some reason
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if ret.returncode != 0:
        print('Invocation of ffmpeg failed!')
        print('Out: ', ret.stdout.decode('utf-8'))
        raise RuntimeError()

# https://superuser.com/questions/556029/how-do-i-convert-a-video-to-gif-using-ffmpeg-with-reasonable-quality
def to_gif(video, duration):
    output = SCRIPT_DIR+'/processed-{}.gif'.format(os.path.basename(video))
    call_ffmpeg(["-i", video,
        # "-t",
        # "{0}".format(duration),
        "-vf",
        "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "-loop", "0",
        output])
    print(output)
    # time.sleep(10)
    return output

# https://devopstar.com/2019/01/28/serverless-watermark-using-aws-lambda-layers-ffmpeg/
def watermark(video, duration):
    output = SCRIPT_DIR+'/processed-{}'.format(os.path.basename(video))
    watermark_file = os.path.dirname(os.path.realpath(__file__))
    # print(watermark_file)
    call_ffmpeg([
        "-i", video,
        "-i", os.path.join(watermark_file, os.path.join('watermark.png')),
        "-filter_complex", "overlay=main_w/2-overlay_w/2:main_h/2-overlay_h/2",
        output])
    print(output)
    return output

def transcode_mp3(video, duration):
    print("placeholder, not implemented..")
    pass

operations = { 'transcode' : transcode_mp3, 'to_gif' : to_gif, 'watermark' : watermark }

def main():
    # input_bucket = event.get('bucket').get('input')
    # output_bucket = event.get('bucket').get('output')
    # key = event.get('object').get('key')
    # duration = event.get('object').get('duration')
    # op = event.get('object').get('op')
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

    # payload = json.loads(req)
    # video = payload['video']
    video = sys.argv[1]
    op = sys.argv[2] # watermark
    video_full_name = video+'.mp4'
    # print(SCRIPT_DIR)

    download_path = os.path.join(SCRIPT_DIR, video_full_name)
    if os.path.isfile(download_path) == False:
        download_begin = datetime.datetime.now()
        s3_client.download_file(input_bucket, "video_proc/"+video_full_name, download_path)
        download_size = os.path.getsize(download_path)
        download_stop = datetime.datetime.now()

    # Restore executable permission
    # print(download_path)
    # ffmpeg_binary = os.path.join(SCRIPT_DIR, 'ffmpeg', 'ffmpeg')
    # # needed on Azure but read-only filesystem on AWS
    # try:
    #     st = os.stat(ffmpeg_binary)
    #     os.chmod(ffmpeg_binary, st.st_mode | stat.S_IEXEC)
    # except OSError:
    #     pass

    process_begin = time.time()
    duration = 1
    upload_path = operations[op](download_path, duration)
    process_end =  time.time()
    os.remove(upload_path)

    # upload_begin = datetime.datetime.now()
    # filename = os.path.basename(upload_path)
    # upload_size = os.path.getsize(upload_path)
    # client.upload(output_bucket, filename, upload_path)
    # upload_stop = datetime.datetime.now()

    # download_time = (download_stop - download_begin) / datetime.timedelta(microseconds=1)
    # upload_time = (upload_stop - upload_begin) / datetime.timedelta(microseconds=1)
    process_time = "{:.2f}".format(process_end - process_begin)
    print(process_time)
    # return {
    #         'result': {
    #             'bucket': output_bucket,
    #             'key': filename
    #         },
    #         'measurement': {
    #             'download_time': download_time,
    #             'download_size': download_size,
    #             'upload_time': upload_time,
    #             'upload_size': upload_size,
    #             'compute_time': process_time
    #         }
    #     }

main()