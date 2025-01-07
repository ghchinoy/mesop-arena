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
""" Flux.1 model (Vertex AI Model Garden) """

import base64
import io
import logging
import time
from typing import Any
import uuid

from PIL import Image

from google.cloud import aiplatform

from config.default import Default
from common.storage import store_to_gcs
from common.metadata import add_image_metadata



config = Default()
logging.basicConfig(level=logging.DEBUG)


def base64_to_image(image_str: str) -> Any:
    """Convert base64 encoded string to an image.

    Args:
      image_str: A string of base64 encoded image.

    Returns:
      A PIL.Image instance.
    """
    image = Image.open(io.BytesIO(base64.b64decode(image_str)))
    return image


def flux_generate_images(model_name: str, prompt: str, aspect_ratio: str):
    """
    Creates images from Model Garden deployed Flux.1 model,
    Returns a list of gcs uris
    """

    start_time = time.time()

    arena_output = []
    print(f"model: {model_name}")
    print(f"prompt: {prompt}")
    print(f"target output: {config.GENMEDIA_BUCKET}")

    aiplatform.init(project=config.PROJECT_ID, location=config.LOCATION)

    instances = [{"text": prompt}]
    parameters = {
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 4,
    }

    endpoint = aiplatform.Endpoint(
        f"projects/{config.PROJECT_NUMBER}/locations/{config.LOCATION}/endpoints/{config.MODEL_FLUX1_ENDPOINT}"
    )

    response = endpoint.predict(
        instances=instances,
        parameters=parameters,
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    images = [
        #base64_to_image(prediction.get("output")) for prediction in response.predictions
        prediction.get("output") for prediction in response.predictions
    ]

    for idx, img in enumerate(images):
        logging.info(
            "Generated image %s with model %s in %s seconds",
            idx,
            model_name,
            f"{elapsed_time:.2f}",
        )

        gcs_uri = store_to_gcs("flux1", f"{uuid.uuid4()}.png", "image/png", img, True)
        gcs_uri = f"gs://{gcs_uri}" # append "gs://"

        logging.info(
            "generated image: %s len %s at %s", idx, len(img), gcs_uri
        )
        # output = img._as_base64_string()
        # state.image_output.append(output)
        arena_output.append(gcs_uri)
        logging.info("image created: %s", gcs_uri)
        try:
            add_image_metadata(gcs_uri, prompt, model_name)
        except Exception as e:
            if "DeadlineExceeded" in str(e):  # Check for timeout error
                logging.error("Firestore timeout: %s", e)
            else:
                logging.error("Error adding image metadata: %s", e)

    return arena_output
