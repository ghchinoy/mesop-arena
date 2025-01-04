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
""" History page"""
import mesop as me

from common.metadata import get_latest_votes


from components.header import header
from components.page_scaffold import (
    page_scaffold,
    page_frame,
)


def history_page_content(app_state: me.state):
    """History Mesop Page"""
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():  # pylint: disable=not-context-manager
            header("History", "history")

            with me.box():
                votes = get_latest_votes()
                print(f"retrieved {len(votes)} votes")
                for v in votes:
                    model1 = v.get('model1')
                    image1 = v.get('image1')
                    model2 = v.get('model2')
                    image2 = v.get('image2')
                    winner = v.get('winner')
                    timestamp = v.get('timestamp')
                    with me.box(
                        style=me.Style(
                            padding=me.Padding.all(10),
                        )
                    ):
                        me.text(f"At {timestamp}, {model1} ({image1}) competed against {model2} ({image2}) and {winner} won.")