FROM python:3.10-bullseye

RUN groupadd -g 1999 user && useradd --create-home --gid user --uid 1999 user

RUN apt-get update \ 
    && apt-get install -y build-essential --no-install-recommends make \
        ca-certificates \
        git \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncurses5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        sqlite3 \
        libsqlite3-mod-spatialite \
        gdal-bin \
        libgdal-dev && \
        rm -rf /var/lib/apt/lists/*

ARG HOME="/home/user"
ARG PYTHON_VERSION=3.10

ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${HOME}/.local/bin:$PATH"
ENV PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions=yes"

RUN echo "done 0" \
    && curl https://pyenv.run | bash \
    && echo "done 1" \
    && pyenv install ${PYTHON_VERSION} \
    && echo "done 2" \
    && pyenv global ${PYTHON_VERSION} \
    && echo "done 3" \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.in-project true

WORKDIR /app

COPY pyproject.toml /app
COPY poetry.lock /app

RUN chown -R user:user /app
RUN chown -R user:user /home/user/.config/pypoetry

RUN poetry install --no-root --no-interaction

COPY . /app/

USER user

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["poetry", "run", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
