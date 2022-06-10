FROM python:3.9
EXPOSE 9999

RUN mkdir -p /data

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app

RUN pip3 install .

ENV SQLALCHEMY_DATABASE_URI sqlite:///data/mint.db

ENV MINT_DATA_DIR /data/

CMD ./entrypoint.sh

