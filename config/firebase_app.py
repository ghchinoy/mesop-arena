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

import logging

import firebase_admin
from firebase_admin import credentials, firestore

logging.basicConfig(level=logging.DEBUG)

def initialize_firebase():
    """Initializes Firebase app."""
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        logging.info("Firebase initialized successfully.")
        return firestore.client()
    except ValueError:
        logging.info("Firebase already initialized.")
        return firestore.client()

initialize_firebase()
