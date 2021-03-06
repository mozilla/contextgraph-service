import boto3
import botocore

from miracle.config import (
    S3_BUCKET,
    S3_ENDPOINT,
)


def create_bucket(s3_bucket=S3_BUCKET, _bucket=None):
    if _bucket is not None:
        return _bucket

    return Bucket(s3_bucket)


class Bucket(object):

    _bucket = None
    _resource = None

    def __init__(self, name):
        self.name = name
        self._resource = s3 = boto3.resource('s3', endpoint_url=S3_ENDPOINT)
        self._bucket = s3.Bucket(name)

    def clear(self):
        if self._bucket:
            try:
                # This deletes up to 1000 objects, which should be plenty
                # for test cleanup.
                self._bucket.objects.delete()
                self._bucket.delete()
                self._bucket.wait_until_not_exists()
            except botocore.exceptions.ClientError:  # pragma: no cover
                # likely NoSuchBucket
                pass
        if self._resource:
            self._bucket = self._resource.Bucket(self.name)
            self._bucket.create()
            self._bucket.wait_until_exists()

    def close(self):
        self._bucket = None
        try:
            self._resource.meta.client._endpoint.http_session.close()
        except AttributeError:  # pragma: no cover
            pass
        self._resource = None

    def ping(self, raven):
        try:
            self._resource.meta.client.head_bucket(Bucket=self.name)
        except botocore.exceptions.ClientError:  # pragma: no cover
            raven.captureException()
            return False
        return True

    def delete(self, key, **kw):
        obj = self._bucket.Object(key)
        return obj.delete(**kw)

    def filter(self, **kw):
        return self._bucket.objects.filter(**kw)

    def get(self, key, **kw):
        obj = self._bucket.Object(key)
        return obj.get(**kw)

    def put(self, key, body, **kw):
        obj = self._bucket.Object(key)
        return obj.put(Body=body, **kw)
