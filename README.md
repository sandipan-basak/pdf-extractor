# PDF Extractor for RBI Notifications

## Overview

The PDF Extractor is a specialized tool designed to automate the extraction of PDF documents from the Reserve Bank of India's notification website. Starting from a specified year, it navigates through the site, identifies PDF documents, and downloads them to a local storage path. This tool is fully containerized, ensuring a consistent and isolated environment for running the extraction process.

## Prerequisites

- Docker
- A `.env` file configured with necessary paths and settings.

## Configuration

Before running the application, ensure you have a `.env` file in the project root with the following configurations:

```env
CHROMEDRIVER_PATH=/usr/bin/chromedriver
PDF_STORAGE_PATH=/usr/src/app/data
START_YEAR=2024
YEAR_RANGE=1
```

This configuration sets up the path to the ChromeDriver, specifies the storage location for downloaded PDFs, and defines the starting year and range for PDF extraction.

## Building the Docker Image
To build the Docker image for the PDF Extractor, navigate to the root directory of the project and execute:

```sh
docker build -t pdf-extractor .
```
This command builds a Docker image named pdf-extractor based on the provided Dockerfile.

## Running the Application
After building the image, run the application with Docker using the following command:

```sh
docker run --env-file ./.env -v $(pwd)/data:/usr/src/app/data --name pdf-extractor-instance pdf-extractor
```

This command runs the PDF Extractor in a container, utilizing the environment variables defined in the .env file. It also mounts a volume from the host's current directory to the container, ensuring that extracted PDFs are saved to the host machine for easy access.

## Customization

To customize the extraction process, such as changing the starting year or the range of years for PDF extraction, simply adjust the START_YEAR and YEAR_RANGE values in the .env file before running the container.

## Note
Ensure that the specified CHROMEDRIVER_PATH and PDF_STORAGE_PATH are accessible and correct within the Docker container's environment. The default paths are set for a Dockerized application; adjust them only if necessary to accommodate your specific setup.




