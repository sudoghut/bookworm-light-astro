# Generate data steps

## Step 1

Create introduction, and put it into data_intro.md

## Step 2

Decide your feature image (original title), and put it into data_config.csv

## Step3

Decide whether you want to get new titles and tags from GPT or Groq

### If GPT

1. Using 0_gpt_prompt_for_title_tags.md to get titles and tags

2. Save the titles and tags json into data_new_title_and_tags.json

3. Set offline-title-tags-json from data_config.csv as True

### If Groq

Set offline-title-tags-json from data_config.csv as False