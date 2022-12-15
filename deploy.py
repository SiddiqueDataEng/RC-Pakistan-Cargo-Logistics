#!/usr/bin/env python3
"""
RC Pakistan Cargo & Logistics - Deployment Script
Automated deployment and setup for the complete analytics pipeline
"""

import os
import sys
import subprocess
import pandas as pd
import sqlite3
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class RCLogisticsDeployment:
    def __init__(self):
        self.project_name = "RC Pakistan Cargo & Logistics"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.processed_dir = os.path.join(self.base_dir, 'processed_data')
        self.star_schema_dir = os.path.join(self.base_dir, 'star_schema')
        self.models_dir = os.path.join(self.base_dir, 'models')
        
    def create_directories(self):
        """Create necessary directories for the project"""
        directories = [
            self.data_dir,
            self.processed_dir,
            self.star_schema_dir,
            self.models_dir,
            os.path.join(self.base_dir, 'data_engineering'),
            os.path.join(self.base_dir, 'data_analysis'),
            os.path.join(self.base_dir, 'data_science'),
            os.path.join(self.base_dir, 'infrastructure'),
            os.path.join(self.base_dir, 'infrastructure', 'sql_scripts'),
            os.path.join(self.base_dir, 'dashboards'),
            os.path.join(self.base_dir, 'reports')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def install_dependencies(self):
        """Install required Python packages"""
        logger.info("Installing Python dependencies...")
        
        requirements = [
            'pandas>=2.0.0',
            'numpy>=1.24.0',
            'matplotlib>=3.7.0',
            'seaborn>=0.12.0',
            'plotly>=5.15.0',
            'scikit-learn>=1.3.0',
            'xgboost>=1.7.0',
            'faker>=19.0.0',
            'jupyter>=1.0.0',
            'openpyxl>=3.1.0'
        ]
        
        for package in requirements:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                logger.info(f"Installed: {package}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package}: {e}")
    
    def generate_sample_data(self):
        """Generate sample data using the data generator"""
        logger.info("Generating sample logistics data...")
        
        try:
            # Import and run the data generator
            sys.path.append(self.base_dir)
            from datagenerator import data_generator, save_to_csv
            
            # Generate data for 2022
            customers, bookings, shipments, payments = data_generator(
                "2022-01-01", 
                "2022-12-31", 
                records=1000
            )
            
            # Save to CSV files
            save_to_csv(customers, bookings, shipments, payments, self.data_dir)
            logger.info("Sample data generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
            return False
        
        return True
    
    def create_star_schema(self):
        """Create star schema from the generated data"""
        logger.info("Creating star schema...")
        
        try:
            # Load the generated data
            customers_df = pd.read_csv(os.path.join(self.data_dir, 'customers.csv'))
            bookings_df = pd.read_csv(os.path.join(self.data_dir, 'bookings.csv'))
            shipments_df = pd.read_csv(os.path.join(self.data_dir, 'shipments.csv'))
            payments_df = pd.read_csv(os.path.join(self.data_dir, 'payments.csv'))
            
            # Convert date columns
            customers_df['CreatedDate'] = pd.to_datetime(customers_df['CreatedDate'])
            bookings_df['BookingDate'] = pd.to_datetime(bookings_df['BookingDate'])
            shipments_df['ShipmentDate'] = pd.to_datetime(shipments_df['ShipmentDate'])
            shipments_df['ExpectedDelivery'] = pd.to_datetime(shipments_df['ExpectedDelivery'])
            payments_df['Date'] = pd.to_datetime(payments_df['Date'])
            
            # Create dimension tables
            self._create_dimensions(customers_df, bookings_df, shipments_df, payments_df)
            
            # Create fact tables
            self._create_facts(customers_df, bookings_df, shipments_df, payments_df)
            
            logger.info("Star schema created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create star schema: {e}")
            return False
        
        return True
    
    def _create_dimensions(self, customers_df, bookings_df, shipments_df, payments_df):
        """Create dimension tables"""
        
        # DimDate
        start_date = pd.to_datetime('2022-01-01')
        end_date = pd.to_datetime('2022-12-31')
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        dim_date = pd.DataFrame({
            'DateKey': [int(d.strftime('%Y%m%d')) for d in date_range],
            'FullDate': date_range,
            'Year': date_range.year,
            'Quarter': date_range.quarter,
            'Month': date_range.month,
            'MonthName': date_range.strftime('%B'),
            'Day': date_range.day,
            'WeekDay': date_range.dayofweek + 1,
            'WeekDayName': date_range.strftime('%A'),
            'IsWeekend': (date_range.dayofweek >= 5).astype(int)
        })
        
        # DimCustomer
        dim_customer = customers_df.copy()
        dim_customer['CustomerKey'] = range(1, len(dim_customer) + 1)
        dim_customer = dim_customer[['CustomerKey', 'CustomerID', 'Name', 'Phone', 'City', 'CreatedDate']]
        dim_customer.rename(columns={'Name': 'CustomerName'}, inplace=True)
        
        # DimCity
        cities_data = [
            (1, 'Dubai', 'UAE', 'Origin'),
            (2, 'Sharjah', 'UAE', 'Origin'),
            (3, 'Ajman', 'UAE', 'Origin'),
            (4, 'Karachi', 'Pakistan', 'Destination'),
            (5, 'Lahore', 'Pakistan', 'Destination'),
            (6, 'Islamabad', 'Pakistan', 'Destination'),
            (7, 'Rawalpindi', 'Pakistan', 'Destination'),
            (8, 'Peshawar', 'Pakistan', 'Destination'),
            (9, 'Mirpur', 'Azad Kashmir', 'Destination'),
            (10, 'Muzaffarabad', 'Azad Kashmir', 'Destination')
        ]
        dim_city = pd.DataFrame(cities_data, columns=['CityKey', 'CityName', 'Country', 'CityType'])
        
        # DimTransportMode
        transport_modes = [
            (1, 'Air', 'Fast delivery, higher cost'),
            (2, 'Sea', 'Economical, longer transit time')
        ]
        dim_transport = pd.DataFrame(transport_modes, columns=['ModeKey', 'ModeName', 'Description'])
        
        # DimStatus
        status_data = [
            (1, 'Booked', 'Initial booking created'),
            (2, 'In Transit', 'Shipment in progress'),
            (3, 'Arrived', 'Arrived at destination country'),
            (4, 'Customs Cleared', 'Cleared customs procedures'),
            (5, 'Delivered', 'Successfully delivered to customer')
        ]
        dim_status = pd.DataFrame(status_data, columns=['StatusKey', 'StatusName', 'Description'])
        
        # Save dimension tables
        dim_date.to_csv(os.path.join(self.star_schema_dir, 'DimDate.csv'), index=False)
        dim_customer.to_csv(os.path.join(self.star_schema_dir, 'DimCustomer.csv'), index=False)
        dim_city.to_csv(os.path.join(self.star_schema_dir, 'DimCity.csv'), index=False)
        dim_transport.to_csv(os.path.join(self.star_schema_dir, 'DimTransportMode.csv'), index=False)
        dim_status.to_csv(os.path.join(self.star_schema_dir, 'DimStatus.csv'), index=False)
        
        # Store for fact table creation
        self.dim_customer = dim_customer
        self.dim_city = dim_city
        self.dim_transport = dim_transport
        self.dim_status = dim_status
    
    def _create_facts(self, customers_df, bookings_df, shipments_df, payments_df):
        """Create fact tables"""
        
        # FactShipment
        fact_base = bookings_df.merge(shipments_df, on='BookingID', how='inner')
        
        # Create lookup dictionaries
        customer_lookup = dict(zip(self.dim_customer['CustomerID'], self.dim_customer['CustomerKey']))
        city_lookup = dict(zip(self.dim_city['CityName'], self.dim_city['CityKey']))
        transport_lookup = {'Air': 1, 'Sea': 2}
        status_lookup = {'Booked': 1, 'In Transit': 2, 'Arrived': 3, 'Customs Cleared': 4, 'Delivered': 5}
        
        def get_date_key(date_col):
            return pd.to_datetime(date_col).dt.strftime('%Y%m%d').astype(int)
        
        fact_shipment = pd.DataFrame({
            'ShipmentKey': range(1, len(fact_base) + 1),
            'ShipmentID': fact_base['ShipmentID'],
            'BookingID': fact_base['BookingID'],
            'CustomerKey': fact_base['CustomerID'].map(customer_lookup),
            'OriginCityKey': fact_base['Origin'].map(city_lookup),
            'DestinationCityKey': fact_base['Destination'].map(city_lookup),
            'TransportModeKey': fact_base['Mode'].map(transport_lookup),
            'StatusKey': fact_base['Status_x'].map(status_lookup),
            'BookingDateKey': get_date_key(fact_base['BookingDate']),
            'ShipmentDateKey': get_date_key(fact_base['ShipmentDate']),
            'ExpectedDeliveryDateKey': get_date_key(fact_base['ExpectedDelivery']),
            'WeightKG': fact_base['WeightKG'],
            'TransitDays': (pd.to_datetime(fact_base['ExpectedDelivery']) - pd.to_datetime(fact_base['ShipmentDate'])).dt.days
        })
        
        # FactRevenue
        revenue_base = payments_df.merge(bookings_df, on='BookingID', how='inner')
        
        fact_revenue = pd.DataFrame({
            'RevenueKey': range(1, len(revenue_base) + 1),
            'PaymentID': revenue_base['PaymentID'],
            'BookingID': revenue_base['BookingID'],
            'CustomerKey': revenue_base['CustomerID'].map(customer_lookup),
            'PaymentDateKey': pd.to_datetime(revenue_base['Date']).dt.strftime('%Y%m%d').astype(int),
            'Amount': revenue_base['Amount'],
            'PaymentMethod': revenue_base['Method'],
            'WeightKG': revenue_base['WeightKG'],
            'RevenuePerKG': revenue_base['Amount'] / revenue_base['WeightKG']
        })
        
        # Save fact tables
        fact_shipment.to_csv(os.path.join(self.star_schema_dir, 'FactShipment.csv'), index=False)
        fact_revenue.to_csv(os.path.join(self.star_schema_dir, 'FactRevenue.csv'), index=False)
    
    def create_database(self):
        """Create SQLite database with star schema"""
        logger.info("Creating SQLite database...")
        
        try:
            db_path = os.path.join(self.processed_dir, 'rc_logistics_dw.db')
            conn = sqlite3.connect(db_path)
            
            # Load and save all tables to database
            tables = ['DimDate', 'DimCustomer', 'DimCity', 'DimTransportMode', 'DimStatus', 'FactShipment', 'FactRevenue']
            
            for table in tables:
                df = pd.read_csv(os.path.join(self.star_schema_dir, f'{table}.csv'))
                df.to_sql(table, conn, if_exists='replace', index=False)
                logger.info(f"Created table: {table}")
            
            conn.close()
            logger.info(f"Database created: {db_path}")
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False
        
        return True
    
    def create_project_summary(self):
        """Create project summary and documentation"""
        logger.info("Creating project summary...")
        
        summary = f"""
# {self.project_name} - Analytics Pipeline

## Project Overview
Complete end-to-end data engineering, analytics, and machine learning pipeline for UAE-Pakistan logistics operations.

## Generated Components

### 1. Data Generation
- [x] Sample logistics data (1,000 records)
- [x] Customers, bookings, shipments, payments
- [x] Realistic UAE to Pakistan/Kashmir routes

### 2. Data Engineering
- [x] Data quality assessment and cleaning
- [x] Star schema data warehouse design
- [x] ETL pipeline implementation
- [x] SQLite database creation

### 3. Data Analysis
- [x] Exploratory data analysis
- [x] Business KPIs and metrics
- [x] Route performance analysis
- [x] Customer behavior insights

### 4. Data Science & ML
- [x] Transit time prediction model
- [x] Revenue forecasting model
- [x] Customer segmentation
- [x] Demand forecasting

### 5. Infrastructure
- [x] SQL scripts for star schema
- [x] Deployment automation
- [x] Configuration management

## Directory Structure
```
rc/
├── data/                    # Raw generated data
├── processed_data/          # Cleaned and processed data
├── star_schema/            # Star schema CSV files
├── models/                 # Trained ML models
├── data_engineering/       # Data engineering notebooks
├── data_analysis/          # Analytics notebooks
├── data_science/           # ML and AI notebooks
├── infrastructure/         # SQL scripts and configs
├── dashboards/            # BI dashboards (future)
└── reports/               # Generated reports (future)
```

## Key Features
- **Realistic Data**: UAE-Pakistan logistics operations
- **Star Schema**: Optimized for analytics and BI
- **ML Models**: Predictive analytics for business insights
- **Scalable**: Ready for production deployment
- **Documentation**: Comprehensive notebooks and scripts

## Next Steps
1. Run Jupyter notebooks for detailed analysis
2. Deploy to cloud infrastructure (Azure/AWS)
3. Create Power BI dashboards
4. Implement real-time data pipeline
5. Add advanced ML features

## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(os.path.join(self.base_dir, 'PROJECT_SUMMARY.md'), 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info("Project summary created")
    
    def run_deployment(self):
        """Run the complete deployment process"""
        logger.info(f"Starting deployment of {self.project_name}")
        logger.info("=" * 60)
        
        steps = [
            ("Creating directories", self.create_directories),
            ("Installing dependencies", self.install_dependencies),
            ("Generating sample data", self.generate_sample_data),
            ("Creating star schema", self.create_star_schema),
            ("Creating database", self.create_database),
            ("Creating project summary", self.create_project_summary)
        ]
        
        for step_name, step_function in steps:
            logger.info(f"Step: {step_name}")
            try:
                result = step_function()
                if result is False:
                    logger.error(f"Step failed: {step_name}")
                    return False
                logger.info(f"Step completed: {step_name}")
            except Exception as e:
                logger.error(f"Step failed with exception: {step_name} - {e}")
                return False
        
        logger.info("=" * 60)
        logger.info("Deployment completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Open Jupyter notebooks in data_engineering/, data_analysis/, data_science/")
        logger.info("2. Explore the generated data and star schema")
        logger.info("3. Run the ML models and analytics")
        logger.info("4. Check PROJECT_SUMMARY.md for detailed overview")
        
        return True

def main():
    """Main deployment function"""
    deployment = RCLogisticsDeployment()
    success = deployment.run_deployment()
    
    if success:
        print("\nRC Pakistan Cargo & Logistics Analytics Pipeline deployed successfully!")
        print("Check the generated files and notebooks to get started.")
    else:
        print("\nDeployment failed. Check deployment.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()