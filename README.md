# COMP3041J-cloud-project1
Cloud Execution Models Mini Project - Campus Buzz System

## Project Overview
This project implements a small cloud-native application based on a **hybrid execution model**, combining **container-based services** and **serverless functions**.

The system allows users to submit campus events, automatically processes submissions in the background, and returns a final result including:
- Status (APPROVED / NEEDS REVISION / INCOMPLETE)
- Category (OPPORTUNITY / ACADEMIC / SOCIAL / GENERAL)
- Priority (HIGH / MEDIUM / NORMAL)

---

## System Architecture

The system follows an **event-driven workflow**:

User → Presentation Service → Workflow Service → Data Service  
→ Submission Event Function → Processing Function → Result Update Function  
→ Data Service → Presentation Service (Result Display)

### Components
**Container Services:**
- Presentation Service
- Workflow Service
- Data Service  

**Serverless Functions:**
- Submission Event Function
- Processing Function
- Result Update Function  


---

## Component Responsibilities

### Presentation Service (`presentation_service.py`)
- Handles user interaction via web interface  
- Accepts form submissions  
- Sends data to Workflow Service  
- Displays final results  

---

### Workflow Service (`workflow_service.py`)
- Creates initial submission record  
- Sends data to Data Service  
- Triggers Submission Event Function  

---

### Data Service (`data_service.py`)
- Stores all submission records  
- Provides APIs for read/write operations  
- Maintains system state  

---

### Submission Event Function (`campus-submission.py`)
- Triggered after a new submission is created  
- Converts submission into a processing request  
- Invokes Processing Function  

---

### Processing Function (`campus-processing.py`)
- Core business logic of the system  
- Performs:
  - Required field validation  
  - Date format validation  
  - Description length check  
  - Category classification (keyword-based)  
  - Priority assignment  
- Produces final result  

---

### Result Update Function (`campus-update.py`)
- Updates processed results in Data Service  
- Ensures consistency between processing output and stored data  

---

## Workflow Description

1. User submits an event via the web interface  
2. Presentation Service sends request to Workflow Service  
3. Workflow Service creates a record in Data Service  
4. Submission Event Function is triggered  
5. Processing Function validates and processes data  
6. Result Update Function updates the record  
7. User views the final result  

---

## How to Run the Project

### Option 1: Access Deployed Version (Recommended)
The application has been deployed on a cloud server and is continuously running.

You can directly access it via:

http://8.136.153.80:5000

No local setup is required.

---

## Testing

Sample test cases are provided in:

- `Test events.pdf`

You can verify the system using the following scenarios:

- Missing required fields → **INCOMPLETE**  
- Invalid date format → **NEEDS REVISION**  
- Description shorter than 40 characters → **NEEDS REVISION**  
- Valid input → **APPROVED**

---

## Technologies Used

- Python (Flask)  
- Docker & Docker Compose  
- Serverless Functions (event-driven simulation)  
- HTML / CSS  

---

## Deployment Notes

- The system is deployed on a cloud server (Alibaba Cloud ECS instance)  
- All services are running continuously using Docker Compose  
- The public IP is exposed for direct access  
- The application is accessible at: http://8.136.153.80:5000  
- This simulates a real cloud deployment environment rather than local-only execution  

---

## Design Rationale

Containers are used for long-running services (presentation, workflow, data),  
while serverless functions are used for event-driven, short-lived processing tasks.  

This separation improves scalability, modularity, and maintainability of the system.

The deployment demonstrates the feasibility of running a hybrid cloud architecture  
in a real cloud environment, integrating container services with event-driven processing.