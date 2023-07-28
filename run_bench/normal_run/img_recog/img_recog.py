
import datetime, json, os, uuid, glob, time

from PIL import Image
import torch
from torchvision import transforms
from torchvision.models import resnet50

# from . import storage
# client = storage.storage.get_instance()

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
class_idx = json.load(open(os.path.join(SCRIPT_DIR, "imagenet_class_index.json"), 'r'))
idx2label = [class_idx[str(k)][1] for k in range(len(class_idx))]
model = None
file_suffix = ".JPEG"
pattern = os.path.join(SCRIPT_DIR, "images", f"*{file_suffix}")
file_paths = glob.glob(pattern)

def main():
    # model_bucket = event.get('bucket').get('model')
    image_paths = []
    rets = []
    for file_path in file_paths:
        image_path = os.path.abspath(file_path)
        # print(image_path)
        image_paths.append(image_path)
    # print(len(image_paths))
    # time.sleep(10)
    model_path = os.path.join(SCRIPT_DIR, "resnet50-19c8e357.pth")
    # image_path = "/home/cc/img_recog/512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg"

    # input_bucket = event.get('bucket').get('input')
    # key = event.get('object').get('input')
    # model_key = event.get('object').get('model')
    # download_path = '/tmp/{}-{}'.format(key, uuid.uuid4())

    image_download_begin = datetime.datetime.now()
    # image_path = download_path
    # client.download(input_bucket, key, download_path)
    image_download_end = datetime.datetime.now()

    global model
    if not model:
        model_download_begin = datetime.datetime.now()
        # model_path = os.path.join('/tmp', model_key)
        # client.download(model_bucket, model_key, model_path)
        model_download_end = datetime.datetime.now()
        model_process_begin = datetime.datetime.now()
        model = resnet50(pretrained=False)
        model.load_state_dict(torch.load(model_path))
        model.eval()
        model_process_end = datetime.datetime.now()
    else:
        model_download_begin = datetime.datetime.now()
        model_download_end = model_download_begin
        model_process_begin = datetime.datetime.now()
        model_process_end = model_process_begin
   
    process_begin = datetime.datetime.now()
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    for index, image_path in enumerate(image_paths):
        try:
            # if index == 
            input_image = Image.open(image_path)
            input_tensor = preprocess(input_image)
            input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model 
            output = model(input_batch)
            _, index = torch.max(output, 1)
            # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
            # prob = torch.nn.functional.softmax(output[0], dim=0)
            # _, indices = torch.sort(output, descending = True)
            ret = idx2label[index]
            rets.append(ret)
        except Exception as e:
            # print(e, "for image", image_path)
            continue
    process_end = datetime.datetime.now()

    download_time = (image_download_end- image_download_begin) / datetime.timedelta(seconds=1)
    model_download_time = (model_download_end - model_download_begin) / datetime.timedelta(seconds=1)
    model_process_time = (model_process_end - model_process_begin) / datetime.timedelta(seconds=1)
    process_time = (process_end - process_begin) / datetime.timedelta(seconds=1)
    print({
            # 'result': {'idx': index.item(), 'class': ret},
            'measurement': {
                'download_time': download_time + model_download_time,
                'compute_time': process_time,
                'model_time': model_process_time,
                'model_download_time': model_download_time
            }
        })

main()