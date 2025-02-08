import json
import os
import requests
from flask import Flask
from flask import request
from threading import Thread
import constant


server_config = {
    constant.CONFIG_URL: constant.EMPTY_STR,
    constant.CONFIG_TOKEN: constant.EMPTY_STR,
    constant.CONFIG_IMSDK_NAME: constant.EMPTY_STR,
    constant.CONFIG_USERNAME: constant.EMPTY_STR,
    constant.CONFIG_SEND_METHOD: None
}


def init_http_server(fn_send_msg_to_admin):
    host = os.getenv(constant.ENV_HOST)
    port = os.getenv(constant.ENV_PORT)
    prefix = os.getenv(constant.ENV_PREFIX)
    username = os.getenv(constant.ENV_USERNAME)
    if prefix is None:
        prefix = constant.EMPTY_STR
    url = constant.TEMPLATE_URL % (host, port, prefix)
    token = os.getenv(constant.ENV_TOKEN)
    imsdk_name = os.getenv(constant.ENV_IMSDK_NAME)
    server_config[constant.CONFIG_URL] = url
    server_config[constant.CONFIG_TOKEN] = token
    server_config[constant.CONFIG_IMSDK_NAME] = imsdk_name
    server_config[constant.CONFIG_USERNAME] = username
    server_config[constant.CONFIG_SEND_METHOD] = fn_send_msg_to_admin
    app = Flask(constant.FLASK_APP_NAME, static_folder=constant.FLASK_STATIC_FOLDER)
    @app.post(constant.FLASK_URL_IMSDK)
    def on_request():
        _token = request.headers.get(constant.PARAMS_TOKEN)
        name = request.json.get(constant.PARAMS_NAME)
        target = request.json.get(constant.PARAMS_TARGET)
        data = request.json.get(constant.PARAMS_DATA)
        if _token != server_config[constant.CONFIG_TOKEN]:
            resp = {
                constant.PARAMS_CODE: constant.ERROR_CODE_INVALID_TOKEN,
                constant.PARAMS_MESSAGE: constant.ERROR_MESSAGE_INVALID_TOKEN
            }
            return json.dumps(resp)
        if target != server_config[constant.CONFIG_IMSDK_NAME]:
            resp = {
                constant.PARAMS_CODE: constant.ERROR_CODE_INVALID_TARGET,
                constant.PARAMS_MESSAGE: constant.ERROR_MESSAGE_INVALID_TARGET
            }
            return json.dumps(resp)
        fn_send_msg_to_admin(constant.FROM
                             + constant.WHITE_SPACE
                             + name
                             + constant.COLON
                             + constant.NEWLINE
                             + data)
        resp = {
            constant.PARAMS_CODE: constant.ERROR_CODE_SUCCESS,
            constant.PARAMS_MESSAGE: constant.ERROR_MESSAGE_SUCCESS
        }
        return json.dumps(resp)
    Thread(target=app.run,
           kwargs={
               constant.CONFIG_HOST: constant.FLASK_HOST,
               constant.CONFIG_PORT: constant.FLASK_PORT
           },
           daemon=True).start()


def send_request(target, data):
    res = requests.post(server_config[constant.CONFIG_URL], json={
        constant.PARAMS_TARGET: target,
        constant.PARAMS_NAME: server_config[constant.CONFIG_IMSDK_NAME],
        constant.PARAMS_DATA: data
    }, headers={
        constant.PARAMS_TOKEN: server_config[constant.CONFIG_TOKEN],
        constant.PARAMS_USERNAME: server_config[constant.CONFIG_USERNAME]
    })
    resp = json.loads(res.text)
    if (resp[constant.PARAMS_CODE] != constant.ERROR_CODE_SUCCESS
            and server_config[constant.CONFIG_SEND_METHOD] is not None):
        server_config[constant.CONFIG_SEND_METHOD](resp[constant.PARAMS_MESSAGE])
