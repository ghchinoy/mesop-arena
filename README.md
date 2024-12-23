# Image Generation Arena & Leaderboard

This is an example of an arena & leaderboard to compare different image generation tools.

Currently, it uses Imagen 2, Imagen 3, and Gemini 2.0 experimental's image generation models.

The application is written in [Mesop](https://google.github.io/mesop/), a python UX framework, with the [Studio Scaffold starter](https://github.com/ghchinoy/studio-scaffold).



## Prerequisites


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

### Application environment vars

Images are generated and stored in a Google Cloud Storage bucket

```
export PROJECT_ID=$(gcloud config get project)
export GENMEDIA_BUCKET=${PROJECT_ID}-genmedia
```

Gemini 2.0 settings


## Arena app

Start the app to explore

```
mesop main.py
```

# Disclaimer

This is not an official Google project
