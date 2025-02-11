import boto3
import sqlparse
import json
from datetime import datetime
import re

class FinanceDataImporter:
    def _init_(self, table_name, region='us-east-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        
    def parse_sql_file(self, file_path):
        """Parse SQL file and extract INSERT statements data."""
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Extract column names from the INSERT statement
        column_match = re.search(r'INSERT INTO \w+ \((.*?)\) VALUES', sql_content)
        if not column_match:
            raise ValueError("Could not find column names in SQL file")
            
        # Get column names and clean them
        columns = [col.strip(' "`') for col in column_match.group(1).split(',')]
        
        # Parse values
        values_pattern = r'VALUES\s*\((.?)\)(?=\s[,;]|$)'
        values_matches = re.finditer(values_pattern, sql_content, re.DOTALL)
        
        items = []
        for match in values_matches:
            values = self.split_values(match.group(1))
            if len(columns) != len(values):
                print(f"Warning: Column count mismatch. Columns: {len(columns)}, Values: {len(values)}")
                continue
            item = self.create_dynamo_item(columns, values)
            items.append(item)
            
        return items
    
    def split_values(self, values_str):
        """Split values handling quoted strings and NULL values."""
        values = []
        current = ''
        in_quotes = False
        for char in values_str + ',':  # Add comma to handle last value
            if char == "'" and not in_quotes:
                in_quotes = True
            elif char == "'" and in_quotes:
                in_quotes = False
            elif char == ',' and not in_quotes:
                values.append(self.clean_value(current.strip()))
                current = ''
            else:
                current += char
        return values
    
    def clean_value(self, value):
        """Clean and convert SQL values to appropriate types."""
        if value.upper() == 'NULL' or value == '':
            return None
            
        # Remove quotes if present
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            
        # Try to convert to number if possible
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            # Check if it's a JSON string
            if value.startswith('{') and value.endswith('}'):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
    
    def create_dynamo_item(self, columns, values):
        """Create DynamoDB item from columns and values."""
        item = {}
        
        # Map specific columns to their values
        for col, val in zip(columns, values):
            # Skip null values
            if val is None:
                continue
                
            # Handle specific columns
            if col == 'id':
                item['id'] = str(val)  # Primary key should be string
            elif col == 'event_list' and isinstance(val, dict):
                item['event_list'] = val  # Already parsed JSON
            elif col in ['product_sales', 'product_sales_tax', 'shipping_credits', 
                        'shipping_credits_tax', 'total']:
                # Convert financial values to string to preserve precision
                item[col] = str(val)
            elif col in ['purchasedate_n', 'utc_posted_date', 'datetime_n', 
                        'date_time', 'order_date', 'order_date_utc']:
                # Keep dates as strings
                item[col] = str(val) if val else None
            elif col in ['created_at', 'updated_at']:
                # Unix timestamps
                item[col] = int(val) if val else None
            else:
                item[col] = val
                
        return item
    
    def import_to_dynamodb(self, items):
        """Import items to DynamoDB table."""
        batch_size = 25
        total_batches = (len(items) - 1) // batch_size + 1
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            try:
                with self.table.batch_writer() as writer:
                    for item in batch:
                        writer.put_item(Item=item)
                print(f"Imported batch {i//batch_size + 1} of {total_batches}")
            except Exception as e:
                print(f"Error importing batch {i//batch_size + 1}: {str(e)}")
                print("First failed item:", batch[0])
                raise

def main():
    # Configuration
    table_name = 'dev_finance_data'  
    sql_file_path = 'data\finance_data.sql'   
    aws_region = 'us-west-2'             
    
    try:
        importer = FinanceDataImporter(table_name, aws_region)
        
        print("Parsing SQL file...")
        items = importer.parse_sql_file(sql_file_path)
        
        print(f"Found {len(items)} items to import")
        print("Sample first item:")
        print(json.dumps(items[0], indent=2))  
        
        confirm = input("Continue with import? (y/n): ")
        if confirm.lower() != 'y':
            print("Import cancelled")
            return
            
        print("Importing to DynamoDB...")
        importer.import_to_dynamodb(items)
        
        print("Import completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if _name_ == "_main_":
    main()