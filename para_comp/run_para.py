import random
import time
import threading
import json
import argparse
import requests
import ast

def main():
    msg = "Run multiple functions in parallel, doing math composition"
    parser = argparse.ArgumentParser(description = msg)
    parser.add_argument('-n', help='number for calculation (integer)')
    parser.add_argument('-p', help='number of functions (containers) to run in parallel (12)')
    parser.add_argument('-e', help='env: <base/cxl>')
    args = parser.parse_args()
    times = int(args.n)
    parallelIndex = int(args.p)
    env = (args.e)

    startTime = GetTime()
    temp = alu(times, parallelIndex, env)
    tot_exec = 0
    tempdict = eval(temp)
    for execTime in tempdict:
        # print(execTime)
        tot_exec += int(execTime)
    avg_exec = tot_exec / parallelIndex
    res_dict = {
        'result': temp,
        'avg_exec':avg_exec,
        'times': times,
        'execTime': GetTime() - startTime
    }
    print(res_dict)
        

def GetTime():
    return int(round(time.time() * 1000))

def alu(times, parallelIndex, env):
    payload = bytes("{\"n\": %d}" %(times / parallelIndex), encoding="utf8")
    
    resultTexts = []
    threads = []
    for i in range(parallelIndex):
        t = threading.Thread(target=singleAlu, args=(payload, resultTexts, i, env))
        threads.append(t)
        resultTexts.append('')
    for i in range(parallelIndex):
        threads[i].start()
    for i in range(parallelIndex):
        threads[i].join()

    return str(resultTexts)

def singleAlu(payload, resultTexts, clientId, env):
    clientStartTime = GetTime()
    response = single_invoke(payload, env)
    clientEndTime = GetTime()
    clientExecTime = clientEndTime - clientStartTime
    singleAluTimeinfo = "client %d startTime: %s, retTime: %s, execTime %s" %(clientId, clientStartTime, clientEndTime, clientExecTime)
    resultTexts[clientId] = str(response['execTime'])
    print("client %d finished" %clientId)

def single_invoke(payload, env):
    url = "http://127.0.0.1:8080/function/seq-" + env
    print("payload is:", payload)
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, payload, headers=headers)
    response_json = ast.literal_eval(response.text)
    return response_json
    

main()



