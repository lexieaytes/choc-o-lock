[![Coverage Status](https://coveralls.io/repos/github/lexieaytes/choc-o-lock/badge.svg?branch=master)](https://coveralls.io/github/lexieaytes/choc-o-lock?branch=master)

# Choc-O-Lock
*"Sweeten your security"*

### Senior Design 2020-21

To run the main Python application:

```
python main.py --resource-id=<resource id> --aws-stream=<kinesis stream name> 
```

Or to run it in DEBUG mode:

```
python main.py --resource-id=<resource id> --aws-stream=<kinesis stream name> --debug
```

`resource id` should identify the data center or server rack that this instance of the system is meant to protect. 

`kinesis stream name` should be the name of the Kinesis Data Stream to which AWS Rekognition writes its processed results.
