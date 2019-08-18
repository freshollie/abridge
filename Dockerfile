FROM python:3.7.3 as build

WORKDIR /build
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev
RUN make build

FROM python:3.7.3
LABEL maintainer="Oliver Bell <freshollie@gmail.com>"

WORKDIR /abridge

COPY --from=build /build/dist/*.whl ./
RUN pip install *.whl

ENTRYPOINT [ "abridge" ]
