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

from dataclasses import field
import random
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# from google.cloud import aiplatform
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

import mesop as me

from common.metadata import (
    add_image_metadata,
    update_elo_ratings,
)
from config.default import Default
from state.state import AppState
from components.header import header

from models.set_up import ModelSetup
from models.gemini_model import (
    generate_content,
    generate_images,
)
from models.model_garden_flux import flux_generate_images

# Initialize configuration
client, model_id = ModelSetup.init()
MODEL_ID = model_id
config = Default()
logging.basicConfig(level=logging.DEBUG)

image_models = [
    Default.MODEL_IMAGEN2,
    Default.MODEL_IMAGEN3_FAST,
    Default.MODEL_IMAGEN3,
    # Default.MODEL_FLUX1,
    Default.MODEL_GEMINI2,
]


@me.stateclass
class PageState:
    """Local Page State"""

    temp_name: str = ""
    is_loading: bool = False

    # pylint: disable=invalid-field-call
    arena_prompt: str = ""
    image_negative_prompt_input: str = ""
    image_aspect_ratio: str = "1:1"
    arena_textarea_key: int = 0
    arena_model1: str = ""
    arena_model2: str = ""
    arena_output: list[str] = field(default_factory=lambda: [])
    chosen_model: str = ""
    # pylint: disable=invalid-field-call


def arena_images(input: str):
    """Create images for arena comparison"""
    state = me.state(PageState)
    if input == "":  # handle condition where someone hits "random" but doesn't modify
        if state.arena_prompt != "":
            input = state.arena_prompt
    state.arena_output.clear()

    logging.info("BATTLE: %s vs. %s", state.arena_model1, state.arena_model2)

    prompt = input
    logging.info("prompt: %s", prompt)
    if state.image_negative_prompt_input:
        logging.info("negative prompt: %s", state.image_negative_prompt_input)

    with ThreadPoolExecutor() as executor:  # Create a thread pool
        futures = []
    # print(f"model: {state.arena_model1}")
    # model1 = ImageGenerationModel.from_pretrained(state.arena_model1)

        # model 1
        if state.arena_model1.startswith("image"):
            futures.append(
                executor.submit(
                    imagen_generate_images,
                    state.arena_model1,
                    prompt,
                    state.image_aspect_ratio,
                )
            )
            # state.arena_output.extend(
            #    imagen_generate_images(state.arena_model1, prompt, state.image_aspect_ratio),
            # )
        elif state.arena_model1.startswith(config.MODEL_GEMINI2):
            logging.info("model: %s", state.arena_model1)
            futures.append(
                executor.submit(
                    generate_images,
                    prompt,

                )
            )
            #state.arena_output.append(generate_images(prompt))

        elif state.arena_model1.startswith(config.MODEL_FLUX1):
            if config.MODEL_FLUX1_ENDPOINT:
                logging.info("model: %s", state.arena_model1)
                futures.append(
                    executor.submit(
                        flux_generate_images,
                        state.arena_model1,
                        prompt,
                        state.image_aspect_ratio,
                    )
                )
            else:
                logging.info("no endpoint defined for %s", config.MODEL_FLUX1)

        # model 2
        if state.arena_model2.startswith("image"):
            futures.append(
                executor.submit(
                    imagen_generate_images,
                    state.arena_model2,
                    prompt,
                    state.image_aspect_ratio,
                )
            )
            # state.arena_output.extend(imagen_generate_images(state.arena_model2, prompt, state.image_aspect_ratio))

        elif state.arena_model2.startswith(config.MODEL_GEMINI2):
            logging.info("model: %s", state.arena_model2)
            futures.append(
                executor.submit(
                    generate_images,
                    prompt,

                )
            )
            #state.arena_output.append(generate_images(prompt))

        elif state.arena_model2.startswith(config.MODEL_FLUX1):
            if config.MODEL_FLUX1_ENDPOINT:
                logging.info("model: %s", state.arena_model2)
                futures.append(
                    executor.submit(
                        flux_generate_images,
                        state.arena_model2,
                        prompt,
                        state.image_aspect_ratio,
                    )
                )
            else:
                logging.info("no endpoint defined for %s", config.MODEL_FLUX1)

        for future in as_completed(futures):  # Wait for tasks to complete
            try:
                result = future.result()  # Get the result of each task
                state.arena_output.extend(
                    result
                )  # Assuming imagen_generate_images returns a list
            except Exception as e:
                logging.error(f"Error during image generation: {e}")



