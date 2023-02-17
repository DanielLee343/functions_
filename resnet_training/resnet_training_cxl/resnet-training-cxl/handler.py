import boto3
import json
# import numpy as np
# from PIL import Image
import torch
from torchvision import datasets, models, transforms
import torch.nn as nn
from torch.nn import functional as F
import torch.optim as optim
import zipfile
from time import time
import os
import shutil

def train_model(model, criterion, optimizer, image_datasets, dataloaders, device, num_epochs=3):
    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch+1, num_epochs))
        print('-' * 10)

        for phase in ['train', 'validation']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                if phase == 'train':
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                _, preds = torch.max(outputs, 1)
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(image_datasets[phase])
            epoch_acc = running_corrects.double() / len(image_datasets[phase])

            print('{} loss: {:.4f}, acc: {:.4f}'.format(phase,
                                                        epoch_loss,
                                                        epoch_acc))
    return model

def setup_and_do_resnet(batch_size=32):
    input_path = "./resnet50_dataset/alien_vs_predator_thumbnails/data/"
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

    image_datasets = {
        'train': 
        datasets.ImageFolder(input_path + 'train', data_transforms['train']),
        'validation': 
        datasets.ImageFolder(input_path + 'validation', data_transforms['validation'])
    }

    dataloaders = {
        'train':
        torch.utils.data.DataLoader(image_datasets['train'],
                                    batch_size=batch_size,
                                    shuffle=True,
                                    num_workers=0),  # for Kaggle
        'validation':
        torch.utils.data.DataLoader(image_datasets['validation'],
                                    batch_size=batch_size,
                                    shuffle=False,
                                    num_workers=0)  # for Kaggle
    }
    device = torch.device("cpu")
    # print(device)

    model = models.resnet50(pretrained=True).to(device)
        
    for param in model.parameters():
        param.requires_grad = False   
        
    model.fc = nn.Sequential(
                nn.Linear(2048, 128),
                nn.ReLU(inplace=True),
                nn.Linear(128, 2)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters())

    start = time()
    model_trained = train_model(model, criterion, optimizer, image_datasets, dataloaders, device, num_epochs=3)
    latency = time() - start
    print(latency)
    return latency

def handle(req):
    payload = json.loads(req)
    f_access_id = open("/var/openfaas/secrets/access-id", "r")
    access_id = f_access_id.read()
    f_access_id.close()
    f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
    secret_key = f_secret_key.read()
    f_secret_key.close()

    dataset_bucket = 'lyuze'
    dataset_object_key = "dl_workload/resnet50_dataset.zip"
    if 'bs' in payload:
        batch_size = int(payload['bs'])
    else:
        batch_size = 32
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_key
    )

    #download dataset from s3 and unzip
    s3_client.download_file(dataset_bucket, dataset_object_key, './resnet50_dataset.zip')
    with zipfile.ZipFile('./resnet50_dataset.zip', 'r') as zip_ref:
        zip_ref.extractall('./')
    
    latency = setup_and_do_resnet(batch_size)
    os.remove('./resnet50_dataset.zip')
    shutil.rmtree('./resnet50_dataset')
    return latency