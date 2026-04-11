# 🚀 Smart Retail Predictor: Enterprise AI & Demand Forecasting ERP

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/MySQL-4479A1.svg?style=for-the-badge&logo=MySQL&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/Data%20Engineering-8A2BE2.svg?style=for-the-badge" alt="Data Engineering" />
</div>

<br>

> **Bridging the gap between raw transactional data and predictive intelligence.** > Smart Retail Predictor is a full-stack, AI-driven inventory management and sales forecasting platform. It seamlessly ingests raw Excel data, processes it through a heavily normalized MySQL database engine, and utilizes Machine Learning to generate 30-day demand forecasts—all visualized on a dark-themed, interactive dashboard.

---

## ✨ System Architecture & Core Modules

### 🧠 1. AI Predictive Engine
* **Demand Forecasting:** Utilizes Machine Learning (`scikit-learn`) to project 30-day sales trends, factoring in historical velocity and seasonal indexing.
* **Automated Data Pipelines:** Drag-and-drop file ingestion system that automatically cleanses, normalizes, and maps bulk CSV/Excel data to the relational backend.

### 🗄️ 2. Enterprise Database Engine (The Core)
The backbone of the application is a **Fully Normalized (3NF) 12-Table MySQL Schema**. The system offloads heavy computational logic from the Python frontend directly to the database layer for maximum performance.
* **Virtualization:** Employs pre-calculated **Views** (`User_Sales_Summary`) to feed the dashboard instantly.
* **Procedural Logic (PL/SQL):** Utilizes **Row-by-Row Cursors** for complex transaction evaluation and **User-Defined Functions (UDFs)** for dynamic customer loyalty tier calculations.
* **Deep Analytics:** Leverages **Correlated Subqueries**, **Set Operations (`UNION`)**, and **Advanced Aggregations (`HAVING`)** to generate instant executive reports (e.g., above-average sales tracking, product extremes).

### 🛡️ 3. Security & Transaction Integrity
* **ACID Compliance:** Implements strict **Exception Handling** via `START TRANSACTION` and `ROLLBACK` protocols. If bad data is injected, the transaction is killed before corruption occurs.
* **Automated Auditing:** Features an `AFTER INSERT` **Trigger** that acts as a silent security camera, logging every bulk upload action, user ID, and timestamp into an isolated `Audit_Log` table without requiring API calls.
* **Cascading Deletes:** Strict `FOREIGN KEY` constraints ensure no orphaned records exist if users or suppliers are removed from the system.

---

## 📊 Interactive Dashboard Interface

The Streamlit UI provides a unified command center for store managers:
* **Real-Time KPIs:** Instant tracking of revenue, quantity sold, and user activity.
* **Complex Query Execution:** A dedicated "Advanced Database Operations" control panel allows users to trigger Stored Procedures, execute subqueries, and test database constraints live with a single click.
* **Visual Data Storytelling:** Interactive line charts and data frames mapping historical performance against AI-generated future predictions.

---

## 🗺️ Database ER Diagram

*(The system architecture maps transactional sales to predictive models via external factors and inventory constraints.)*

**[📸 Replace this text: Drag and drop your final er_diagram.png image here]**

---

## 🛠️ Technical Stack

| Category | Technologies Used |
| :--- | :--- |
| **Frontend UI** | Python, Streamlit, Pandas, Altair |
| **Backend Database** | MySQL 8.0, Advanced PL/SQL |
| **Machine Learning** | Scikit-learn, NumPy |
| **Database Paradigms** | 3NF Normalization, Cursors, Triggers, UDFs, Subqueries, Joins |
| **Version Control** | Git, GitHub |
