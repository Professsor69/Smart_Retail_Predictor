# 🚀 Smart Retail Predictor: Enterprise AI & Demand Forecasting ERP

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/MySQL-4479A1.svg?style=for-the-badge&logo=MySQL&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" />
</div>

<br>

> **Bridging the gap between raw transactional data and predictive intelligence.**
> Smart Retail Predictor is a full-stack, AI-driven inventory management and sales forecasting platform. It seamlessly ingests raw Excel data, processes it through a highly normalized MySQL database engine, and utilizes Machine Learning to generate 30-day demand forecasts—all visualized on a sleek, modern glassmorphism web application.

---

## ✨ System Architecture & Core Modules

### 🧠 1. AI Predictive Engine
* **Demand Forecasting:** Utilizes Machine Learning (`scikit-learn`) to project 30-day sales trends, factoring in historical velocity and seasonal indexing.
* **Automated Data Pipelines:** Drag-and-drop file ingestion system that automatically cleanses, normalizes, and maps bulk CSV/Excel data to the relational backend.

### 🗄️ 2. Enterprise Database Engine (The Core)
The backbone of the application is a **Fully Normalized (3NF) MySQL Schema**. The system offloads heavy computational logic directly to the database layer for maximum performance.
* **Complex Query Execution:** Utilizes advanced SQL techniques including Correlated Subqueries, Set Operations (`UNION`), and Advanced Aggregations (`HAVING`) to generate instant reports.
* **Transaction Integrity:** Strict error handling prevents bad data injection, with automated logging systems tracking bulk upload actions.

### 🌐 3. High-Performance Web Architecture
Recently migrated from a monolithic Streamlit architecture to a modern, decoupled client-server model:
* **FastAPI Backend:** Provides robust, asynchronous RESTful API endpoints for data processing and machine learning integration.
* **Custom Glassmorphism Frontend:** A highly responsive, premium dark-themed UI built with pure HTML, CSS, and vanilla JavaScript.
* **Secure Authentication:** Seamless username and password verification with secure tokens.

---

## 💻 Getting Started

### Prerequisites
* Python 3.9+
* MySQL Server (running locally)

### Quick Start
We've included simple scripts to manage the application server seamlessly:

1. **Start the Server:** Double-click `start_server.bat`
2. **Access the App:** Open your browser and navigate to `http://localhost:8000`
3. **Stop the Server:** Double-click `stop_server.bat` to instantly kill all related background processes.

---

## 📊 Interactive Dashboard Interface

The custom web UI provides a unified command center for store managers:
* **Real-Time KPIs:** Instant tracking of revenue, quantity sold, and user activity.
* **Data Ingestion:** Secure drag-and-drop file uploads for continuous data integration.
* **Visual Data Storytelling:** Interactive charts and data frames mapping historical performance against AI-generated future predictions.

---

## 🛠️ Technical Stack

| Category | Technologies Used |
| :--- | :--- |
| **Frontend UI** | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript, Chart.js |
| **Backend API** | Python, FastAPI, Uvicorn |
| **Database** | MySQL 8.0 |
| **Machine Learning** | Scikit-learn, NumPy, Pandas |
| **Authentication** | Secure Local Auth |
| **Version Control** | Git, GitHub |
