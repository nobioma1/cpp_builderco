# CPP_Builderco

## Overview

A Django project utilizing AWS resources for scalability of hosting, storage and processing resources

## Prerequisites

- Python >= 3.12.0
- AWS (RDS, S3)

## Installation

- Clone the Repository

    ```bash
      git clone https://github.com/noble-cc/cpp_builderco.git
      cd cpp_builderco
    ```

- Set Up a Virtual Environment

  ```bash
    python -m venv venv
    source venv/bin/activate
  ```

- Install Dependencies
  ```bash
    pip install -r requirements.txt
  ```

## Configuration

- Create a PostgreSQL Database instance

- Create an S3 bucket and update the `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_BUCKET_REGION` in the `settings.py` file or run
  command:

  ```bash
    python manage.py create_s3_bucket --name <bucket-name> --region <bucket-region> --enable_versioning
  ```

## Running the Project

- Create `.env` file on the root directory, and environment variables [(Env Sample File)](./.env.sample)
- Run migrations

  ```bash
    python manage.py migrate
  ```

- Start Django project:

  ```bash
    python manage.py runserver
  ```

