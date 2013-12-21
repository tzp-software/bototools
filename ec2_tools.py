import os
import time
import boto
import boto.manage.cmdshell


def request_and_allocate_elastic_ip(instance):
    ec2 = boto.connect_ec2()
    addr = ec2.allocate_address()
    ec2.associate_address(instance.id,addr.public_ip)


def launch_instance(ami='ami-c17b27a8', instance_type='t1.micro',
                    key_name='key3',key_extension='.pem',
                    key_dir='~/.ssh', group_name='tzp',
                    ssh_port=22, cidr='0.0.0.0/0', tag='tzp-server',
                    user_data=None, cmd_shell=True, login_user='ubuntu',
                    ssh_passwd=None):
    '''
        launchs new ec2 instance with given parameters

        ami - ami to launch in ec2
            default is an ubuntu alestic

        instance_type - size/compute power of instance
            default is 't1.micro' <free>
    
        key_name, key_extension, key_dir ssh key stuff
        def key1   def  .pem      def ~/.ssh

        group_name, ssh_port, cidr, more ssh connection stuff
            tzp         22    0.0.0.0/0

        tag, user_data - user defined stuff
        tzp, no def

        cmd_shell - should you ssh?

        login_user - default login

        ssh_passwd - not needed!
    '''
    cmd = None
    ec2 = boto.connect_ec2()
    try:
        key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    except ec2.ResponseError, e:
        if e.code == "InvalidKeyPair.NotFound":
            print 'Creating key pair %s' % key_name
            key = ec2.create_key_pair(key_name)
            key.save(key_dir)
        else:
            raise

    try:
        group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
        if e.code == "InvalidGroup.NotFound":
            print 'Creating security group %s' % group_name
            group = ec2.create_security_group(group_name,'a ssh enabled group')
        else:
            raise

    try:
        group.authorize('tcp',ssh_port,ssh_port,cidr)
    except ec2.ResponseError, e:
        if e.code == "InvalidPermission.Duplicate":
            print 'security group %s was already authorized for ssh' % group_name
        else:
            raise
    
    reservation = ec2.run_instances(ami,key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data,)
    instance = reservation.instances[0]
    print 'waiting for instance %s to launch' % tag
    while instance.state != 'running':
        print '.',
        time.sleep(5)
        instance.update()
    print 'done loading...'
    instance.add_tag(tag)
    
    if cmd_shell:
        key_path = os.path.join(os.path.expanduser(key_dir),key_name+key_extension)
        cmd = boto.manage.cmdshell.sshclient_from_instance(instance,key_path,user_name=login_user)
        return (instance,cmd)


def main():
    i,c = launch_instance()
    c.shell()
    i.terminate()
    while i.state == 'running':
        print 'still running'
        i.update()
    print 'down'

if __name__ == "__main__":
    main()
