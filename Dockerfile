FROM mcr.microsoft.com/azure-functions/python:2.0

COPY . /home/site/wwwroot

ENV AzureFunctionsJobHost__Logging__Console__IsEnabled=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgtk2.0

RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt