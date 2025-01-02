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

import datetime

from config.default import Default
from models.set_up import ModelSetup, PersistenceSetup


# Initialize configuration
client, model_id = ModelSetup.init()
MODEL_ID = model_id
config = Default()

db = PersistenceSetup.init()


def add_image_metadata(gcsuri: str, prompt: str, model: str):
    """ Add Image metadata to Firestore persistence """

    current_datetime = datetime.datetime.now()

    # Store the image metadata in Firestore
    doc_ref = db.collection(config.IMAGE_COLLECTION_NAME).document()
    doc_ref.set({
        "gcsuri": gcsuri,
        "prompt": prompt,
        "model": model,
        "timestamp": current_datetime, # alt: firestore.SERVER_TIMESTAMP
    })
    
    print(f"Image data stored in Firestore with document ID: {doc_ref.id}")
