FROM python:3.8-alpine

WORKDIR /app 

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD ["view.py"]

