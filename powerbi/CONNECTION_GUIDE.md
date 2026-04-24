# Connecting Power BI to Railway PostgreSQL

This guide provides step-by-step instructions on how to connect your Power BI Desktop to your Railway-hosted PostgreSQL database.

## 1. Install PostgreSQL ODBC Driver on Windows
Power BI requires the Npgsql driver to interact with PostgreSQL databases securely.
- Open your web browser and search for **Npgsql**.
- Go to the Npgsql releases page or download directly via the Power BI documentation link.
- Download the Windows installer (`.msi` file).
- Run the installer. When prompted for features to install, ensure that the **Npgsql GAC Installation** (Global Assembly Cache) is selected and installed.
- Restart Power BI Desktop if it was open.

## 2. Get Your Railway PostgreSQL Connection Details
- Log in to your Railway dashboard (railway.app) and open your project.
- Click on your **PostgreSQL** service.
- Navigate to the **Connect** or **Variables** tab.
- Switch to the **Public Network** view (internal network URLs will not work from your local machine).
- Note down the following details from your `DATABASE_URL` (format: `postgresql://[User]:[Password]@[Host]:[Port]/[Database]`):
  - **Server (Host)**: Usually looks like `roundhouse.proxy.rlwy.net`
  - **Port**: Usually a 5-digit number like `29557`
  - **Database name**: Usually `railway`
  - **Username**: Usually `postgres`
  - **Password**: The provided password string

## 3. Connect Power BI to PostgreSQL
- Open Power BI Desktop.
- Click on **Get Data** > **More...**
- Search for **PostgreSQL** in the search bar and select **PostgreSQL database**.
- Click **Connect**.
- In the Server field, enter your Railway host and port separated by a colon (e.g., `roundhouse.proxy.rlwy.net:29557`).
- In the Database field, enter your database name (e.g., `railway`).
- Under Data Connectivity mode, choose **Import**.
- Click **OK**.
- When prompted for credentials, enter your Railway PostgreSQL Username and Password.
- Click **Connect**.

## 4. Import the Required Tables
- Once connected, a Navigator window will appear showing your database structure.
- Expand the database folder, then expand the **public** schema folder.
- Check the boxes next to the following tables to select them:
  - `dim_company`
  - `fact_profit_loss`
  - `fact_balance_sheet`
  - `fact_cash_flow`
  - `fact_ml_scores`
- Click **Load** to import the data into Power BI. (If you need to clean data types first, you can click Transform Data instead).

## 5. Create Relationships Between Tables
- Go to the **Model view** in Power BI (the relations icon on the left sidebar).
- Power BI might have auto-detected some relationships. It is highly recommended to review them.
- To build the star schema, you need to connect your dimension table (`dim_company`) to all your fact tables using the `company_id` field.
- Drag and drop the `company_id` column from `dim_company` to the `company_id` column in `fact_profit_loss`.
- Repeat this process to link `dim_company` to `fact_balance_sheet`, `fact_cash_flow`, and `fact_ml_scores`.
- Ensure all relationships are **1-to-Many** (1 side on `dim_company`, Many side * on the fact tables) and the cross-filter direction is set to **Single**.

## 6. Refresh Data
- Whenever you load new data into your Railway Postgres DB (e.g. running your python ETL scripts), you will want to update your dashboards.
- In Power BI Desktop, go to the **Home** tab on the ribbon.
- Click on the **Refresh** button.
- Power BI will reach out to Railway, pull the latest data for all tables, and automatically update your visualizations.
