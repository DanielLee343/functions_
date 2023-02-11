import boto3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import json

import pandas as pd
from time import time
import re
import io

tmp = '/tmp/'
cleanup_re = re.compile('[^a-z]+')

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

    dataset_bucket = 'lyuze'
    model_bucket = 'lyuze'
    if 'ds_size' in payload:
        ds_size = payload['ds_size']
        dataset_object_key = "model_training/reviews"+ds_size+".csv"
    else:
        dataset_object_key = "model_training/reviews10mb.csv"
    
    if 'model' in payload:
        model = payload['model']
        model_object_key = "model_training/"+model
    else:
        model_object_key = "model_training/lr_model.pk"

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_key
    )

    obj = s3_client.get_object(Bucket=dataset_bucket, Key=dataset_object_key)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))

    start = time()
    df['train'] = df['Text'].apply(cleanup)
    tfidf_vector = TfidfVectorizer(min_df=100).fit(df['train'])
    train = tfidf_vector.transform(df['train'])
    model = LogisticRegression(max_iter=10000)
    model.fit(train, df['Score'])
    latency = time() - start
    # model_file_path = tmp + model_object_key
    # joblib.dump(model, model_file_path)
    # s3_client.upload_file(model_file_path, model_bucket, model_object_key)

    print(latency)
    return latency