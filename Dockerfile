FROM python:3.11
EXPOSE 9999

ENV SQLALCHEMY_DATABASE_URI sqlite:///data/mint.db

ENV MINT_DATA_DIR /data/

RUN mkdir -p /data

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . /app

RUN cd /app && pip3 install -e .

WORKDIR /app

CMD chmod +x entrypoint.sh && ./entrypoint.sh

