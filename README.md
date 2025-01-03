# Instructure-Canvas-APIs

This project contains a Django management command to automate the import of data from the **Canvas LMS API** into a PostgreSQL database. The script fetches data for resources like users, courses, assignments, and submissions, and updates or creates records in the database.

---

## Features
- **Automated Canvas Data Import** – Pulls data directly from Canvas LMS via API requests.  
- **Dynamic Resource Handling** – Supports importing data for various resources including:
  - `Users`
  - `Assignments`
  - `Courses`
  - `Submissions`
  - `Assignment Groups`
  - `Sections`  
- **Upsert Operation** – Updates existing records or creates new ones to avoid data duplication.  
- **Flexible Configuration** – Options to target specific academic years, courses, or LMS environments (Live/Test).  
- **Batch Processing** – Fetches and processes data for multiple courses in a single run.  

---

## Requirements
- **Python 3.8+**  
- **Django Framework**  
- **PostgreSQL Database**  
- **pipenv** (for dependency management)  
- **Canvas LMS API Access**

- Environment Setup
Create a .env file in the root directory with the following structure:

LMS_LIVE_BASE_URL=https://canvas.live.com/api/v1
LMS_LIVE_ACCESS_TOKEN=your_live_access_token
LMS_TEST_BASE_URL=https://canvas.test.com/api/v1
LMS_TEST_ACCESS_TOKEN=your_test_access_token

## How It Works
The script queries the Canvas API for the specified resource (e.g., assignments or users).

Data is fetched and stored in the PostgreSQL database.

The script supports pagination and continues fetching data until all records are processed.

If --del_existing=yes is specified, existing records for the target resource are truncated before new data is imported.

## Logging

The script logs import activities using the LogManagement class, providing detailed records of processed resources, errors, and successful imports.
