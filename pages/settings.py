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
import mesop as me

from components.header import header
from components.page_scaffold import (
    page_scaffold,
    page_frame,
)

from typing import Any
from config.default import Default
from config.firebase_config import FirebaseClient

import asyncio
from google.cloud.firestore import AsyncClient, FieldFilter


cnfg = Default()
db = FirebaseClient(cnfg.IMAGE_FIREBASE_DB).get_client()

def settings_page_content(app_state: me.state):
    """Settings Mesop Page"""
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("Settings", "settings")

            me.text(f"Hello, {app_state.name}!")
            _render_study_info(_get_studies(), app_state)

async def _purge_elo_ratings(study: str) -> bool:
    db = AsyncClient(project=cnfg.PROJECT_ID, database=cnfg.IMAGE_FIREBASE_DB)

    batch_transcations = db.batch()
    ratings = db.collection("arena_elo")
    docs = ratings.where(filter=FieldFilter("study", "==", study)).stream()

    batches = []
    idx = 0
    async for doc in docs:
        doc_ref = doc.reference
        batch_transcations.delete(doc_ref)

        if((idx + 1) % 1000 == 0):
            batches.append(batch_transcations.commit(timeout=60))
            batch_transcations = db.batch()
        idx += 1
        idx = idx % 1000
    
    if batch_transcations:
        batches.append(batch_transcations.commit(timeout=60))
    
    results = await asyncio.gather(*batches)

    return all(results)

def _get_studies() -> dict[dict[str, Any]]:
    studies = dict()
    docs = db.collection(cnfg.STUDY_COLLECTION_NAME).stream()
    for doc in docs:
        doc_content = doc.to_dict()
        studies.update({doc_content['label']: doc_content})
    studies.update({"live": {"label": "live", "gcsuri": "imagen_prompts.json"}})
    return studies

def _render_study_info(studies: dict[dict[str, Any]], app_state: me.state):
    def _handle_select(study: me.ClickEvent):
        app_state.study = study.key
        app_state.study_prompts_location = studies[study.key]['gcsuri']
        app_state.study_models = studies[study.key].get('models', [])
    
    def _handle_purge(study: me.ClickEvent):
        asyncio.run(_purge_elo_ratings(study=study.key))
    
    if len(studies):
        me.markdown("## Select a Study:")
        for study in studies.keys():
            with me.box(style=_BOX_STYLE):
                for key, value in studies[study].items():
                    me.markdown(f"**{key}:** {value}")
                me.button(label="Select Study", on_click=lambda study=study: _handle_select(study), key=study, disabled=app_state.study == study)

                
            me.divider(inset=False)
        me.button(label="Reset Leaderboard", style=me.Style(position="absolute", top="70%", right="750px", transform="translateY(-50%)"),
                            on_click=lambda study=app_state.study: _handle_purge(study), key=f"{app_state.study}")
            
    else:
        me.markdown("No Studies found")

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