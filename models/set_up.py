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

from typing import Optional
from dotenv import load_dotenv
from google import genai

from config.firebase_app import initialize_firebase
#import firebase_admin
#from firebase_admin import credentials, firestore

from config.default import Default


load_dotenv(override=True)


class ModelSetup:
    """model set up class"""

    @staticmethod
    def init(
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_id: Optional[str] = None,
    ):
        """initializes common model settings"""

        config = Default()
        if not project_id:
            project_id = config.PROJECT_ID
        if not location:
            location = config.LOCATION
        if not model_id:
            model_id = config.MODEL_ID
        if None in [project_id, location, model_id]:
            raise ValueError("All parameters must be set.")
        print(f"initiating genai client with {project_id} in {location}")
        client = genai.Client(
            vertexai=config.INIT_VERTEX,
            project=project_id,
            location=location,
        )

        return client, model_id


class PersistenceSetup:
    """persistence set up class"""

    _client = None  # Class-level variable to store the Firestore client

    @classmethod
    def init(cls):
        """Initializes the Firestore client if it hasn't been already."""
        if cls._client is None:
            cls._client = initialize_firebase()
        return cls._client
