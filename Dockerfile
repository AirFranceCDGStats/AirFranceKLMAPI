FROM sanicframework/sanic:lts-py3.11

RUN apk add --no-cache git

COPY . ./AirFranceKLMAPI

WORKDIR /AirFranceKLMAPI

RUN git submodule update --init --recursive

RUN git submodule foreach git pull origin main

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["python", "__main__.py"]
