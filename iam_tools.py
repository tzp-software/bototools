
import boto

def create_new_key_pair(keyName,keyDir=None,keyExt=None):
    ec2 = boto.connect_ec2()
    key = ec2.create_key_pair(keyName)
    key.save(keyDir)

    return True


