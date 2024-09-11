from botocore.session import get_session


class S3Client:

    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str
    ):
        self.__config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'endpoint_url': endpoint_url,
        }
        self._bucket_name = bucket_name
        self.session = get_session()
        self.client = self.session.create_client("s3", **self.__config, verify=False)

    def upload_file(self, path):
        filename = path.split('/')[-1]
        with open(path, "rb") as file:
            self.client.put_object(
                Bucket=self._bucket_name,
                Key=filename,
                Body=file,
            )