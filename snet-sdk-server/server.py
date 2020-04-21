import os
import sys

import shutil
import json
from pathlib import Path
import traceback

from flask import Flask, request

import ipfsapi
from snet import sdk
from snet.snet_cli.utils_ipfs import safe_extract_proto_from_ipfs

SDK_SERVER_DIR = Path(__file__).absolute().parent
sys.path.insert(0, "{}".format(SDK_SERVER_DIR))
from utils.proto_tools import load_proto, input_factory, output_factory


class SDKServer:
    def __init__(self,
                 host, port,
                 ssl_context,
                 eth_rpc_endpoint,
                 org_id, service_id, group_name,
                 private_key,
                 use_cors=False):

        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.eth_rpc_endpoint = eth_rpc_endpoint
        self.org_id = org_id
        self.service_id = service_id
        self.group_name = group_name
        self.private_key = private_key

        # Getting Service .proto file(s) from its Metadata
        _, _, services_dict, classes, stubs = load_proto(self.get_proto())
        self.services_dict = services_dict
        self.classes = classes
        self.stubs = stubs

        if use_cors:
            from flask_cors import CORS
            CORS(self.app)

    def get_proto(self):
        snet_sdk = sdk.SnetSDK(config={
            "private_key": self.private_key,
            "eth_rpc_endpoint": self.eth_rpc_endpoint})
        metadata = snet_sdk.get_service_metadata(self.org_id, self.service_id)
        ipfs_client = ipfsapi.connect("http://ipfs.singularitynet.io", 80)
        proto_dir = "{}/protos".format(SDK_SERVER_DIR)
        if os.path.exists(proto_dir):
            shutil.rmtree(proto_dir)
        safe_extract_proto_from_ipfs(ipfs_client,
                                     metadata["model_ipfs_hash"],
                                     proto_dir)
        return proto_dir

    def serve(self):
        @self.app.route("/", methods=["GET", "POST"])
        @self.app.route("/<path:path>", methods=["GET", "POST"])
        def rest_to_grpc(path=None):
            if request.method in ["GET", "POST"]:
                try:
                    req = None
                    if request.method == "GET":
                        if not request.args:
                            ret = dict()
                            for s in self.services_dict.keys():
                                ret[s] = list(self.services_dict[s].keys())
                            return ret, 200
                        else:
                            req = request.args.to_dict()

                    if not path:
                        return self.services_dict, 500

                    path_list = path.split("/")
                    if not path_list or path_list[0].upper() == "HELP":
                        return self.services_dict, 500

                    service = path_list[0]
                    if service not in self.services_dict:
                        return {"Error": "Invalid gRPC service.", **self.services_dict}, 500

                    if not req:
                        if request.data:
                            req = json.loads(request.data.decode("utf-8"))
                        else:
                            req = request.json if request.json else request.form.to_dict()

                    if len(path_list) > 1:
                        method = path_list[1]
                    else:
                        method = req.get("method", list(self.services_dict[service].keys())[0])

                    if method not in self.services_dict[service].keys():
                        return {"Error": "Invalid gRPC method.", **self.services_dict[service]}, 500

                    # Free calls: Removing its fields from the Request to route only the gPRC ones.
                    token = req.get("token", "")
                    expiration = int(req.get("expiration", "0"))
                    email = req.get("email", "")
                    if all(p in req.keys() for p in ["token", "expiration", "email"]):
                        del req["token"]
                        del req["expiration"]
                        del req["email"]
                    else:
                        return {"Error": "token, expiration and email fields are required!"}, 500

                    input_message = self.services_dict[service][method]["input"]
                    input_dict = input_factory(req, input_message, self.classes)

                    grpc_input = self.classes[input_message["name"]](**input_dict)

                    config = {
                        "eth_rpc_endpoint": self.eth_rpc_endpoint,
                        "private_key": self.private_key,
                        "free_call_auth_token-bin": token,
                        "free-call-token-expiry-block": expiration,
                        "email": email
                    }

                    snet_sdk = sdk.SnetSDK(config)
                    client = snet_sdk.create_service_client(self.org_id,
                                                            self.service_id,
                                                            self.stubs[service],
                                                            group_name=self.group_name)
                    method_stub = getattr(client.service, method, None)
                    response = method_stub(grpc_input)
                    output_message = self.services_dict[service][method]["output"]
                    output_dict = output_factory(response, output_message)
                    return output_dict, 200

                except Exception as e:
                    print("{}\n{}".format(e, traceback.print_exc()))
                    return {"Error": "Invalid gRPC request.", **self.services_dict}, 500

            return {"Error": "Invalid HTTP request (use POST)."}, 500

        self.app.run(debug=False,
                     host=self.host,
                     port=self.port,
                     ssl_context=self.ssl_context,
                     use_reloader=False,
                     threaded=True,
                     passthrough_errors=True)
