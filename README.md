[![Coverage Status](https://coveralls.io/repos/github/lexieaytes/choc-o-lock/badge.svg?branch=master)](https://coveralls.io/github/lexieaytes/choc-o-lock?branch=master)

# Choc-O-Lock
*"Sweeten your security"*

### Senior Design 2020-21

To run the main Python application:

```
python main.py --resource-id=<resource id>
```

`<resource id>` should be the data center or server rack that this deployment protects.

The first time you run the Python application, it will attempt to provision all the AWS resources required:
- IAM role/policy
- Rekognition collection
- Kinesis Video Stream
- Kinesis Data Stream
- Rekognition stream processor

You can also manually run setup like so:

```
python setup.py
```

Running setup will create a file called `config.json` in the project directory. This file contains all the identifiers for the AWS resources. 

After you've run setup once, it will be skipped whenever you run the main application from then on.

To run the main application in DEBUG mode:

```
python main.py --resource-id=<resource id> --debug
```
