# First stage will only be used to install Poetry and to generate the requirements.txt
# with your project dependencies from Poetry's pyproject.toml file.
FROM python:3.9 as requirements-stage

# Set /tmp as the current working directory.
# Here's where we will generate the file requirements.txt
WORKDIR /tmp

# Install Poetry in this Docker stage.
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files to the /tmp directory.
# Because it uses ./poetry.lock* (ending with a *), it won't crash if that file is not available yet.
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Generate the requirements.txt file. This requirements.txt file will be used with pip later in the next stage.
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# This is the final stage, anything here will be preserved in the final container image.
FROM python:3.9

# Set the current working directory to /code.
WORKDIR /code
ENV PYTHONPATH="/code"

ENV USER user
ENV USER_ID 1001
RUN useradd -m ${USER} -u ${USER_ID}

# Copy the requirements.txt file to the /code directory.
# This file only lives in the previous Docker stage, that's why we use --from-requirements-stage to copy it.
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# Install the package dependencies in the generated requirements.txt file.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app directory to the /code directory.
COPY ./app /code/app
RUN chown -R ${USER} /code

# ensure container runs as non-root.
USER ${USER_ID}

# Run the main.py script using python
CMD ["python", "app/main.py"]
