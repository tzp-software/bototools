import boto
import time

def create_ebs_volume(instance,size,devName):
    '''
        generates an elastic block storage volume
        then attaches it to the given ec2 instance
    '''
    ec2 = instance.connection
    azone = instance.placement
    volume = ec2.create_volume(size,azone)
    
    # wait till its ready
    while volume.status != 'avaliable':
        time.sleep(5)
        volume.update()
    volume.attach(instance.id,devName)
        
