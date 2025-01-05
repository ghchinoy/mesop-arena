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

import datetime
import pandas as pd

from google.cloud import firestore

from config.default import Default
from models.set_up import ModelSetup, PersistenceSetup


# Initialize configuration
client, model_id = ModelSetup.init()
MODEL_ID = model_id
config = Default()

db = PersistenceSetup.init()


def add_image_metadata(gcsuri: str, prompt: str, model: str):
    """Add Image metadata to Firestore persistence"""

    current_datetime = datetime.datetime.now()

    # Store the image metadata in Firestore
    doc_ref = db.collection(config.IMAGE_COLLECTION_NAME).document()
    doc_ref.set(
        {
            "gcsuri": gcsuri,
            "prompt": prompt,
            "model": model,
            "timestamp": current_datetime,  # alt: firestore.SERVER_TIMESTAMP
        }
    )

    print(f"Image data stored in Firestore with document ID: {doc_ref.id}")


def get_elo_ratings():
    """ Retrieve ELO ratings for models from Firestore """
    # Fetch current ELO ratings from Firestore
    doc_ref = (
        db.collection(config.IMAGE_RATINGS_COLLECTION_NAME)
        .where("type", "==", "elo_rating")
        .get()
    )
    updated_ratings = {}
    if doc_ref:
        for doc in doc_ref:
            ratings = doc.to_dict().get("ratings", {})
            updated_ratings.update(ratings)
    # Convert to DataFrame
    df = pd.DataFrame(list(updated_ratings.items()), columns=['Model', 'ELO Rating'])
    df = df.sort_values(by='ELO Rating', ascending=False)  # Sort by rating
    df.reset_index(drop=True, inplace=True)  # Reset index
    return df


def update_elo_ratings(model1: str, model2: str, winner: str, images: list[str], prompt: str):
    """Update ELO ratings for models"""

    current_datetime = datetime.datetime.now()

    # Fetch current ELO ratings from Firestore
    doc_ref = (
        db.collection(config.IMAGE_RATINGS_COLLECTION_NAME)
        .where("type", "==", "elo_rating")
        .get()
    )

    updated_ratings = {}
    elo_rating_doc_id = None  # Store the document ID
    if doc_ref:
        for doc in doc_ref:
            elo_rating_doc_id = doc.id  # Get the document ID
            ratings = doc.to_dict().get("ratings", {})
            updated_ratings.update(ratings)

    elo_model1 = updated_ratings.get(model1, 1000)  # Default to 1000 if not found
    elo_model2 = updated_ratings.get(model2, 1000)

    # Calculate expected scores
    expected_model1 = 1 / (1 + 10 ** ((elo_model2 - elo_model1) / 400))
    expected_model2 = 1 / (1 + 10 ** ((elo_model1 - elo_model2) / 400))

    # Update ELO ratings based on the winner
    k_factor = config.ELO_K_FACTOR
    if winner == model1:
        elo_model1 = elo_model1 + k_factor * (1 - expected_model1)
        elo_model2 = elo_model2 + k_factor * (0 - expected_model2)
    elif winner == model2:
        elo_model1 = elo_model1 + k_factor * (0 - expected_model1)
        elo_model2 = elo_model2 + k_factor * (1 - expected_model2)

    updated_ratings[model1] = round(elo_model1, 2)
    updated_ratings[model2] = round(elo_model2, 2)

    print(f"Ratings: {updated_ratings}")

    # Store updated ELO ratings in Firestore
    if elo_rating_doc_id:  # Check if the document ID was found
        doc_ref = db.collection(config.IMAGE_RATINGS_COLLECTION_NAME).document(elo_rating_doc_id)
        doc_ref.update(
            {
                "ratings": updated_ratings,
                "timestamp": current_datetime,
            }
        )
        print(f"ELO ratings updated in Firestore with document ID: {doc_ref.id}")
    else:
        # Document doesn't exist, create it
        doc_ref = db.collection(config.IMAGE_RATINGS_COLLECTION_NAME).document()
        doc_ref.set(
            {
                "type": "elo_rating",
                "ratings": updated_ratings,
                "timestamp": current_datetime,
            }
        )

        print(f"ELO ratings created in Firestore with document ID: {doc_ref.id}")

    doc_ref = db.collection(config.IMAGE_RATINGS_COLLECTION_NAME).document()
    doc_ref.set(
        {
            "timestamp": current_datetime,
            "type": "vote",
            "model1": model1,
            "image1": images[0],
            "model2": model2,
            "image2": images[1],
            "winner": winner,
            "prompt": prompt,
        }
    )

    print(f"Vote updated in Firestore with document ID: {doc_ref.id}")


def get_latest_votes(limit: int = 10):
    """Retrieve the latest votes from Firestore, ordered by timestamp in descending order."""

    try:
        votes_ref = (
            db.collection(config.IMAGE_RATINGS_COLLECTION_NAME)
            .where("type", "==", "vote")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        votes = []
        for doc in votes_ref.stream():
            votes.append(doc.to_dict())

        return votes

    except Exception as e:
        print(f"Error fetching votes: {e}")
        return []