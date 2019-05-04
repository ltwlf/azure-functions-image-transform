import logging
import io
import os 

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python meta data HTTP trigger function is processing a request.')

    file = io.open(os.getcwd() + '/swagger.json', 'r')
    swagger = file.read()

    return func.HttpResponse(swagger, status_code=200, mimetype="application/json")
