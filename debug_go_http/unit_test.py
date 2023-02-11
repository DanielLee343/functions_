# import boto3
import numpy

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# import joblib
# import json

# import pandas as pd
from time import time, sleep
# import re
# import io

# tmp = '/tmp/'
# cleanup_re = re.compile('[^a-z]+')

# def cleanup(sentence):
#     sentence = sentence.lower()
#     sentence = cleanup_re.sub(' ', sentence).strip()
#     return sentence

# def model_training():
#     # payload = json.loads(req)
#     # f_access_id = open("/var/openfaas/secrets/access-id", "r")
#     # access_id = f_access_id.read()
#     # f_access_id.close()
#     # f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
#     # secret_key = f_secret_key.read()
#     # f_secret_key.close()
#     access_id = "AKIAYFDPR5IUQLLZATEJ"
#     secret_key = "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"

#     dataset_bucket = 'lyuze'
#     model_bucket = 'lyuze'
#     # if 'ds_size' in payload:
#         # ds_size = payload['ds_size']
#         # dataset_object_key = "model_training/reviews"+ds_size+".csv"
#     # else:
#     dataset_object_key = "model_training/reviews50mb.csv"
    
#     # if 'model' in payload:
#     #     model = payload['model']
#     #     model_object_key = "model_training/"+model
#     # else:
#     model_object_key = "model_training/lr_model.pk"

#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=access_id,
#         aws_secret_access_key=secret_key
#     )

#     obj = s3_client.get_object(Bucket=dataset_bucket, Key=dataset_object_key)
#     df = pd.read_csv(io.BytesIO(obj['Body'].read()))

#     start = time()
#     df['train'] = df['Text'].apply(cleanup)
#     tfidf_vector = TfidfVectorizer(min_df=100).fit(df['train'])
#     train = tfidf_vector.transform(df['train'])
#     model = LogisticRegression(max_iter=10000)
#     model.fit(train, df['Score'])
#     latency = time() - start
#     # model_file_path = tmp + model_object_key
#     model_file_path = "./lr_model.pk"
#     joblib.dump(model, model_file_path)
#     s3_client.upload_file(model_file_path, model_bucket, model_object_key)

#     print(latency)
#     # return latency

# def read_s3_to_pd():
#     dataset_path = 's3://lyuze/model_training/reviews10mb.csv'
#     dataset = pd.read_csv(dataset_path)

def see_so():
    
def main():
    see_so()
main()