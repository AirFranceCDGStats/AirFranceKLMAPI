FROM sanicframework/sanic:lts-py3.11
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add --no-cache git

COPY . ./AirFranceKLMAPI

WORKDIR /AirFranceKLMAPI

RUN uv sync --frozen

CMD ["uv", "run", "__main__.py"]
