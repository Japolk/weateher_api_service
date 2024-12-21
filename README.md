# Weather API Service

Asynchronous weather data service built with FastAPI.
Features throttled API calls to OpenWeather, S3 caching, and DynamoDB logging.


## AWS Setup Requirements
**S3 Bucket:** Create S3 bucket for weather data caching

**DynamoDB** Table with Partition key: id

Create AWS credentials with access to S3 Bucket and DynamoDB

## openweather requirements
**API key** Create API key to access API

Depending on the subscription level, openweather API has a different allowed number of requests per minute
free tier provides 60 requests per minute. 

Weather API project makes 2 requests to find city weather. 1st - to obtain coordinates,  2nd - to find weather by coodrintaes

## Environment Setup

Create `.env` file with the following configurations:

```env
# OpenWeather API
OPENWEATHER_API_KEY=your_api_key
MAX_CALLS_PER_MIN=60

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
S3_BUCKET_NAME=your_bucket_name
DYNAMODB_TABLE=your_table_name

# Cache Configuration
CACHE_EXPIRY_MINUTES=5
```

## Run application
1. Obtain openweather API key
2. Create S3 bucket, DynamoDB table with Partition key: id
3. Obtain aws credentials with access to the services above
4. Create .env file in the project root. Can be copied from .env.example
5. Start application with Docker Compose:

```bash
docker compose up
```


## Local Development

Start the development server:
```bash
uvicorn src.main:app --reload
```

Access the API documentation:
```bash
http://localhost:8000/docs
```

