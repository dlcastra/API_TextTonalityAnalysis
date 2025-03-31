# Text Tonality Analysis API

## Description

This API allows for text tonality analysis using the library `TextBlob`.
The API supports both direct HTTP requests and requests from Amazon SQS. All requests are processed asynchronously.

Internal services are precessed the file's byte content. As result the API returns dictionary with numerical metrics of
the text tonality and description of each metric.

## Services and Technologies

- Python 3.13
- FastAPI
- TextBlob
- Docker
- Docker Compose
- AWS S3, SQS, IAM
- Google Translate API

## How It Works

### Direct Request Flow:

1. The endpoint receives the request and forwards the data to the handler.
2. The handler fetches the file's byte code.
3. The data is passed to `TextTonalityAnalysisService`.
4. The service processes the file's bytes and returns the result to the handler.
5. The handler sends the response back to the router function(endpoint).
6. The endpoint forwards the result to the specified callback URL.

### SQS Queue Request Flow:

1. A function inside the service checks whether there is data in the queue.
2. If data is found, the function sends the data to the handler, otherwise the function waits 0.5 seconds and checks the
   queue again.
3. The handler fetches the file's byte code and passes it to `TextTonalityAnalysisService`.
4. The service processes the file's bytes and returns the result to the handler.
5. The handler returns the result in SQS handler.
6. The result is sent to the callback URL.

## API Endpoints

### Analyze Text Endpoint

- **URL:** `api/v1/analysis/tonality/`
- **Method:** `POST`
- **Supported Formats:** `txt`, `docx`, `pdf`
- **Request Body Example:**
  ```json
  {
      "s3_key": "some_file.txt",
      "callback_url": "https://webhook/mywebhook"
  }
  ```

## Example API Responses

### Successful Response

- **api/v1/analysis/tonality**
- **Status Code:** 201
  ```json
  {
      "polarity": 0.1288487559411474,
      "subjectivity": 0.45834842106581275,
      "objective_sentiment_score": 0.15333648129278898,
      "polarity_status": "Positive",
      "polarity_description": "Slightly positive tone.",
      "subjectivity_status": "Mixed",
      "subjectivity_description": "A mix of subjective and objective statements.",
      "objective_sentiment_status": "Rather subjective opinion",
      "objective_sentiment_description": "The sentiment is present but leans more toward subjectivity.",
      "s3_key": "some_file.txt",
      "status": "success"
  }
  ```

### Error Response

- **api/v1/analysis/tonality**
- **Status Code:** 400
  ```json
  {
      "detail": "Unsupported file format.",
      "status": "error"
  }
  ```

- **api/v1/analysis/tonality**
- **Status Code:** 500
  ```json
  {
      "detail": "Internal server error.",
      "status": "error"
  }
  ```
  
## How to Run the API

### Run with Docker:
1. Clone the repository:
    ```sh
    git clone https://github.com/dlcastra/API_TextTonalityAnalysis.git
    ```
2. Configure environment variables in the `.env` file (use `.env.ex` as an example).
3. Build and start the containers:
   ```sh
   docker-compose up --build
   ```

### Run Locally:
1. Clone the repository:
    ```sh
    git clone https://github.com/dlcastra/API_TextTonalityAnalysis.git
    ```
2. Configure environment variables in the `.env` file (use `.env.ex` as an example).
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the application:
   ```sh
   uvicorn application:app --reload --port 8000
   ```   

## Error Handling
- If the file is not found in S3, an appropriate error response is returned.
- If the file format is not supported, the request is rejected with a descriptive error message.
- If an unexpected error occurs, a generic error response is sent, and logs are generated for debugging.