def imagen_generate_images(model_name: str, prompt: str, aspect_ratio: str):
    """creates images from Imagen and returns a list of gcs uris
    Args:
        model_name (str): imagen model name
        prompt (str): prompt for t2i model
        aspect_ratio (str): aspect ratio string
    Returns:
        _type_: a list of strings (gcs uris of image output)
    """

    start_time = time.time()

    arena_output = []
    logging.info(f"model: {model_name}")
    logging.info(f"prompt: {prompt}")
    logging.info(f"target output: {config.GENMEDIA_BUCKET}")

    vertexai.init(project=config.PROJECT_ID, location=config.LOCATION)

    image_model = ImageGenerationModel.from_pretrained(model_name)

    response = image_model.generate_images(
        prompt=prompt,
        add_watermark=True,
        # aspect_ratio=getattr(state, "image_aspect_ratio"),
        aspect_ratio=aspect_ratio,
        number_of_images=1,
        output_gcs_uri=f"gs://{config.GENMEDIA_BUCKET}",
        language="auto",
        # negative_prompt=state.image_negative_prompt_input,
        safety_filter_level="block_few",
        # include_rai_reason=True,
    )
    end_time = time.time()
    elapsed_time = end_time - start_time

    for idx, img in enumerate(response.images):
        logging.info(f"Generated image: #{idx} with model {model_name} in {elapsed_time:.2f} seconds")

        logging.info(
            f"Generated image: #{idx}, len {len(img._as_base64_string())} at {img._gcs_uri}"
        )
        # output = img._as_base64_string()
        # state.image_output.append(output)
        arena_output.append(img._gcs_uri)
        logging.info(f"Image created: {img._gcs_uri}")
        try:
            add_image_metadata(img._gcs_uri, prompt, model_name)
        except Exception as e:
            if "DeadlineExceeded" in str(e):  # Check for timeout error
                logging.error(f"Firestore timeout: {e}")
            else:
                logging.error(f"Error adding image metadata: {e}")

    return arena_output


def random_prompt() -> str:
    """return a random image generation prompt"""
    # get a random prompt
    with open("imagen_prompts.json", "r") as file:
        data = file.read()
    prompts = json.loads(data)
    prompt = random.choice(prompts["imagen"])
    return prompt


