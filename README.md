# Energy Data Pipeline

This project processes ENTSO-E grid data using S3, Iceberg, Redshift, dbt, and Airflow, provisioned with Terraform. It mimics asset/market data platforms (e.g., Tanesco).

## Project Structure

```
energy-data-pipeline/
├── terraform/         # Terraform scripts for infrastructure provisioning
├── scripts/           # Python scripts for data ingestion and processing
├── dbt/               # dbt project for Redshift data transformation
├── airflow/           # Airflow DAGs for workflow orchestration
├── data/              # Sample ENTSO-E data (not pushed to Git)
└── README.md          # Project documentation
```

## Getting Started

(Instructions for setting up and running the project will go here)
