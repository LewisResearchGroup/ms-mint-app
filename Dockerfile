FROM python:3.10
EXPOSE 9999

RUN mkdir -p /data

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

RUN pip3 list

COPY . /app

WORKDIR /app

RUN pip3 install .

ENV SQLALCHEMY_DATABASE_URI sqlite:///data/mint.db

ENV MINT_DATA_DIR /data/

CMD chmod +x entrypoint.sh && ./entrypoint.sh

