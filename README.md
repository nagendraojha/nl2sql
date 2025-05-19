# NL2SQL Demo Project

# Overview
This project demonstrates a Natural Language to SQL (NL2SQL) converter using the Mistral-7B model through Hugging Face's Inference API. The system generates SQL queries from natural language questions and evaluates the results using Loose Match Accuracy.

Model Access Issues
The following suggested models were not working or accessible during testing:

- tscholak/optimum-nl2sql

- b-mc2/sqlcoder

- Salesforce/grappa_large

So, I used mistralai/Mistral-7B-Instruct-v0.3 instead.

# Setup Instructions

1. Install required dependencies:

-pip install requests python-dotenv


2. Create a .env file with your Hugging Face API token:

-HUGGINGFACE_API_TOKEN=""


# Running the Demo

Execute the script with:

- python nl2sql_demo.py


# Evaluation Metrics
- Evaluation Method: Loose Match Accuracy
- Current Performance:78% accuracy on sample questions
- Note:The loose match approach considers token similarity rather than requiring exact matches, providing more flexible evaluation.

# Project Details
- Uses a sample database schema with employees and departments tables
- Designed for testing basic SQL generation capabilities
- Implements error handling for API reliability



