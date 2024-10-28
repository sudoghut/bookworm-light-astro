# pip install groq
from groq import Groq
import os
import datetime
import requests
import json

INPUT_IMG_URL = "https://oopus.info/imghorce/_working/list_image_files.php"
OUPUT_FOLDER = ["generate_data", "output"]
OUTPUT_IMG_FOLDER = ["generate_data", "output"]
CONFIG_FILE = os.path.join(os.getcwd(), "generate_data", "data_config.csv")
INTRO_FILE = os.path.join(os.getcwd(), "generate_data", "data_intro.md")
API_KEY_FILE = os.path.join(os.getcwd(), "generate_data", "api_key.txt")
PROMPT_FILE = os.path.join(os.getcwd(), "generate_data", "data_prompt.md")
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


# Read api key
with open(API_KEY_FILE, "r", encoding="utf-8") as f:
    API_KEY = f.read().strip()
CLIENT = Groq(api_key = API_KEY)

# Read config file
config = {}
with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip().split(",")
        config[line[0]] = line[1]
print(config)

INTRO_TEXT = ""
with open(INTRO_FILE, "r", encoding="utf-8") as f:
    INTRO_TEXT = f.read().strip()

# Read prompt
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT = f.read().strip()
print(PROMPT)

# Empty the output
if os.path.exists(os.path.join(os.getcwd(), *OUPUT_FOLDER)):
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), *OUPUT_FOLDER)):
        for file in files:
            os.remove(os.path.join(root, file))

# Create output image folder
TODAY_DATE = datetime.datetime.now().strftime("%Y%m%d")
OUTPUT_IMG_FOLDER = os.path.join(os.getcwd(), *OUPUT_FOLDER, f"{config['title'].replace(' ','-')}-{TODAY_DATE}")
if not os.path.exists(OUTPUT_IMG_FOLDER):
    os.makedirs(OUTPUT_IMG_FOLDER)

# Get all image names
image_name_list = []
response = requests.get(INPUT_IMG_URL, headers=HEADERS)
image_name_list = response.json()
print(image_name_list)

# for test
# image_name_list = [image_name_list[0]]
# image_name_list = image_name_list[:2]

# Get image title and tags
def get_image_title_and_tags(image_name):
    image_url = INPUT_IMG_URL.replace("list_image_files.php", "") + image_name
    completion = CLIENT.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{PROMPT}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{image_url}"
                        }
                    }
                ]
            },
            {
                "role": "assistant",
                "content": ""
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        stream=False,
        stop=None,
    )
    output_text = completion.choices[0].message.content
    print(output_text[-1])
    if output_text[-1] != "}":
        output_text = output_text[:-1]
    print(output_text)
    return json.loads(output_text)
    

image_name_content_dict = {}
tag_list = []
for image_name in image_name_list:
    print(image_name)
    image_generated_dic = get_image_title_and_tags(image_name)
    # create image_new_name and image_content from image_generated_dic
    image_new_name = ""
    image_content = ""
    for idx, val in image_generated_dic.items():
        image_new_name = idx.replace(" ", "-") + "." + image_name.split(".")[1]
        image_content = val
        tag_list += val
    image_name_content_dict[image_name] = {image_new_name: image_content}
tag_list = list(set(tag_list))
tag_text = ", ".join(tag_list)

# Save file:
# 1. Save image with new name
# 2. Create blog md
CURRENT_TIMEZONE = datetime.datetime.now().astimezone().strftime("%z")
time_for_blog = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S") + CURRENT_TIMEZONE
time_for_blog = time_for_blog[:-2] + ":" + time_for_blog[-2:]
IMG_ONLINE_ROOT = INPUT_IMG_URL.replace("_working/list_image_files.php", "") + f"{config['title'].replace(' ','-')}-{TODAY_DATE}" + "/"
print(image_name_content_dict[config['featured-image']].keys())
print(list(image_name_content_dict[config['featured-image']].keys()))
FEATURED_IMAGE = IMG_ONLINE_ROOT + list(image_name_content_dict[config['featured-image']].keys())[0]
print(FEATURED_IMAGE)

blog_md = f'''---
title: "{config['title']}"
description: "meta description"
date: {time_for_blog}
image: "{FEATURED_IMAGE}"
categories: ["{config['category']}"]
authors: ["Imghorce Oopus"]
tags: [{tag_text}]
draft: false
---

## Introduction

{INTRO_TEXT}

## Images

'''

for image_name, content in image_name_content_dict.items():
    image_new_name = list(content.keys())[0]
    image_content = content[image_new_name]
    image_download_url = INPUT_IMG_URL.replace("list_image_files.php", "") + image_name
    image_new_url = IMG_ONLINE_ROOT + image_new_name
    print(image_name)
    print(image_download_url)
    print(image_new_name)
    print(image_new_url)
    print(image_content)
    tag_text = ", ".join(image_content)

    image_md = f'''[![{image_new_url}]({image_new_url})]({image_new_url})  

**{image_new_name}**: {tag_text}.

'''
    # Save image
    response = requests.get(image_download_url, headers=HEADERS)
    with open(os.path.join(OUTPUT_IMG_FOLDER, image_new_name), "wb") as f:
        f.write(response.content)
    # Update blog_md
    blog_md += image_md

# print(blog_md)

with open(os.path.join(os.getcwd(), *OUPUT_FOLDER, f"{config['title'].replace(' ','-')}-{TODAY_DATE}.md"), "w", encoding="utf-8") as f:
    f.write(blog_md)

print("Done!")