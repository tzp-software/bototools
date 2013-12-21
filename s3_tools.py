# coding: utf-8
import os
import time
import boto
import random

b = [random.randrange(9) for x in range(4)]

def upload_website(bucket_name,sitedir,indexfile='index.html',errorfile=None):
    s3 = boto.connect_s3()
    bucket = s3.lookup(bucket_name)
    if not bucket:
        bucket = create_bucket(bucket_name)
    bucket.set_canned_acl('public-read')
    for root, dirs, files in os.walk(sitedir):
        for file in files:
            fullpath = os.path.join(root,file)
            relpath = os.path.relpath(fullpath,sitedir)
            print "uploading %s as %s" % (fullpath,relpath)
            key = bucket.new_key(relpath)
            key.content_type = 'text/html'
            key.set_contents_from_filename(fullpath,policy='public-read')

    bucket.configure_website(indexfile,errorfile)
    time.sleep(3)
    print "You can access the website at: ",
    print bucket.get_website_endpoint()
    
def create_bucket(name):
    s3 = boto.connect_s3()
    bucket = s3.lookup(name)
    if bucket:
        print 'bucket (%s) already exists' % name
    else:
        try:
            bucket = s3.create_bucket(name)
        except s3.provider.storage_create_error, e:
            print 'Bucket (%s) is owned by another user!' % name
    return bucket

if __name__ == "__main__":
    import sys
    upload_website('tzp-'+str(b),sys.argv[1])
