# retail-purchase-insights
An end-to-end data pipeline analyzing retail customer behavior and revenue trends using Python, PostgreSQL, and Tableau.

# Customer Behavior Analytics

An end-to-end data pipeline analyzing retail customer behavior and revenue trends. This project utilizes Python and PostgreSQL to process retail data, featuring a Tableau dashboard that visualizes customer purchase patterns, demographic revenue, and subscription impacts.

## Key Features
* **Demographic Analysis:** Calculates revenue by age group and gender to identify high-value segments.
* **Purchase Patterns:** Tracks average purchase amount, purchase frequency, and seasonal trends.
* **Customer Attributes:** Analyzes the impact of shipping types, applied discounts, and subscription status on customer lifetime value.
* **Product Insights:** Evaluates average review ratings and category performance.

## Tech Stack
* **Database:** PostgreSQL (`customer_behavior` database)
* **Data Processing:** Python (Pandas, SQLAlchemy)
* **Visualization:** Tableau

## Project Structure
* `/data/` - Raw and processed datasets (ignored in version control)
* `/sql/` - PostgreSQL schema and table creation scripts
* `/src/` - Python scripts for data extraction, cleaning, and database loading
* `/dashboards/` - Tableau workbook files

## Setup Instructions
1. Clone this repository to your local machine.
2. Set up a local PostgreSQL instance and execute the schema scripts in the `/sql/` directory to create the `customer_behavior` database.
3. Install the required Python dependencies using `pip install -r requirements.txt`.
4. Run the data processing scripts in `/src/` to load and clean the dataset.
5. Open the Tableau workbook in the `/dashboards/` folder and connect it to your local PostgreSQL database.
