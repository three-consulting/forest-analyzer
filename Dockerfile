FROM python:3.10-bullseye

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
        libgdal-dev

RUN groupadd -g 1999 user && useradd --create-home --gid user --uid 1999 user
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

COPY . .

RUN poetry install --no-root --no-interaction

CMD ["poetry", "run", "streamlit", "run", "app/main.py"]