import nats
import os
import sys
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def test_nats(event):
    subject = "nats-test"
    req_body = event.body
    req_headers = event.headers
    req_method = event.method
    req_query = event.query
    req_path = event.path
    eprint("req_body: ", req_body)
    eprint("req_headers: ", req_headers)
    eprint("req_method: ", req_method)
    eprint("req_query: ", req_query)
    eprint("req_path: ", req_path)

    # nats_url = os.getenv('nats_url')
    nats_url = os.environ.get('nats_url')
    eprint("nats_url: ", nats_url)

    nc = nats.connect(nats_url)
    eprint("publishing " + str(len(req_body))+ " bytes to " + subject)

    sub = nc.subscribe(subject)
    nc.publish(subject, req_body)

def handle(event, context):
    test_nats(event)
    return {
        "statusCode": 200,
        "body": "Hello from OpenFaaS!"
    }
