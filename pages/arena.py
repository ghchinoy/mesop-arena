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

from google.cloud import aiplatform
import vertexai

import mesop as me

from config.default import Default
from state.state import AppState
from components.header import header

from models.set_up import ModelSetup

from models.gemini_model import (
    generate_content,
    generate_images,
)


# Initialize configuration
client, model_id = ModelSetup.init()
MODEL_ID = model_id


image_models = [
    Default.MODEL_IMAGEN2, 
    Default.MODEL_IMAGEN3_FAST, 
    Default.MODEL_IMAGEN3, 
    "gemini2",
] # "black-forest-labs/FLUX.1-schnell"]



@me.stateclass
class PageState:
    """Local Page State"""

    temp_name: str = ""
    is_loading: bool = False

    # pylint: disable=invalid-field-call
    arena_prompt: str = ""
    arena_textarea_key: int = 0
    arena_model1: str = ""
    arena_model2: str = ""
    arena_output: list[str] = field(default_factory=lambda:[])
    # pylint: disable=invalid-field-call


def arena_images(input: str):
    """ Create images for arena comparison """
    state = me.state(PageState)
    if input == "": # handle condition where someone hits "random" but doesn't modify
        if state.arena_prompt != "":
            input = state.arena_prompt
    state.arena_output.clear()

    prompt = input
    print(f"prompt: {prompt}")
    if state.image_negative_prompt_input:
        print(f"negative prompt: {state.image_negative_prompt_input}")

    # print(f"model: {state.arena_model1}")    
    # model1 = ImageGenerationModel.from_pretrained(state.arena_model1)


    if state.arena_model1.startswith('image'):
        state.arena_output.extend(imagen_generate_images(state.arena_model1, prompt, state.image_aspect_ratio))
    elif state.arena_model1 == "gemini2":
        print(f"model: {state.arena_model1}") 
        state.arena_output.append(generate_images(prompt))
    #else:
    #    # probably flux
    #    print(f"model: {state.arena_model1}") 
    #    state.arena_output.append(flux1_schnell.generate_images(prompt))

    #print(f"model: {state.arena_model2}")   
    #model2 = ImageGenerationModel.from_pretrained(state.arena_model2)


    if state.arena_model2.startswith('image'):
        state.arena_output.extend(imagen_generate_images(state.arena_model2, prompt, state.image_aspect_ratio))
    elif state.arena_model1 == "gemini2":
        print(f"model: {state.arena_model2}") 
        state.arena_output.append(generate_images(prompt))
    #else:
    #    # probably flux
    #    print(f"model: {state.arena_model2}") 
    #    state.arena_output.append(flux1_schnell.generate_images(prompt))


def imagen_generate_images(model_name: str, prompt: str, aspect_ratio: str):
    """creates images from Imagen and returns a list of gcs uris
    Args:
        model_name (str): imagen model name
        prompt (str): prompt for t2i model
        aspect_ratio (str): aspect ratio string
    Returns:
        _type_: a list of strings (gcs uris of image output)
    """
    arena_output = []
    print(f"model: {model_name}")
    model1 = ImageGenerationModel.from_pretrained(model_name)
    
    response = model1.generate_images(
        prompt=prompt,
        add_watermark=True,
        #aspect_ratio=getattr(state, "image_aspect_ratio"),
        aspect_ratio=aspect_ratio,
        number_of_images=1,
        output_gcs_uri=cfg.GENMEDIA_BUCKET,
        language="auto",
        #negative_prompt=state.image_negative_prompt_input,
        safety_filter_level="block_few",
        #include_rai_reason=True,
    )
    for idx, img in enumerate(response.images):
        print(f"generated image: {idx} len {len(img._as_base64_string())} at {img._gcs_uri}")
        #output = img._as_base64_string()
        #state.image_output.append(output)
        arena_output.append(img._gcs_uri)
        
    return arena_output


def random_prompt() -> str:
    """ return a random image generation prompt """
    # get a random prompt
    with open("imagen_prompts.json", "r") as file:
        data = file.read()
    prompts = json.loads(data)
    prompt = random.choice(prompts["imagen"])
    return prompt


