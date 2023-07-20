# Pull official base image 
FROM python:3.10.0-alpine

# Set working directory
WORKDIR /lama

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-client build-base postgresql-dev git \
    && pip install Pillow
    
# Install dependencies
COPY ./lama/requirements ./requirements
RUN pip install --upgrade pip
RUN pip install -r ./requirements/dev.txt

# Copy entrypoint.sh
COPY ./docker/dev/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY ./lama /lama

ENTRYPOINT [ "/entrypoint.sh" ]