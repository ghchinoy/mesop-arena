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
""" Default Configuration for GenMedia Arena """

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


load_dotenv(override=True)


@dataclass
class GeminiModelConfig:
    """Configuration specific to Gemini models"""


@dataclass
class Default:
    """All configuration variables for this application are managed here."""

    # pylint: disable=invalid-name
    PROJECT_ID: str = os.environ.get("PROJECT_ID")
    LOCATION: str = os.environ.get("LOCATION", "us-central1")
    MODEL_ID: str = os.environ.get("MODEL_ID", "gemini-2.0-flash")
    INIT_VERTEX: bool = True

    GENMEDIA_BUCKET = os.environ.get("GENMEDIA_BUCKET")
    GENMEDIA_GENERATED_BUCKET = os.environ.get("GENMEDIA_GENERATED_BUCKET")
    IMAGE_FIREBASE_DB = os.environ.get("IMAGE_FIREBASE_DB", "")
    IMAGE_COLLECTION_NAME = os.environ.get("IMAGE_COLLECTION_NAME", "arena_images")
    IMAGE_RATINGS_COLLECTION_NAME = os.environ.get("IMAGE_RATINGS_COLLECTION_NAME", "arena_elo")
    ELO_K_FACTOR = int(os.environ.get("ELO_K_FACTOR", 32))

    # image models
    MODEL_IMAGEN2 = "imagegeneration@006"
    MODEL_IMAGEN3_FAST = "imagen-3.0-fast-generate-001"
    MODEL_IMAGEN3 = "imagen-3.0-generate-001"
    MODEL_IMAGEN32 = "imagen-3.0-generate-002"
    
    MODEL_GEMINI2 = "gemini-2.0-flash"

    # model garden image models
    MODEL_FLUX1 = "black-forest-labs/FLUX.1-schnell"
    MODEL_FLUX1_ENDPOINT_ID = os.environ.get("MODEL_FLUX1_ENDPOINT_ID")

    def __post_init__(self):
        """Validates the configuration variables after initialization."""

        if not self.PROJECT_ID:
            raise ValueError("PROJECT_ID environment variable is not set.")
        
        if not self.GENMEDIA_GENERATED_BUCKET:
            raise ValueError("GENMEDIA_GENERATED_BUCKET environment variable is not set.")

        if not self.GENMEDIA_BUCKET:
            raise ValueError("GENMEDIA_BUCKET environment variable is not set.")

        if not self.MODEL_FLUX1_ENDPOINT_ID:
            print("MODEL_FLUX1_ENDPOINT_ID environment variable is not set. List of models will exclude flux1") # Optional: List of models will exclude flux1

        if self.ELO_K_FACTOR <= 0:
            raise ValueError("ELO_K_FACTOR must be a positive integer.")

        valid_locations = ["us-central1", "us-east4", "europe-west4", "asia-east1"]  # example locations
        if self.LOCATION not in valid_locations:
            print(f"Warning: LOCATION {self.LOCATION} may not be valid.")
        print("Configuration validated successfully.")

    # pylint: disable=invalid-name
