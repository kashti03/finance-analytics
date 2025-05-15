import boto3
import csv
import os

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def upload_csv_to_dynamodb(file_path, table_name):
    try:
        table = dynamodb.Table(table_name)
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            print(f"Starting upload from {file_path} to table {table_name}...")
            for row in reader:
                item = {k: str(v) for k, v in row.items()}  # ensure all values are strings
                table.put_item(Item=item)
                count += 1
                if count % 10 == 0:
                    print(f"✅ {count} rows uploaded to {table_name}...")
            print(f"Completed uploading {count} rows to {table_name}\n")
    except Exception as e:
        print(f"Error uploading {file_path} to {table_name}: {e}")

if __name__ == "__main__":
    print("Script started")

    env = os.getenv("ENV", "dev")  # You can change this if needed

    base_path = os.path.join(os.path.dirname(__file__), "..", "data")

    datasets = {
        f"{env}_finance_data": "finance_data.csv",
        f"{env}_order_report_data": "order_report_data.csv",
        f"{env}_product_report_data": "product_report_data.csv"
    }

    for table_name, filename in datasets.items():
        file_path = os.path.join(base_path, filename)
        if os.path.exists(file_path):
            upload_csv_to_dynamodb(file_path, table_name)
        else:
            print(f"File not found: {file_path}")

    print("All uploads complete.")
