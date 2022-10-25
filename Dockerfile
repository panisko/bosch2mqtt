FROM python:latest
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && pip install --upgrade -r requirements.txt && pip install git+https://github.com/bosch-thermostat/bosch-thermostat-client-python.git
COPY src .
CMD [ "python3", "bosch2mqtt.py" ]
