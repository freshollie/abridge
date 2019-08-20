FROM python:3.7.3 as build

WORKDIR /build
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev
COPY README.md README.md
COPY abridge abridge

RUN poetry build

FROM python:3.7.3-alpine3.10
LABEL maintainer="Oliver Bell <freshollie@gmail.com>"

WORKDIR /abridge

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev jpeg-dev zlib-dev ffmpeg
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

COPY --from=build /build/dist/*.whl ./
RUN pip install --no-cache-dir *.whl
RUN rm *.whl

ENTRYPOINT [ "abridge" ]
