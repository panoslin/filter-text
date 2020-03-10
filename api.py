#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/2/7
# IDE: PyCharm

## add current path to system path temporary
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)

from sanic import response as Response
from sanic import Sanic
from sanic_cors import CORS
from filter import (
    DFAFilter,
    BSFilter,
)

app = Sanic()
app.config.KEEP_ALIVE = True
app.config.KEEP_ALIVE_TIMEOUT = 500
app.config.RESPONSE_TIMEOUT = 500
CORS(app, automatic_options=True)


@app.route("/")
async def test(request):
    return Response.json({"hello": "world"})

def get_post_args(request, key, default=None):
    try:
        data = request.json.get(key, default)
    except AttributeError:
        data = request.form.get(key, default)
    return data


@app.route(uri='/filter-text', methods=['GET', 'POST'], name='filter')
async def filter_text(request):
    if request.method == "GET":
        text = request.args.get("text")
        repl = request.args.get("repl", "*")
        algorithm = request.args.get("algorithm", "bs")
    else:
        text = get_post_args(request, "text")
        repl = get_post_args(request, "repl", "*")
        algorithm = get_post_args(request, "algorithm", "bs")
    if not text:
        return Response.json(
            {"code": 400,
             "message": "You should specify necessary params `text`",
             "data": None}
        )
    else:
        gfw = DFAFilter() if algorithm == "dfa" else BSFilter()
        gfw.parse("filter/keywords")

        result = gfw.filter(message=text, repl=repl)

        return Response.json(
            {
                "code": 200,
                "message": "success",
                "data": {
                    "result": result
                }
            }
        )


@app.route(uri='/match-text', methods=['GET', 'POST'], name='match')
async def match_text(request):
    if request.method == "GET":
        text = request.args.get("text")
        algorithm = request.args.get("algorithm")
        keywords = request.args.get("keywords")
    else:
        text = get_post_args(request, "text")
        algorithm = get_post_args(request, "algorithm", "bs")
        keywords = get_post_args(request, "keywords")
    if not text:
        return Response.json(
            {"code": 400,
             "message": "You should specify necessary params `text`",
             "data": None}
        )
    else:
        gfw = DFAFilter() if algorithm == "dfa" else BSFilter()
        if keywords:
            for ele in keywords:
                gfw.add(ele)
        else:

            gfw.parse("filter/keywords")

        result = list(gfw.match(message=text))

        return Response.json(
            {
                "code": 200,
                "message": "success",
                "data": {
                    "result": result
                }
            }
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=9974,
            workers=2,
            debug=True,
            access_log=True,
            strict_slashes=False,
            )
