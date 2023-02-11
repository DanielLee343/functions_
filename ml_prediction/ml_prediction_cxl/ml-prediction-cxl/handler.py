import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import pandas as pd
import json
from time import time
import os
import re
import io

tmp = '/tmp/'
cleanup_re = re.compile('[^a-z]+')

# has bug!!

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def handle(req):
    payload = json.loads(req)
    f_access_id = open("/var/openfaas/secrets/access-id", "r")
    access_id = f_access_id.read()
    f_access_id.close()
    f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
    secret_key = f_secret_key.read()
    f_secret_key.close()

    x = payload['x']
    ds_size = payload['ds_size']
    dataset_bucket = 'lyuze'
    dataset_object_key = "model_training/reviews"+ds_size+".csv"
    model_bucket = 'lyuze'
    if 'model' in payload:
        model_object_key = "model_training/" + payload['model'] + ".pk"
    else:
        model_object_key = "model_training/lr_model.pk"
    

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_key
    )
    
    model_path = tmp + 'lr_model.pk'
    if not os.path.isfile(model_path):
        s3_client.download_file(model_bucket, model_object_key, model_path)

    obj = s3_client.get_object(Bucket=dataset_bucket, Key=dataset_object_key)
    dataset = pd.read_csv(io.BytesIO(obj['Body'].read()))

    start = time()

    df_input = pd.DataFrame()
    df_input['x'] = [x] # text to test
    df_input['x'] = df_input['x'].apply(cleanup)

    dataset['train'] = dataset['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(dataset['train'])

    X = tfidf_vect.transform(df_input['x'])

    model = joblib.load(model_path)
    y = model.predict(X)

    latency = time() - start
    print(latency)
    return {'y': y, 'latency': latency}