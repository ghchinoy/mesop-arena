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

from models.image_models import ImageModel


@dataclass
class GeminiModelConfig:
    """Configuration specific to Gemini models"""


@dataclass
class Config:
    """All configuration variables for this application are managed here."""

    GENMEDIA_BUCKET = os.environ.get("GENMEDIA_BUCKET")
    PROJECT_ID = os.environ.get("PROJECT_ID", "")
    LOCATION = os.getenv("LOCATION", "us-central1")
    MODEL_GEMINI_MULTIMODAL = "gemini-2.0-flash-exp"
    MODEL_IMAGEN2 = "imagegeneration@006"
    MODEL_IMAGEN3_FAST = "imagen-3.0-fast-generate-001"
    MODEL_IMAGEN3 = "imagen-3.0-generate-001"
