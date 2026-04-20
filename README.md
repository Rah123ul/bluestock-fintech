# 📈 Nifty 100 Financial Intelligence Platform

## 📖 Project Overview
The Nifty 100 Financial Intelligence Platform is a comprehensive web application for analyzing, visualizing, and scoring the top 100 NSE companies. It features an automated data pipeline and machine learning-based health scoring to evaluate financial stability. The platform provides interactive dashboards and actionable insights to empower users with data-driven investment decisions.

## 🔗 Live Demo
**[Live Application (Railway)](https://web-production-83588.up.railway.app)**

## 🌟 Features
- **Automated Data Pipeline:** End-to-end ETL processes handling data extraction, cleaning, and loading to a centralized PostgreSQL data warehouse.
- **Financial Health Scoring:** Intelligent module assessing profitability, growth, leverage, and cash flow to assign health labels.
- **Interactive Dashboards:** Dynamic and responsive frontend visualizations powered by Chart.js for real-time fundamental analysis.
- **Data Screener:** Advanced data screening capabilities to filter companies based on various financial metrics.
- **RESTful API Architecture:** Robust backend services built with Django REST Framework serving financial metrics securely.
- **Power BI Integration:** Support for enterprise reporting and deep-dive analytical insights using DAX measures.

## 💻 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.14 |
| **Backend Framework** | Django 6.0, Django REST Framework |
| **Data Processing** | pandas |
| **Database** | PostgreSQL |
| **Frontend/Visualization**| HTML, CSS, JavaScript, Chart.js |
| **Deployment** | Railway |

## 📂 Project Structure

```text
bluestock-fintech/
├── api/                  # Django app for serving RESTful endpoints
├── bluestock/            # Main Django project configuration settings
├── companies/            # Django app for company models and core views
├── data/                 # Raw and cleaned dataset storage
│   ├── clean/
│   └── raw/
├── etl/                  # Python scripts for Extract, Transform, Load processes
├── notebooks/            # Jupyter notebooks for data exploration and logic testing
├── powerbi/              # DAX measures and BI connection documentation
├── scripts/              # Shell scripts for deployment and environment setup
├── sql/                  # Raw SQL scripts for database schema and queries
├── static/               # CSS, JS, Images, and Chart.js configurations
└── templates/            # HTML templates for rendering the frontend views
```

## 🚀 How to Run Locally

Follow these steps to set up the development environment:

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/bluestock-fintech.git
cd bluestock-fintech
```

**2. Create a virtual environment and install dependencies**
```bash
python3.14 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

**3. Configure Environment Variables**
Create a `.env` file in the root directory and add your database configuration:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/bluestock_db
```

**4. Run Migrations and Start the Server**
```bash
python manage.py migrate
python manage.py runserver
```
*Visit `http://localhost:8000` in your browser.*

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/companies/` | Retrieves a list of all Nifty 100 companies. |
| `GET` | `/api/v1/companies/screener/` | Retrieves filtered company data for the screener. |
| `GET` | `/api/v1/companies/health-scores/` | Retrieves the computed financial health scores. |
| `GET` | `/api/v1/companies/{company_id}/` | Retrieves detailed information for a specific company. |
| `GET` | `/api/v1/companies/{company_id}/charts/` | Retrieves charting data for a specific company. |

## 📸 Screenshots

*(Replace with actual screenshots of your dashboards and UI)*

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)
![Company Analysis](https://via.placeholder.com/800x400?text=Financial+Charts+Screenshot)
