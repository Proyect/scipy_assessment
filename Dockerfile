# Use a specific Python base image version
FROM python:3.8-slim-buster

# Set work directory
WORKDIR /usr/src/app

COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install specific versions of setuptools and wheel
RUN pip install --no-cache-dir --upgrade pip
# RUN pip install --no-cache-dir setuptools==59.6.0 wheel

# Install Python dependencies
RUN pip install --no-cache-dir numpy==1.17.3 cython==0.29.33 pytest

# Install scipy dependencies
RUN pip install --no-cache-dir pybind11

# Install nose (required for some decorators)
RUN pip install --no-cache-dir nose

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Modify setup.py to fix the version issue
RUN sed -i 's/ISRELEASED = False/ISRELEASED = True/' setup.py

# Modify setup.py to remove test_suite option
RUN sed -i '/test_suite/d' setup.py

# Install scipy in editable mode with verbose output
RUN pip install --no-use-pep517 -e . -v

# Remove pytest.ini if it exists (to avoid config issues)
RUN rm -f pytest.ini

# Run specified test
CMD pytest -v -rA --tb=long -p no:cacheprovider --disable-warnings \
    scipy/sparse/tests/test_base.py
