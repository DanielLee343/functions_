import boto3
import json
from torchvision import models, transforms
import torch.nn as nn
import torch
from PIL import Image
from torch.nn import functional as F
import zipfile
from time import time
import shutil
import os

def pil_loader(path):
    with open(path, 'rb') as f:
        img = Image.open(f)
        return img.convert('RGB')

def setup_and_do_serving():
    validation_img_paths = []
    input_path = "./resnet50_dataset/alien_vs_predator_thumbnails/data/"
    for i in range(100):
        validation_img_paths.append("validation/alien/" + str(i) + ".jpg")
        validation_img_paths.append("validation/predator/" + str(i) + ".jpg")
    # print(validation_img_paths)
    img_list = [pil_loader(input_path + img_path) for img_path in validation_img_paths]

    device = torch.device("cpu")
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                    std=[0.229, 0.224, 0.225])
    data_transforms = {
        'train':
        transforms.Compose([
            transforms.Resize((224,224)),
            transforms.RandomAffine(0, shear=10, scale=(0.8,1.2)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize
        ]),
        'validation':
        transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            normalize
        ]),
    }

    model = models.resnet50(pretrained=False).to(device)
    model.fc = nn.Sequential(
                nn.Linear(2048, 128),
                nn.ReLU(inplace=True),
                nn.Linear(128, 2)).to(device)
    model.load_state_dict(torch.load('./resnet50_weights.h5'))

    start = time()
    validation_batch = torch.stack([data_transforms['validation'](img).to(device)
                                    for img in img_list])
    pred_logits_tensor = model(validation_batch)
    # print(pred_logits_tensor)
    pred_probs = F.softmax(pred_logits_tensor, dim=1).cpu().data.numpy()
    latency = time() - start
    print(latency)
    return latency 

def handle(req):
    # payload = json.loads(req)
    f_access_id = open("/var/openfaas/secrets/access-id", "r")
    access_id = f_access_id.read()
    f_access_id.close()
    f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
    secret_key = f_secret_key.read()
    f_secret_key.close()

    dataset_bucket = 'lyuze'
    dataset_object_key = "dl_workload/resnet50_dataset.zip"
    weight_object_key = "dl_workload/resnet50_weights.h5"
    # if 'e' in payload:
    #     epoch = int(payload['e'])
    # else:
    #     epoch = 3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_key
    )
    s3_client.download_file(dataset_bucket, dataset_object_key, './resnet50_dataset.zip')
    with zipfile.ZipFile('./resnet50_dataset.zip', 'r') as zip_ref:
        zip_ref.extractall('./')
    s3_client.download_file(dataset_bucket, weight_object_key, './resnet50_weights.h5')

    latency = setup_and_do_serving()
    os.remove('./resnet50_dataset.zip')
    os.remove('./resnet50_weights.h5')
    shutil.rmtree('./resnet50_dataset')
    return latency
