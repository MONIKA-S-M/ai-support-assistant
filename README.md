# AI Support Ticket Assistant

An AI-powered support ticket analysis system that allows users to ask natural-language questions about support tickets, analyze ticket statistics, and detect anomalous tickets through an interactive web interface.

---

## Features

- Natural-language question answering for support tickets
- LLM-based intent classification using Ollama
- Deterministic data analysis using Pandas
- Ticket statistics and category/priority/status breakdowns
- Priority-specific and status-specific queries
- Anomaly detection for unusual support tickets
- REST API built with FastAPI
- Interactive web interface built with Streamlit
- Swagger API documentation
- Local LLM inference using Llama 3.2 3B

---

## System Architecture

```text
                    support_tickets.csv
                           |
                           v
                    +--------------+
                    | Data Loader  |
                    |   Pandas     |
                    +--------------+
                           |
                           v
                  +------------------+
                  |   Query Engine   |
                  +------------------+
                     |            |
                     |            |
                     v            v
               Ollama LLM    Pandas Analysis
               Intent        Actual Data
               Detection     Calculation
                     |            |
                     +-----+------+
                           |
                           v
                     +-----------+
                     |  FastAPI  |
                     | REST API  |
                     +-----------+
                           |
                           v
                    +--------------+
                    |  Streamlit   |
                    |      UI      |
                    +--------------+

                    Anomaly Detector
                           |
                           v
                    Detected Anomalies
```

### Design Approach

The LLM is used primarily to understand and classify the user's natural-language question.

The actual numerical calculations are performed using Pandas on the CSV dataset. This reduces the risk of the LLM generating or hallucinating incorrect statistics.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10 | Core programming language |
| Pandas | Data loading and analysis |
| FastAPI | REST API |
| Uvicorn | FastAPI server |
| Streamlit | Web interface |
| Ollama | Local LLM runtime |
| Llama 3.2 3B | Natural-language intent classification |
| Requests | Communication between UI and API |

---

## Dataset

The application uses:

```text
data/support_tickets.csv
```

The dataset contains 500 support tickets with the following fields:

```text
ticket_id
created_at
category
priority
status
response_time_hrs
resolution_time_hrs
agent_id
customer_rating
issue_summary
```

### Data Handling

The `created_at` column is converted to a datetime format during data loading.

Missing values in `resolution_time_hrs` and `customer_rating` are preserved. Pandas aggregation functions naturally ignore missing values when calculating averages.

---

## Supported Natural-Language Queries

The application supports questions such as:

```text
How many tickets are currently open?
```

```text
How many tickets are there in total?
```

```text
What is the average customer rating?
```

```text
What is the average resolution time?
```

```text
How many tickets are in each category?
```

```text
How many Technical tickets are there?
```

```text
How many tickets are there by priority?
```

```text
How many Critical tickets are there?
```

```text
How many High priority tickets are there?
```

```text
How many Medium priority tickets are there?
```

```text
How many Low priority tickets are there?
```

```text
How many tickets are there by status?
```

```text
How many tickets are resolved?
```

```text
How many tickets are escalated?
```

```text
Which agent resolved the most tickets?
```

The system also supports general questions about the support-ticket system through the LLM.

---

## LLM Integration

The application uses Ollama with the local model:

```text
llama3.2:3b
```

The LLM classifies natural-language questions into predefined intents such as:

```text
open_tickets
total_tickets
average_rating
average_resolution
by_category
by_priority
by_status
top_agent
general
```

After intent detection, the application uses the corresponding Pandas-based function to calculate the requested result.

### Example

For:

```text
How many Critical tickets are there?
```

The system identifies the priority-related query and uses Pandas to calculate the actual count from the dataset.

The resulting answer is:

```text
There are 55 Critical tickets.
```

---

## Anomaly Detection

The application includes an anomaly detection module located at:

```text
app/anomaly_detector.py
```

Two anomaly conditions are currently checked.

### 1. Critical Unresolved Tickets

The system identifies High-priority tickets that:

- Are not resolved
- Are older than 24 hours based on their created_at timestamp

### 2. Unusually Long Resolution Times

The system calculates the 95th percentile of `resolution_time_hrs`.

Tickets with a resolution time above this threshold are flagged as anomalies.

Detected anomalies include:

- Ticket ID
- Anomaly type
- Relevant details

---

## REST API

The backend is implemented using FastAPI.

### Start the API

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Endpoints

### Health Check

```text
GET / health
```

Returns the API status.

---

### Ticket Summary

```text
GET /tickets/summary
```

Returns:

- Total tickets
- Open tickets
- Average customer rating
- Average resolution time
- Top resolving agent

Example response:

```json
{
    "total_tickets": 500,
    "open_tickets": 111,
    "average_customer_rating": 3.75,
    "average_resolution_time_hrs": 19.16,
    "top_resolving_agent": "AGT-09"
}
```

---

### Tickets by Category

```text
GET /tickets/by-category
```

Example response:

```json
{
    "General": 189,
    "Billing": 159,
    "Technical": 152
}
```

---

### Tickets by Priority

```text
GET /tickets/by-priority
```

Example response:

```json
{
    "Medium": 169,
    "Low": 142,
    "High": 134,
    "Critical": 55
}
```

---

### Tickets by Status

```text
GET /tickets/by-status
```

Example response:

```json
{
    "Resolved": 327,
    "Open": 111,
    "Escalated": 62
}
```

---

### Anomaly Detection

```text
GET /anomalies
```

