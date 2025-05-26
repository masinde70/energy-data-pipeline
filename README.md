# Energy Data Pipeline

This project processes ENTSO-E grid data using S3, Iceberg, Redshift, dbt, and Airflow, provisioned with Terraform. It mimics asset/market data platforms (e.g., Tanesco).


* **Objective**: Build an end-to-end data pipeline to process energy grid data (e.g., electricity consumption or generation), mimicking asset/market data workflows.
* **Tech Stack**:
  * **AWS S3**: Store raw meter data (bronze layer).
  * **Apache Iceberg**: Clean and partition data (silver layer).
  * **Amazon Redshift**: Model a star schema (gold layer).
  * **dbt**: Transform data in Redshift.
  * **Apache Airflow**: Schedule and orchestrate the pipeline.
  * **Terraform**: Provision AWS infrastructure (S3, Redshift, etc.).
* **Data Source**: Public ENTSO-E dataset (e.g., electricity load or generation time-series).
* **Deliverable**: A GitHub repository with code, Terraform scripts, and a README linking to asset/market data use cases.


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
