# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64

from google.cloud import aiplatform
from google.cloud import storage
import vertexai

from config.default import Default


# Initialize Configuration
cfg = Default()
vertexai.init(project=cfg.PROJECT_ID, location=cfg.LOCATION)
aiplatform.init(project=cfg.PROJECT_ID, location=cfg.LOCATION)


def store_to_gcs(
    folder: str, file_name: str, mime_type: str, contents: str, decode: bool = False
):
    """store contents to GCS"""
    client = storage.Client(project=cfg.PROJECT_ID)
    bucket = client.get_bucket(cfg.GENMEDIA_BUCKET)
    destination_blob_name = f"{folder}/{file_name}"
    blob = bucket.blob(destination_blob_name)
    if decode:
        contents_bytes = base64.b64decode(contents)
        blob.upload_from_string(contents_bytes, content_type=mime_type)
    else:
        blob.upload_from_string(contents, content_type=mime_type)
    return f"{cfg.GENMEDIA_BUCKET}/{destination_blob_name}"
