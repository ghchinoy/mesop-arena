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
""" Gemini model methods """

import random
import time

from google.cloud import aiplatform
from google import genai
from google.genai.types import (
    GenerateContentConfig,
)
from google.genai.errors import (
    ClientError
)
import vertexai

from config.config import Config


# Initialize configuration
cfg = Config()
vertexai.init(project=cfg.PROJECT_ID, location=cfg.LOCATION)
aiplatform.init(project=cfg.PROJECT_ID, location=cfg.LOCATION)
client = genai.Client(
    vertexai=True,
    project=cfg.PROJECT_ID,
    location=cfg.LOCATION,
)


def generate_images(prompt: str) -> str:
    """generate text content"""

    max_retries = 3
    retry_count = 0
    backoff_factor = 1  # Initial backoff factor (in seconds)

    while retry_count < max_retries:
        try:
            response = client.models.generate_content(
                model=cfg.MODEL_GEMINI_MULTIMODAL,
                contents=prompt,
                config=GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )
            print(f"success! {response.text}")
            return response.text

        except ClientError as e:
            print(f"error: {e}")
            #print(f"Exception type: {type(e).__name__} in {e.__class__.__module__}")

            if hasattr(e, 'code') and e.code == 429:  # ClientError
                print(f"An error occurred: {e}")
                retry_count += 1

                # Exponential backoff with jitter
                sleep_time = backoff_factor * (1 + random.random())  # Add jitter
                print(
                    f"Retrying in {sleep_time:.2f} seconds (attempt {retry_count}/{max_retries})"
                )
                time.sleep(sleep_time)
                backoff_factor *= 2  # Increase backoff factor exponentially
            else:
                return "oops, couldn't be nice"

    return "oops, couldn't be nice"


def generate_content(prompt: str) -> str:
    """generate text content"""

    max_retries = 3
    retry_count = 0
    backoff_factor = 1  # Initial backoff factor (in seconds)

    while retry_count < max_retries:
        try:
            response = client.models.generate_content(
                model=cfg.MODEL_GEMINI_MULTIMODAL,
                contents=prompt,
                config=GenerateContentConfig(
                    response_modalities=["TEXT"],
                ),
            )
            print(f"success! {response.text}")
            return response.text

        except ClientError as e:
            print(f"error: {e}")
            #print(f"Exception type: {type(e).__name__} in {e.__class__.__module__}")

            if hasattr(e, 'code') and e.code == 429:  # ClientError
                print(f"An error occurred: {e}")
                retry_count += 1

                # Exponential backoff with jitter
                sleep_time = backoff_factor * (1 + random.random())  # Add jitter
                print(
                    f"Retrying in {sleep_time:.2f} seconds (attempt {retry_count}/{max_retries})"
                )
                time.sleep(sleep_time)
                backoff_factor *= 2  # Increase backoff factor exponentially
            else:
                return "oops, couldn't be nice"

    return "oops, couldn't be nice"
