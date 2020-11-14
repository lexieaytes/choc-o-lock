# Choc-O-Lock
*"Sweeten up your security"*

### Senior Design 2020-21

You must tell the main script what resource it protects and the name of the AWS Kinesis Video Stream it should connect to. You do this through enviroment variables. 

For example, run the following on the command line to launch the script, substituting the correct values for `resource_id` and `stream_name`. The `resource_id` should come from the MySQL database, while the `stream_name` is whatever you titled the Kinesis Video Stream when you created it.

```
CHOC_O_LOCK_RESOURCE_ID=<resource_id> AWS_VIDEO_STREAM_NAME=<stream_name> python main.py
````

