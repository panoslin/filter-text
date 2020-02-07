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
import sanic.exceptions
from filter import DFAFilter


app = Sanic()
app.config.KEEP_ALIVE = True
app.config.KEEP_ALIVE_TIMEOUT = 500
app.config.RESPONSE_TIMEOUT = 500
CORS(app, automatic_options=True)

@app.route("/")
async def test(request):
    return Response.json({ "hello": "world" })

def get_post_args(request, key, default=None):
    data = request.json.get(key, default)
    if not data:
        data =request.form.get(key, default)
    return data


@app.route(uri='/filter-text', methods=['GET', 'POST'], name='filter')
async def filter_text(request):
    if request.method == "GET":
        text = request.args.get("text")
        repl = request.args.get("repl", "*")
    else:
        text = get_post_args(request, "text")
        repl = get_post_args(request, "repl", "*")
    if not text:
        return Response.json(
            {"code": 400,
             "message": "You should specify necessary params `text`",
             "data": None}
        )
    else:
        gfw = DFAFilter()
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


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=9974,
            workers=2,
            debug=True,
            access_log=True,
            strict_slashes=False,
            )
