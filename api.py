#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/2/3
# IDE: PyCharm

## flask run --host=0.0.0.0 --port=6739
## curl http://0.0.0.0:6739/?image_path=/root/CrawlerBackend/download/avatar/bb2ecb28-306a-11ea-b19d-00155d07b703.jpg
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)

from ns4w.classifier import classify_image
from flask import Flask
from flask import request
import os
import requests

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def classifier():
    if request.method == 'POST':
        image_path = request.form.get('image_path', None)
        image_url = request.form.get('image_url', None)
    else:
        image_path = request.args.get('image_path', None)
        image_url = request.args.get('image_url', None)
    if image_path:
        if os.path.exists(image_path):
            sfw, nsfw = classify_image(image_path=image_path)
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "sfw": sfw,
                    "nsfw": nsfw,
                }
            }
        else:
            return {
                "code": 401,
                "message": "image_path does not exist",
                "data": None
            }
    elif image_url:
        response = requests.get(image_url)
        status_code = response.status_code
        if status_code >= 400:
            return {
                "code": 402,
                "message": "image_url \n"
                           "'{image_url}' \n"
                           "cannot be accessed".format(image_url=image_url),
                "data": None
            }
        else:
            try:
                sfw, nsfw = classify_image(response=response)
            except OSError:
                return {
                    "code": 403,
                    "message": "image_url \n"
                               "'{image_url}' \n"
                               "is not an image file".format(image_url=image_url),
                    "data": None
                }
            else:
                return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "sfw": sfw,
                        "nsfw": nsfw,
                    }
                }

    else:
        return {
            "code": 400,
            "message": "image_path does not provided",
            "data": None
        }
