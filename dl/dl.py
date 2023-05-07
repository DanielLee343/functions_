import argparse
import subprocess
import sys, time, os
import json
from pathlib import Path
import learning

initTime = time.time()
CUR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
def main():
    # Read commands parsed by users
    parser = argparse.ArgumentParser(
        prog='canary', description='All in One action deep learning')
    parser.add_argument('-job', type=str,
                        help='Target job for testing (dl, mining, query)')
    parser.add_argument('-m', '--model', type=str,
                        help='Target model for training job. \nDefault is ResNet50.')
    parser.add_argument('-d', '--dataset', type=str,
                        help='Target dataset. \nDefault is CIFAR10.')
    parser.add_argument('-b', '--batch', type=int,
                        help='Size of data batch. \nDefault is 64.')
    parser.add_argument('-e', '--epoch', type=int,
                        help='Number of epochs. \nDefault is 100.')
    parser.add_argument('-t', '--type', type=str,
                        help='Batch or standalone computation (use std or batch). \nDefault is std')
    parser.add_argument('-hm', '--heatmap', action='store_true',
                        help='Whether to run damo to generate heatmap. \nDefault is false')
    parser.add_argument('-vtune', action='store_true',
                        help='Whether to run vtune profiler. \nDefault is false')

    print("MAKESPAN ::> Job Launched -> Time = {0}.s".format(0))
    compile(parser)


def compile(parser):
    params = vars(parser.parse_args())
    workload = params['job']
    if workload == "dl":
        buildDL(params)
    # elif workload == "mining":
    #     buildMining(params)
    # elif workload == "query":
    #     buildQuery(params)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)


def buildDL(params):
    # image = "hpdsl/canary:dltrain"
    model = "vgg16" if params['model'] is None else params['model']
    dataset = "cifar10" if params['dataset'] is None else params['dataset']
    # params['file'] = "{0}/{1}/{2}.json".format(CUR_DIR, data, model)
    # print(params['file'])

    # get data and model info from file
    # with open(params['file']) as file:
    #     file_content = json.load(file)
    # print(file_content)

    # # Get datasets parameters
    # data_features = file_content['dataset']
    # params['features'] = data_features
    # size_attributes = data_features['size'].split(" ")
    # size_value = int(float(size_attributes[0]))
    # dataset = data_features['name']
    batch_size = 128 if params['batch'] is None else params['batch']
    epochs = 5 if params['epoch'] is None else params['epoch']
    # params['model'] = file_content['model']['name']
    params['model'] = model
    params['dataset'] = dataset
    params['batch'] = batch_size
    params['epochs'] = epochs
    # metadata = json.dumps({"model": file_content['model']['name'], "dataset": dataset,
    #                        "batch": batch_size, "epochs": epochs, "features": params["features"]})
    
    # print(metadata)
    # learning.run_train(params)
    learning.run_transfer(params)

    # # Create package
    # package_code = "wsk -i package update deep --param meta '{0}'".format(metadata)
    # post(package_code)

    # if params['type'] == 'batch':
    #     sys.exit(0)
    # else:
    #     # Create action
    #     action_code = "wsk -i action update deep/learning $HOME/canary/dltraining/learning.py --docker {img} --memory 12228 --timeout 540000".format(img=image)
    #     post(action_code)

    #     # Invoke action
    #     answer = post("wsk -i action invoke deep/learning")
    #     print("MAKESPAN ::> Container Launched -> Time = {0}.s".format(time.time()-initTime))
    #     activation = answer.split(" ")[-1]
    #     print("Retrieve results with activation code {act}".format(act=activation))



def buildMining(params):

    image = "hpdsl/canary:sparkdiversity"

    # Create action
    action_code = "wsk -i action update divindex $HOME/canary/datamining/divindex.py --docker {img} --memory 1024 --timeout 540000".format(img=image)
    post(action_code)

    # Invoke action
    answer = post("wsk -i action invoke divindex")
    print("MAKESPAN ::> Container Launched -> Time = {0}.s".format(time.time()-initTime))
    activation = answer.split(" ")[-1]
    print("Retrieve results with activation code {act}".format(act=activation))


def buildQuery(params):

    image = "hpdsl/canary:dbquery"

    # Prepare database
    post("docker cp $HOME/canary/dbquery/prepare.py canary-db:/tmp/canary")
    post("docker cp $HOME/canary/dbquery/setupdb.sh canary-db:/tmp/canary")
    post("docker exec canary-db python /tmp/canary/setupdb.sh")
    post("docker exec canary-db python /tmp/canary/prepare.py")

    # Create action
    action_code = "wsk -i action update dbquery $HOME/canary/dbquery/dbquery.py --docker {img} --memory 512 --timeout 540000".format(img=image)
    post(action_code)

    # Invoke action
    answer = post("wsk -i action invoke dbquery")
    print("MAKESPAN ::> Container Launched -> Time = {0}.s".format(time.time()-initTime))
    activation = answer.split(" ")[-1]
    print("Retrieve results with activation code {act}".format(act=activation))


def post(command):
    print('Running ({0})....'.format(command))
    reply = subprocess.run(['/bin/bash', '-c', command], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT).stdout.decode().strip()
    if "error" in reply:
        pass
    else:
        print('Result:', reply)
    return reply


if __name__ == '__main__':
    main()