Returns the number of detected anomalies and their details.

Example structure:

```json
{
    "count": 17,
    "anomalies": [
        {
            "ticket_id": "TKT-023",
            "type": "Long resolution time",
            "details": "Resolution time of 76.1 hours"
        }
    ]
}
```

---

### Natural-Language Query

```text
GET /ask
```

Example:

```text
/ask?question=How many Low priority tickets are there?
```

Example response:

```json
{
    "question": "How many Low priority tickets are there?",
    "answer": "There are 142 Low priority tickets."
}
```

---

## Swagger API Documentation

FastAPI automatically provides interactive API documentation.

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface can be used to test all API endpoints.

---

## Streamlit User Interface

The frontend is implemented using Streamlit.

The interface provides:

### Natural-Language Query Section

Users can enter questions such as:

```text
How many Low priority tickets are there?
```

and receive the answer through the FastAPI backend.

### Anomaly Detection Section

Users can click:

```text
Check Anomalies
```

to retrieve and display detected anomalies.

---

## Running the Streamlit Application

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Start Streamlit:

```powershell
streamlit run streamlit_app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Installation

### 1. Clone or open the project

```powershell
cd D:\ai-support-assistant
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 5. Install Ollama

Install Ollama separately and make sure it is available on the system.

### 6. Pull the required LLM

```powershell
ollama pull llama3.2:3b
```

### 7. Start the FastAPI backend

```powershell
uvicorn app.main:app --reload
```

### 8. Start the Streamlit frontend

Open another terminal, activate the virtual environment, and run:

```powershell
streamlit run streamlit_app.py
```

---

## Project Structure

```text
ai-support-assistant/
│
├── app/
│   ├── main.py
│   ├── data_loader.py
│   ├── query_engine.py
│   └── anomaly_detector.py
│
├── data/
│   └── support_tickets.csv
│
├── venv/
│
├── check_data.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

## Key Python Modules

### `app/data_loader.py`

Responsible for:

- Loading the CSV dataset
- Converting `created_at` into datetime format
- Preparing the DataFrame for analysis

---

### `app/query_engine.py`

Responsible for:

- Ticket statistics
- Category analysis
- Priority analysis
- Status analysis
- Agent analysis
- LLM-based intent classification
- Natural-language question handling

---

### `app/anomaly_detector.py`

Responsible for:

- Detecting critical unresolved tickets with high response times
- Detecting unusually long resolution times
- Returning anomaly details

---

### `app/main.py`

Responsible for:

- Creating the FastAPI application
- Exposing REST API endpoints
- Connecting the query engine and anomaly detector to the API

---

### `streamlit_app.py`

Responsible for:

- Providing the web interface
- Accepting natural-language questions
- Displaying answers
- Displaying detected anomalies
- Communicating with the FastAPI backend

---

## Example Dataset Results

For the provided dataset, the application currently produces the following results:

| Metric | Result |
|---|---:|
| Total tickets | 500 |
| Open tickets | 111 |
| Resolved tickets | 327 |
| Escalated tickets | 62 |
| Average customer rating | 3.75 |
| Average resolution time | 19.16 hours |
| Detected anomalies | 97 |
| Top resolving agent | AGT-09 |

### Category Distribution

```text
General     : 189
Billing     : 159
Technical   : 152
```

### Priority Distribution

```text
Medium      : 169
Low         : 142
High        : 134
Critical    : 55
```

### Status Distribution

```text
Resolved    : 327
Open        : 111
Escalated   : 62
```

---

## Example End-to-End Flow

A user enters:

```text
How many Critical tickets are there?
```

The flow is:

```text
User Question
      |
      v
Streamlit UI
      |
      v
FastAPI /ask Endpoint
      |
      v
Query Engine
      |
      v
LLM Intent Classification
      |
      v
Priority Query
      |
      v
Pandas Data Analysis
      |
      v
55 Critical Tickets
      |
      v
Response to User
```

---

## Design Principles

### LLM for Understanding

The LLM is used to understand the intent of natural-language questions.

### Python/Pandas for Computation

Actual ticket statistics are calculated from the dataset using Python and Pandas rather than relying on the LLM to generate numerical answers.

### API Separation

The FastAPI backend separates the data-processing layer from the user interface.

### Simple and Modular Architecture

The application is divided into separate modules for:

- Data loading
- Query processing
- Anomaly detection
- API handling
- User interface

This makes the system easier to maintain and extend.

---

## Known Limitations

- The system currently uses a fixed CSV dataset and does not connect to a live ticketing system.
- The LLM runs locally using Ollama and requires the Llama 3.2 3B model to be available.
- Anomaly detection uses rule-based and statistical thresholds that may require tuning for different datasets.
- The current system is designed for the provided support-ticket dataset and may need additional query handling for unsupported question types.

## Future Improvements

Possible future improvements include:

- Date-based filtering such as daily, weekly, and monthly analysis
- More advanced anomaly detection techniques
- Additional natural-language query types
- Interactive charts and dashboards
- Authentication and authorization
- Database integration instead of CSV storage
- Production deployment
- More advanced LLM models
- Conversation history and contextual follow-up questions

---

## Conclusion

The AI Support Ticket Assistant combines an LLM with deterministic data analysis to provide a natural-language interface for support ticket analytics.

The system demonstrates:

- LLM integration
- Data analysis with Pandas
- Anomaly detection
- REST API development
- Streamlit UI development
- Modular Python architecture

The application can be run locally using FastAPI, Streamlit, and Ollama.
