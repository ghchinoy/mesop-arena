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

import uuid
import logging

from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)

from google.cloud import aiplatform
from google import genai
from google.genai.types import (
    GenerateContentConfig,
)
from google.genai.errors import ClientError
import vertexai

from models.set_up import ModelSetup

from config.default import Default
from common.storage import store_to_gcs
from common.metadata import add_image_metadata


# Initialize configuration
client, model_id = ModelSetup.init()
MODEL_ID = model_id

config = Default()
logging.basicConfig(level=logging.DEBUG)

@retry(
    wait=wait_exponential(
        multiplier=2, min=1, max=25
    ),  # Exponential backoff (1s, 2s, 4s... up to 10s)
    stop=stop_after_attempt(3),  # Stop after 3 attempts
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    reraise=True,  # re-raise the last exception if all retries fail
)
def generate_images(prompt: str) -> str:
    """generate image content"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        logging.info(len(response.candidates[0].content.parts))
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    img_data = part.inline_data.data
                    break
        logging.info("success! inline_data.data length: %s", len(img_data))

        gcs_uri = store_to_gcs("gemini-2.0-flash-exp", f"{uuid.uuid4()}.png", "image/png", img_data, False)
        gcs_uri = f"gs://{gcs_uri}"
        logging.info("response: \"%s\"", response.candidates[0].content.parts[0].text)
        logging.info("gcs_uri: %s", gcs_uri)
        
        try:
            add_image_metadata(gcs_uri, prompt, config.MODEL_GEMINI2)
        except Exception as e:
            if "DeadlineExceeded" in str(e):  # Check for timeout error
                logging.error("Firestore timeout: %s", e)
            else:
                logging.error("Error adding image metadata: %s", e)

        return [gcs_uri]

    except Exception as e:
        logging.error("error: %s", e)
        raise  # Re-raise the exception for tenacity to handle


@retry(
    wait=wait_exponential(
        multiplier=2, min=1, max=25
    ),  # Exponential backoff (1s, 2s, 4s... up to 10s)
    stop=stop_after_attempt(3),  # Stop after 3 attempts
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    reraise=True,  # re-raise the last exception if all retries fail
)
def generate_content(prompt: str) -> str:
    """generate text content"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT"],
            ),
        )
        logging.info(f"success! {response.text}")
        return response.text

    except Exception as e:
        logging.error(f"error: {e}")
        raise  # Re-raise the exception for tenacity to handle