def on_click_reload_arena(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Reload arena handler"""
    state = me.state(PageState)

    state.arena_prompt = random_prompt()

    state.arena_output.clear()

    state.is_loading = True
    yield

    # get random images
    state.arena_model1, state.arena_model2 = random.sample(image_models, 2)
    
    arena_images(state.arena_prompt)

    state.is_loading = False
    yield


def on_click_arena_vote(e: me.ClickEvent):
    """Arena vote handler"""
    state = me.state(PageState)
    model_name = getattr(state, e.key)
    logging.info("user preferred %s: %s", e.key, model_name)
    state.chosen_model = model_name
    # update the elo ratings
    update_elo_ratings(state.arena_model1, state.arena_model2, model_name, state.arena_output, state.arena_prompt)
    yield
    time.sleep(1)
    yield
    # clear the output and reload
    state.arena_output.clear()
    state.chosen_model = ""
    state.arena_prompt = random_prompt()
    yield
    arena_images(state.arena_prompt)
    yield


WELCOME_PROMPT = """
Welcome the user to the battle of the generative media images, and encourage participation by asserting their voting on the images presented. 
This should be one or two sentences.
"""


def reload_welcome(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Handle regeneration of welcome message event"""
    app_state = me.state(AppState)
    app_state.welcome_message = generate_welcome()
    yield


def generate_welcome() -> str:
    """Generate a nice welcome message with Gemini 2.0"""
    return generate_content(WELCOME_PROMPT)


def arena_page_content(app_state: me.state):
    """Arena Mesop Page"""

    page_state = me.state(PageState)

    # TODO this is an initialization function that should be extracted
    if not app_state.welcome_message:
        app_state.welcome_message = generate_welcome()
    if not page_state.arena_prompt:
        page_state.arena_prompt = random_prompt()
        page_state.arena_model1 = config.MODEL_IMAGEN2
        page_state.arena_model2 = config.MODEL_IMAGEN3_FAST
        arena_images(page_state.arena_prompt)
        # imagen_generate_images(Default.MODEL_IMAGEN3_FAST, page_state.arena_prompt, "1:1")

    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column",
            height="100%",
        ),
    ):
        with me.box(
            style=me.Style(
                background=me.theme_var("background"),
                height="100%",
                overflow_y="scroll",
                margin=me.Margin(bottom=20),
            )
        ):
            with me.box(
                style=me.Style(
                    background=me.theme_var("background"),
                    padding=me.Padding(top=24, left=24, right=24, bottom=24),
                    display="flex",
                    flex_direction="column",
                )
            ):
                header("Arena", "stadium")

                # welcome message
                with me.box(
                    style=me.Style(
                        flex_grow=1,
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    on_click=reload_welcome,
                ):
                    me.text(
                        app_state.welcome_message,
                        style=me.Style(
                            width="80vw",
                            font_size="10pt",
                            font_style="italic",
                            color="gray",
                        ),
                    )

                me.box(style=me.Style(height="16px"))

                with me.box(
                    style=me.Style(
                        margin=me.Margin(left="auto", right="auto"),
                        width="min(1024px, 100%)",
                        gap="24px",
                        flex_grow=1,
                        display="flex",
                        flex_wrap="wrap",
                        flex_direction="column",
                        align_items="center",
                    )
                ):
                    # Prompt
                    with me.box(
                        style=me.Style(
                            display="flex",
                            flex_direction="column",
                            align_items="center",
                            width="85%",
                        )
                    ):
                        me.text(
                            "Select the output you prefer for the given prompt",
                            style=me.Style(font_weight=500, font_size="20px"),
                        )
                        me.box(style=me.Style(height=16))
                        me.text(page_state.arena_prompt)

                    # Image outputs
                    with me.box(style=_BOX_STYLE):
                        # with me.box(style=me.Style(align_content="center")):
                        # me.text(
                        #    "Select the image you prefer for the prompt above",
                        #    style=me.Style(font_weight=500),
                        # )
                        if page_state.is_loading:
                            with me.box(
                                style=me.Style(
                                    display="grid",
                                    justify_content="center",
                                    justify_items="center",
                                )
                            ):
                                me.progress_spinner()
                        if len(page_state.arena_output) != 0:
                            with me.box(
                                style=me.Style(
                                    display="grid",
                                    justify_content="center",
                                    justify_items="center",
                                )
                            ):
                                # Generated images row
                                with me.box(
                                    style=me.Style(
                                        flex_wrap="wrap", display="flex", gap="15px"
                                    )
                                ):
                                    for idx, img in enumerate(page_state.arena_output):
                                        model_name = f"arena_model{idx+1}"
                                        model_value = getattr(page_state, model_name)

                                        img_url = img.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        )
                                        with me.box(
                                            style=me.Style(align_items="center", justify_content="center", display="flex", flex_direction="column"),
                                        ):
                                            image_border_style = me.Style(
                                                width="450px",
                                                margin=me.Margin(top=10),
                                                border_radius="35px",
                                            )
                                            if page_state.chosen_model:
                                                if page_state.chosen_model == model_value:
                                                    # green border
                                                    image_border_style = me.Style(
                                                        width="450px",
                                                        margin=me.Margin(top=10),
                                                        border_radius="35px",
                                                        border=me.Border().all(me.BorderSide(color="green", style="inset", width="5px"))
                                                    )
                                                else:
                                                    # opaque
                                                    image_border_style = me.Style(
                                                        width="450px",
                                                        margin=me.Margin(top=10),
                                                        border_radius="35px",
                                                        opacity=0.5,
                                                    )
                                            me.image(
                                                src=f"{img_url}",
                                                style=image_border_style,
                                            )
                                            
                                            if page_state.chosen_model:
                                                text_style = me.Style()
                                                if page_state.chosen_model == model_value:
                                                    text_style = me.Style(font_weight="bold")
                                                me.text(model_value, style=text_style)
                                            else:
                                                me.box(style=me.Style(height=18))

                                me.box(style=me.Style(height=15))

                                if len(page_state.arena_output) != 2:
                                    disabled_choice = True
                                else:
                                    disabled_choice = False

                                with me.box(
                                    style=me.Style(
                                        flex_direction="row",
                                        display="flex",
                                        gap=50,
                                    )
                                ):
                                    # left choice button
                                    with me.content_button(
                                        type="flat",
                                        key="arena_model1",
                                        on_click=on_click_arena_vote,
                                        disabled=disabled_choice,
                                    ):
                                        with me.box(
                                            style=me.Style(
                                                display="flex", align_items="center"
                                            )
                                        ):
                                            me.icon("arrow_left")
                                            me.text("left")
                                    # skip button
                                    me.button(
                                        label="skip",
                                        type="stroked",
                                        on_click=on_click_reload_arena,
                                    )
                                    # right choice button
                                    with me.content_button(
                                        type="flat",
                                        key="arena_model2",
                                        on_click=on_click_arena_vote,
                                        disabled=disabled_choice,
                                    ):
                                        with me.box(
                                            style=me.Style(
                                                display="flex", align_items="center"
                                            )
                                        ):
                                            me.text("right")
                                            me.icon("arrow_right")
                    # show user choice
                    if page_state.chosen_model:
                        me.text(f"You voted {page_state.chosen_model}")


_BOX_STYLE = me.Style(
    flex_basis="max(480px, calc(50% - 48px))",
    background=me.theme_var("background"),
    border_radius=12,
    box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
    padding=me.Padding(top=16, left=16, right=16, bottom=16),
    display="flex",
    flex_direction="column",
    width="100%",
)
