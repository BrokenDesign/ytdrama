# YouTube Drama
This is mostly just a for-fun thing, to learn some of the Google API and sqlalchemy's ORM. 

## What does it do?
Given a list of channels defined in `config.toml` it will extract data associated with all of the videos uploaded to the two channels and their corresponding transcripts (if they exist). This data is then saved into `data/yt.sqlite` for analysis (TODO). At the very least the analysis is going to include how often the streamers mentioned each other over time, and as a function of the time streamed -- this is drama afterall, we have to see who is living rent free. But I might also play around with some other NLP/visualizations. 

## Configuration
There are two files that drive most things: 
* config.toml, contains all of the settings used within `/ytdrama`
* logging.toml, contains the settings for the loggers. By default it will go to console and log. There are a few different formatters in there if you woult like to see different detail. 

## Prerequisites
An existing python installation >= 3.11. 
Poetry installed, this can be installed with: 
```
pip install poetry
```
You need to create a .env file at project level (even if empty)
GCS project with a generated API key placed in config.toml or the .env file (called SECRET). 

## Instructions
From within the project directory run:
```bash 
poetry install
poetry use 
```
Change config.toml to reference the channels you want. 
Configure anything else you want to change. 
Run `/scripts/extract_data.py` to create the sqlite database. 
All other analysis will be in either `scripts/` or `notebooks/`

