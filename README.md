# snet-sdk-server
Simple REST API to expose snet-sdk to external apps.

First clone this repo:
```shell script
git clone https://github.com/arturgontijo/snet-sdk-server.git
cd snet-sdk-server
```

Installing the dependencies:
```shell script
pip3 install -r requirements.txt
```

Starting the server:
```shell script
python3 snet-sdk-server --org snet --service cntk-image-recon --pk __PRIVATE_KEY_WITH_0x__ --host 0.0.0.0 --port 7000 --cors
```

This command will auto fetch the `.proto` file(s) from the SingularityNET IPFS endpoint and compile them.

To call the service, first:
- Go the `cntk-image-recon` page on the [SingularityNET dApp](https://beta.singularitynet.io/servicedetails/org/snet/service/cntk-image-recon).
- Got to the "Install and Run" tab.
- Put your Public Account in the text field input (the pubbey derived from the `__PRIVATE_KEY_WITH_0x__` above).
- Get the necessary fields from the generated `authToken.txt` file and use them on the command below:
  - "email" -> "email"
  - "tokenToMakeFreeCall" -> "token"
  - "tokenExpirationBlock" -> "expiration"
```shell script
curl -XPOST -H "Content-Type: application/json" -d '{"model": "ResNet152", "img_path": "https://raw.githubusercontent.com/singnet/dnn-model-services/master/docs/assets/users_guide/rose.jpg", "email": "__SNET_DAPP_EMAIL__", "token": "__SNET_DAPP_TOKEN__", "expiration": __SNET_DAPP_EXPIRATION__}' localhost:7000/Recognizer/flowers
```

The server will route your HTTP request to the `cntk-image-recon` Daemon and return an HTTP response:
```shell script
{"delta_time":"2.0213","top_5":"{1: '99.47%: rose', 2: '00.20%: mallow', 3: '00.07%: globe-flower', 4: '00.04%: bougainvillea', 5: '00.03%: anthurium'}"}
```


