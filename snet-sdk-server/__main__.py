import os
import argparse

from server import SDKServer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # SNET SDK
    parser.add_argument("--rpc",
                        type=str,
                        default=os.environ.get(
                            "SDK_SERVER_RPC",
                            "https://mainnet.infura.io/v3/09027f4a13e841d48dbfefc67e7685d5"),
                        help="Ethereum RPC Endpoint.")
    parser.add_argument("--org",
                        type=str,
                        default=os.environ.get("SDK_SERVER_ORG", "snet"),
                        help="Organization ID.")
    parser.add_argument("--service",
                        type=str,
                        default=os.environ.get("SDK_SERVER_SERVICE", "example-service"),
                        help="Service ID.")
    parser.add_argument("--group",
                        type=str,
                        default=os.environ.get("SDK_SERVER_GROUP", "default_group"),
                        help="Group Name.")
    parser.add_argument("--pk",
                        type=str,
                        default=os.environ.get("SDK_SERVER_PK", ""),
                        help="Private key caller Account, used at token generation.")
    # REST API
    parser.add_argument("--host",
                        type=str,
                        default=os.environ.get("SDK_SERVER_HOST", "localhost"),
                        help="Transcoder server host.")
    parser.add_argument("--port",
                        type=int,
                        default=os.environ.get("SDK_SERVER_PORT", 7000),
                        help="Transcoder server port.")
    parser.add_argument("--cors",
                        action='store_true',
                        default=os.environ.get("SDK_SERVER_CORS", False),
                        help="Allow CORS (all domains!).")
    parser.add_argument("--cert",
                        type=str,
                        default=os.environ.get("SDK_SERVER_CERT", ""),
                        help="Path to certificate file.")
    parser.add_argument("--certkey",
                        type=str,
                        default=os.environ.get("SDK_SERVER_CERTKEY", ""),
                        help="Path to cert key.")
    args = parser.parse_args()

    ssl_context = None
    if os.path.exists(args.cert) and os.path.exists(args.certkey):
        ssl_context = (args.cert, args.certkey)

    rest_server = SDKServer(host=args.host,
                            port=args.port,
                            ssl_context=ssl_context,
                            eth_rpc_endpoint=args.rpc,
                            org_id=args.org,
                            service_id=args.service,
                            group_name=args.group,
                            private_key=args.pk,
                            use_cors=args.cors)

    print("\n================== Configurations ==================")
    for k, v in vars(args).items():
        if k == "pk":
            v = "********"
        tabs = "\t"
        if len(k) < 8:
            tabs = "\t\t"
        print("{}{}{}".format(k, tabs, v))
    print("====================================================\n")
    
    rest_server.serve()
