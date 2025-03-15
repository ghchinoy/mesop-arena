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
""" Utility functions for prompts """

import json
import random

class PromptManager:
    """Singleton class to manage and provide image generation prompts"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptManager, cls).__new__(cls)
            cls._instance._load_prompts()
        return cls._instance

    def _load_prompts(self):
        """Loads prompts from the JSON file into memory."""
        try:
            with open("imagen_prompts.json", "r") as file:
                data = file.read()
            self.prompts = json.loads(data)
        except FileNotFoundError:
            print("Error: imagen_prompts.json not found.")
            self.prompts = {"imagen": []} #initialize to empty list to avoid errors.
        except json.JSONDecodeError:
            print("Error: imagen_prompts.json is not valid JSON.")
            self.prompts = {"imagen": []}

    def random_prompt(self) -> str:
        """Returns a random image generation prompt."""
        if self.prompts and self.prompts["imagen"]:
            return random.choice(self.prompts["imagen"])
        else:
            return "Default prompt: No prompts available."  # Handle empty prompt list

if __name__ == "__main__":
    prompt_manager = PromptManager()
    random_prompt1 = prompt_manager.random_prompt()
    random_prompt2 = prompt_manager.random_prompt()

    print(random_prompt1)
    print(random_prompt2)

    # Verify singleton behavior:
    another_manager = PromptManager()
    print(prompt_manager is another_manager)  # Should print True