# abridge

[![pipeline status](https://gitlab.com/freshollie/abridge/badges/master/pipeline.svg)](https://gitlab.com/freshollie/abridge/commits/master)
[![coverage report](https://gitlab.com/freshollie/abridge/badges/master/coverage.svg)](http://freshollie.gitlab.io/abridge)
[![PyPI version](https://img.shields.io/pypi/v/abridge)](https://badge.fury.io/py/abridge)
[![](https://images.microbadger.com/badges/image/freshollie/abridge.svg)](https://microbadger.com/images/freshollie/abridge)
[![](https://images.microbadger.com/badges/version/freshollie/abridge.svg)](https://microbadger.com/images/freshollie/abridge)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Effortlessly shorten videos.

## About

`abridge` can automatically shorten video files by removing parts from the video
where not much happens. This is great for making timelapse videos more engaging
and removes the need for manual editing to cut these dead spots from the videos.

## Installation

`pip install abridge`

`abridge` makes use of `moviepy`, which releys on `ffmpeg`. `ffmpeg` should be installed
when the package is installed, but this may not work on some systems.

## Docker

`adbridge` can be run as a docker image, which gaurentees it will run
on all systems.

`docker pull freshollie/abridge:latest`

`docker run freshollie/abridge`

## Usage

```
usage: abridge [-h] [-w workers] [-o outdir] [-t diff-threshold]
               [-r repetition-threshold]
               clip [clip ...]

Effortlessly shorten videos

positional arguments:
  clip                  Clip to cut or glob group

optional arguments:
  -h, --help            show this help message and exit
  -w workers            Number of clip processors
  -o outdir
  -t diff-threshold     Difference threshold required between frames for a
                        frames to be considered different
  -r repetition-threshold
                        Number of frames in a row required to make a cut
```

## Api

```python
from abridge import abridge_clip

abridge_clip("/path/to/clip")
```

## Developing

The `abridge` project is managed and packaged by `poetry`

Use `poetry install` to download the required packages for development

`poetry run pre-commit install` should be run to install the pre-commit
scripts which help with ensuring code is linted before push.

### Tests

Tests are written with `pytest` and can be run with `make test`

### Linting

`abridge` is linted with `pylint` and formatted with `black` and `isort`

`mypy` is used throughout the project to ensure consitent types.

`make lint` will check linting, code formatting, and types

`make format` will format code to required standards

## TODO:

- Test coverage on processor

## License

`MIT`
