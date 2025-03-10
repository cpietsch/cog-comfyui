#syntax=docker/dockerfile:1.4
#FROM nvcr.io/nvidia/pytorch:25.02-py3
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa

RUN apt install -y google-perftools

RUN apt-get -y update

RUN apt install -y bash \
    build-essential \
    git \
    git-lfs \
    curl \
    ca-certificates \
    libsndfile1-dev \
    libgl1 \
    python3.12 \
    python3-pip \
    python3.12-venv && \
    rm -rf /var/lib/apt/lists


COPY requirements.txt /tmp/requirements.txt
ENV CFLAGS="-O3 -funroll-loops -fno-strict-aliasing -flto -S"
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements.txt
ENV CFLAGS=
RUN curl -o /usr/local/bin/pget -L "https://github.com/replicate/pget/releases/latest/download/pget_$(uname -s)_$(uname -m)" && chmod +x /usr/local/bin/pget
RUN pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
WORKDIR /src
EXPOSE 5000 8188
COPY . /src
#RUN python3 scripts/install_custom_nodes.py
CMD ["python3", "-m", "cog.server.http"]