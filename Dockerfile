#syntax=docker/dockerfile:1.4
FROM nvcr.io/nvidia/pytorch:25.02-py3
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked apt-get update -qq && apt-get install -qqy  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
ENV CFLAGS="-O3 -funroll-loops -fno-strict-aliasing -flto -S"
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /tmp/requirements.txt
ENV CFLAGS=
RUN curl -o /usr/local/bin/pget -L "https://github.com/replicate/pget/releases/latest/download/pget_$(uname -s)_$(uname -m)" && chmod +x /usr/local/bin/pget
RUN pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
WORKDIR /src
EXPOSE 5000 8188
COPY . /src
RUN python scripts/install_custom_nodes.py
CMD ["python", "-m", "cog.server.http"]