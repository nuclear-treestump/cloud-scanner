# Cloud Resource Scanner

## Overview

The Cloud Resource Scanner (cloudscanner) is a Flask-based application designed to facilitate the security assessment of cloud resources. It provides an interface for uploading JSON files containing resource data (such as EC2 Instances, S3 Buckets, and RDS Instances) and assessing their compliance with predefined security rules.

## Features

- **File Upload Endpoint (`/upload`)**: Allows users to upload JSON files containing detailed descriptions of EC2 Instances, S3 Buckets, and RDS Instances. The endpoint parses the file, validates the JSON structure, and inserts the data into an SQLite database for further processing.
  
- **Resource Evaluation Endpoint (`/api/resources`)**: Offers an interface for querying the database to evaluate cloud resources against a set of security rules. Users can specify the type of resource (EC2, S3, RDS) and a minimum security score to retrieve a filtered list of resources that meet the criteria.

- **SQLite DB**: All entries are stored within a SQLite DB, allowing you to have a historical record. Protections within the handling of `database_ops.py` prevent duplication through `UNIQUE` requirements, and batchloading of data decreases the number of queries and transactions required.

- **Containerized**: The entire project is containerized and ready for deployment through docker / docker-compose.


## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Curl (for testing endpoints)

### Installation and Setup

1. **Locally**
    ```
    git clone https://github.com/nuclear-treestump/cloud-scanner.git
    python -m pip install -r requirements.txt
    cd cloud_scanner
    python -m flask --app app.py run -p 5000
    ```
2. **Through Docker**

    ```
    docker-compose up --build
    ```

    **OR**
    ```
    docker build -t cloudscanner . 
    docker run -d -p 5000:5000 cloudscanner
    ```

## Usage

To insert data into the scanner, send a json file to the `/upload` endpoint.
The data must be in the following format:
```
{
    "EC2Instances": [Array of EC2Object objects],
    "S3Buckets": [Array of S3Bucket objects],
    "RDSInstances": [Array of RDSInstance objects]
}
```
### Example EC2 Instance Object:
```
{
    "GroupId": "sg-groupID"
    "GroupName": "sg-groupName"
    "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 0,
                "ToPort": 0,
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0"
                    }
                ]
            }
        ],
    "Description": "Example Security Group",
    "PublicIp": "8.8.8.8", 
    "PrivateIp": "192.168.0.2"
}
```
### Example S3 Bucket Object:
```
{
    "Name": "bucket_name",
    "CreationDate": "1970-01-01T12:00:00",
    "PublicAccess": false,
    "Encrypted": false,
    "LoggingEnabled": false
}
```
### Example RDS Instance Object:
```
{
    "DBInstanceIdentifier": "db-db_name",
    "DBInstanceClass": "db.class.size",
    "Engine": "ExampleDBSoftware",
    "PubliclyAccessible": false,
    "StorageEncrypted": false,
    "DBPortNumber": 1337,
    "PublicIp": 8.8.8.8,
    "PrivateIp": "192.168.0.2"
}
```
Example Curl Command to upload:

> `curl -X POST -F 'data=@path/to/yourfile.json' http://localhost:5000/upload`

### Expected Response from `/upload` Endpoint:

> ```"Data has been loaded. <number> Items Accepted."```

## Retrieving Results
To retrieve your results from the app, you can query the `/api/resources/` endpoint.
> You can use the following `type` values: `ec2`,`s3`,`rds`. You can also use `min_score` as a filter. `min_score` is not a required field.

>Content Type MUST be application/json. Output will be JSON.

Example curl request to retrieve 'rds' assets with a risk score of 1 or higher.
> `curl -X POST http://localhost:5000/api/resources
-H "Content-Type: application/json"
-d '{"type": "rds", "min_score": 1}'`

Example JSON Payload
```
{
    "type": "rds",
    "min_score": 1
}
```

## What Did and Didn't Work / Lessons Learned
> Within the /unused folder in this repo is a collection of ideas that didn't come to fruition. Some examples include: The entire parsing system I tried to make, rules engine, support for, and processing, of condition expressions, auth through boto3 (had to discard due to no access to a decent sized AWS env). While normally I wouldn't include what I see as 'scratch paper' files, I felt it was an appropriate decision.