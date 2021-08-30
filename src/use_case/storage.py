from os import environ
from typing import Union
from uuid import UUID

from google.cloud import storage

from src.services import FileAPI


class UploadBucketFile:

    @classmethod
    def handle(cls, simulation_uuid: Union[UUID, str], file_id: UUID) -> bool:
        bucket_name = environ.get("GCP_BUCKET_NAME")
        blob_name = "/".join([str(simulation_uuid), "in", str(file_id)])

        response, is_invalid = FileAPI.find_file(
            simulation_uuid,
            file_id
        )
        if is_invalid:
            return True
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        try:
            blob.upload_from_string(
                response.text,
                content_type="text/plain",
                num_retries=3
            )
        except Exception:
            raise RuntimeError("Cant execute files")
        return False
