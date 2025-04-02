# Image Generation Arena & Leaderboard

This is an example of an arena & leaderboard to compare different image generation tools.

Currently, it uses Imagen 2, Imagen 3, image generation models with Gemini 2.0 experimental's image output model forthcoming.

The application is written in [Mesop](https://google.github.io/mesop/), a python UX framework, with the [Studio Scaffold starter](https://github.com/ghchinoy/studio-scaffold).


![](./assets/arena_view.png)

![](./assets/latest-small.gif)


## Prerequisites
The following APIs are required in your project:

1. Vertex AI API
1. Dataform API
1. Compute Engine API
1. Cloud Storage



### Python environment

A python virtual environment, with required packages installed.

Using [uv](https://github.com/astral-sh/uv):

```
# create a virtual environment
uv venv venv
# activate the virtual environ,ent
. venv/bin/activate
# install the requirements
uv pip install -r requirements.txt
```

### Cloud Firestore

We will be using [Cloud Firestore](https://firebase.google.com/docs/firestore), a NoSQL cloud database that is part of the Firebase ecosystem and built on Google Cloud infrastructure, to save generated image metadata and ELO scores for the leaderboard.

> If you're new to Firebase, a great starting point is [here](https://firebase.google.com/docs/projects/learn-more#firebase-cloud-relationship). 

Go to your Firebase project and create a database. Instructions on how to do this can be found [here](https://firebase.google.com/docs/firestore/quickstart).

Next do the following steps:

1. Create a collection called `arena_images`.
1. Create a collection called `arena_elo`
1. Create an index for `arena_elo` with two fields: `type` set to `ASC` and `timestamp` set to `DESC` and query scope set to `Collection Group`.


The name of the collections can be changed via environment variables in the `.env` file. i.e. `IMAGE_COLLECTION_NAME` and `IMAGE_RATINGS_COLLECTION_NAME`, respectively.

To verify your index has been created successfully, run the following command:

```bash
firebase firestore:indexes --database <DATABASE_NAME> --project <YOUR_PROJECT_ID>
```

The output should look like this:

```json
{
  "indexes": [
    {
      "collectionGroup": "arena_elo",
      "queryScope": "COLLECTION_GROUP",
      "fields": [
        {
          "fieldPath": "type",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "timestamp",
          "order": "DESCENDING"
        }
      ]
    }
  ],
  "fieldOverrides": []
}
```

### Cloud Spanner
We use Cloud Spanner to store the ELO scores, per model, for each rating done. Before running the application. 

> **IMPORTANT:** As a prerequisite, create an instance of Cloud Spanner with 100 processing units from the Cloud Console. Instructions can be found [here](https://cloud.google.com/spanner/docs/getting-started).

Next, change the following environment variables or use the default values already set in the `.env.template` file.


```bash
PROJECT_ID=<YOUR_PROJECT_ID>
SPANNER_INSTANCE_ID="arena"
SPANNER_DATABASE_ID="study"
```

Now run the following script to create the tables and indexes.  

```bash
python3 -m scripts.setup_study_db
``` 


### Application environment vars

Images are generated and stored in a Google Cloud Storage bucket.

The repository has a file named `.env.template` that you can use as a template.

> **IMPORTANT:** Rename `.env.template` to `.env` and fill in your entries.

```
PROJECT_ID=<YOUR_PROJECT_ID>
GENMEDIA_BUCKET=${PROJECT_ID}-genmedia
GEMINI_PROJECT_ID=<YOUR_PROJECT_ID_WITH_GEMINI_API_ACCESS>
LOCATION="us-central1"
MODEL_ID="gemini-2.0-flash"
IMAGE_FIREBASE_DB="arena"
IMAGE_COLLECTION_NAME="arena_images"
IMAGE_RATINGS_COLLECTION_NAME="arena_elo"
ELO_K_FACTOR=32
MODEL_FLUX1_ENDPOINT_ID=<YOUR_FLUX1_MODEL_ENDPOINT_ID> # This is the endpoint ID for the Flux1 model in Model Garden
MODEL_STABLE_DIFFUSION_ENDPOINT_ID=<YOUR_STABLEDIFFUSION_ENDPOINT_ID> # This is the endpoint ID for the StableDiffusion model in Model Garden
```


## Arena app

Start the app to explore

```
mesop main.py
```


## Deploy


### Service Account
Create a Service Account to run your service, and provide the following permissions to the Service Account

* Cloud Run Invoker
* Vertex AI User
* Cloud Datastore User
* Storage Object User

```
export PROJECT_ID=$(gcloud info --format='value(config.project)')

export DESC="genmedia arena"
export SA_NAME="sa-genmedia-arena"
export SA_ID=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

# create a service account
gcloud iam service-accounts create $SA_NAME --description $DESC --display-name $SA_NAME

# assign vertex and cloud run roles
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SA_ID}" --role "roles/run.invoker"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SA_ID}" --role "roles/aiplatform.user"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SA_ID}" --role "roles/storage.objectUser"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SA_ID}" --role "roles/datastore.user"
```

### Deploy

```
gcloud run deploy genmedia-arena --source . \
    --service-account=$SA_ID \
    --set-env-vars GENMEDIA_BUCKET=${PROJECT_ID}-genmedia \
    --set-env-vars PROJECT_ID=${PROJECT_ID} \
    --set-env-vars MODEL_ID=gemini-2.0-flash \
    --region us-central1
```


# Disclaimer

This is not an official Google project