def on_click_reload_arena(e: me.ClickEvent):  # pylint: disable=unused-argument
    """ Reload arena handler """
    state = me.state(PageState)

    state.arena_prompt = random_prompt()

    state.arena_output.clear()

    state.is_loading = True
    yield

    # get random images
    state.arena_model1, state.arena_model2 = random.sample(image_models, 2)
    print(f"{state.arena_model1} vs. {state.arena_model2}")
    arena_images(random_prompt)

    state.is_loading = False
    yield


def on_click_arena_vote(e: me.ClickEvent):
    """ Arena vote handler """
    state = me.state(PageState)
    model_name = getattr(state, e.key)
    print(f"user preferred {e.key}: {model_name}")

    on_click_reload_arena(e)
    yield


WELCOME_PROMPT = """
Welcome the user to the battle of the generative media images, and encourage participation by asserting their voting on the images presented. 
This should be one or two sentences.
"""


def reload_welcome(e: me.ClickEvent):  # pylint: disable=unused-argument
    """ Handle regeneration of welcome message event """
    app_state = me.state(AppState)
    app_state.welcome_message = generate_welcome()


def generate_welcome() -> str:
    """ Generate a nice welcome message with Gemini 2.0"""
    return generate_content(WELCOME_PROMPT)


def arena_page_content(app_state: me.state):
    """Arena Mesop Page"""

    page_state = me.state(PageState)

    if not app_state.welcome_message:
        app_state.welcome_message = generate_welcome()
    if not page_state.arena_prompt:
        page_state.arena_prompt = random_prompt()


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
                        flex_grow=1, display="flex",
                        align_items="center", justify_content="center",
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
                    with me.box(style=me.Style(
                        display="flex",
                        flex_direction="column",
                        align_items="center",
                        width="85%"
                    )):
                        me.text(
                            "Select the output you prefer for the given prompt", 
                            style=me.Style(font_weight=500, font_size="20px"),
                        )
                        me.box(style=me.Style(height=16))
                        me.text(page_state.arena_prompt)

                    # Image outputs
                    with me.box(style=_BOX_STYLE):
                        #with me.box(style=me.Style(align_content="center")):
                            #me.text(
                            #    "Select the image you prefer for the prompt above",
                            #    style=me.Style(font_weight=500),
                            #)
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
                                        img_url = img.replace(
                                            "gs://",
                                            "https://storage.mtls.cloud.google.com/",
                                        )
                                        me.image(
                                            src=f"{img_url}",
                                            style=me.Style(
                                                width="450px",
                                                margin=me.Margin(top=10),
                                                border_radius="35px",
                                            ),
                                        )

                                me.box(style=me.Style(height=15))

                                with me.box(
                                    style=me.Style(
                                        flex_direction="row",
                                        display="flex",
                                        gap=50,
                                    )
                                ):
                                    with me.content_button(
                                        type="flat",
                                        key="arena_model1",
                                        on_click=on_click_arena_vote,
                                    ):
                                        with me.box(
                                            style=me.Style(
                                                display="flex", align_items="center"
                                            )
                                        ):
                                            me.icon("arrow_left")
                                            me.text("left")

                                    me.button(
                                        label="skip",
                                        type="stroked",
                                        on_click=on_click_reload_arena,
                                    )

                                    with me.content_button(
                                        type="flat",
                                        key="arena_model2",
                                        on_click=on_click_arena_vote,
                                    ):
                                        with me.box(
                                            style=me.Style(
                                                display="flex", align_items="center"
                                            )
                                        ):
                                            me.text("right")
                                            me.icon("arrow_right")


_BOX_STYLE = me.Style(
    flex_basis="max(480px, calc(50% - 48px))",
    background=me.theme_var("background"),
    border_radius=12,
    box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
    padding=me.Padding(top=16, left=16, right=16, bottom=16),
    display="flex",
    flex_direction="column",
    width="100%"
)
