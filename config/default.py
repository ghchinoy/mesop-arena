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
    PROJECT_NUMBER: str = os.environ.get("PROJECT_NUMBER")
    LOCATION: str = os.environ.get("LOCATION", "us-central1")
    MODEL_ID: str = os.environ.get("MODEL_ID", "gemini-2.0-flash-exp")
    INIT_VERTEX: bool = True

    GENMEDIA_BUCKET = os.environ.get("GENMEDIA_BUCKET", f"{PROJECT_ID}-genmedia")
    IMAGE_COLLECTION_NAME = os.environ.get("IMAGE_COLLECTION_NAME", "arena_images")
    IMAGE_RATINGS_COLLECTION_NAME = os.environ.get("IMAGE_RATINGS_COLLECTION_NAME", "arena_elo")
    ELO_K_FACTOR = os.environ.get("ELO_K_FACTOR", 32)

    # image models
    MODEL_IMAGEN2 = "imagegeneration@006"
    MODEL_IMAGEN3_FAST = "imagen-3.0-fast-generate-001"
    MODEL_IMAGEN3 = "imagen-3.0-generate-001"
    
    # model garden image models
    MODEL_FLUX1 = "black-forest-labs/FLUX.1-schnell"
    MODEL_FLUX1_ENDPOINT = "9021247714809085952" #"flux1-schnell-1736198391493@1"


    # pylint: disable=invalid-name
