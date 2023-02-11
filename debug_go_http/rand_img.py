from randimage import get_random_image, show_array
import matplotlib
from multiprocessing import Process, Pipe
import time
import requests
import cv2
import boto3
import os

def gen_rand_img():
    parallelIndex = 1
    threads = []
    start = time.time()
    for i in range(parallelIndex):
        width = (i+1) * 1920
        print(i)
        print(width)
        t = Process(target=generate_img, args=(width, i))
        threads.append(t)
    for i in range(parallelIndex):
        threads[i].start()
    for i in range(parallelIndex):
        threads[i].join()

    exec_time = time.time() - start
    print("exec_time:", exec_time)

def generate_img(width, i):
    img_size = (width, width)
    print(img_size)
    img = get_random_image(img_size)  #returns numpy array
    # show_array(img) #shows the image
    matplotlib.image.imsave("./randimage_"+str(i)+".png", img)

def download_file(img_url, download_path):
    response = requests.get(img_url)
    open(download_path, "wb").write(response.content)


def from_api():
    # for i in range(2):
    #     width = (i+1) * 5000
    #     # print(i)
    #     img_url = 'https://picsum.photos/' + str(width)
    #     download_path = "./images/" + str(i) + ".jpg"
    #     print(img_url)
    #     print(download_path)
    #     download_file(img_url, download_path)
    #     time.sleep(5)
    img_size = "10mb"
    img_url = 'https://sample-videos.com/img/Sample-jpg-image-'+img_size+'.jpg'
    download_path = "./images/" + img_size + ".jpg"
    download_file(img_url, download_path)

def concat_vh(list_2d):
    return cv2.vconcat([cv2.hconcat(list_h) 
                        for list_h in list_2d])
def concact_img():
    img0 = cv2.imread('./images/30mb.jpg')
    # img1 = cv2.imread('./images/1.jpg')
    # img_vconcat = cv2.vconcat([img0, img0])
    img_tile = concat_vh([[img0, img0, img0],
                      [img0, img0, img0]])
    # cv2.imwrite('./images/vconcat.jpg', img_vconcat)
    cv2.imwrite('./images/vhconcat.jpg', img_tile)
  
    # show the output image
    # cv2.imshow('./images/res.jpg', im_v)

def download_from_s3():
    # input_bucket = event['input_bucket']
    input_bucket = "lyuze"
    s3_client = boto3.client('s3')
    # img_size = payload['img_size']
    object_key = "img_proc/5mb.jpg"
    download_path = "./images/5mb_from_s3.jpg"
    # object_key = choose_img()
    s3_client.download_file(input_bucket, object_key, download_path)

def truncat_str():
    img_size = "1mb"
    object_key = "video_proc/" + img_size + ".mp4"
    file_name = object_key[object_key.find('/')+1:object_key.find('.')]
    print(file_name)
    
def main():
    
    truncat_str()
main()