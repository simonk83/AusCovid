# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.7.4

EXPOSE 5000
# RUN apt-get update -y && \
    # apt-get install -y python-pip python-dev
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]