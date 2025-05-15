import pandas as pd
import re
import os

def sql_to_csv(file_path):
    """
    Converts an .sql file containing INSERT statements into a cleaned .csv file.
    
    Parameters:
        file_path (str): Path to the .sql file.
    
    Returns:
        str: Path to the saved .csv file.
    """
    # Read the SQL file
    with open(file_path, "r", encoding="utf-8") as file:
        sql_content = file.readlines()

    # Extract column names from the first line
    column_names_match = re.search(r"INSERT INTO `\w+` \((.*?)\) VALUES", sql_content[0])
    if column_names_match:
        columns = [col.strip("` ") for col in column_names_match.group(1).split(",")]
    else:
        raise ValueError("Could not extract column names from SQL file.")

    # Extract data rows
    data_rows = []
    for line in sql_content[1:]:  # Skip first line (column names)
        values_match = re.findall(r"\((.*?)\)", line)
        if values_match:
            for row in values_match:
                values = [val.strip().strip("'") for val in row.split(",\t")]
                data_rows.append(values)

    # Create DataFrame
    df = pd.DataFrame(data_rows, columns=columns)

    # Clean the dataset
    df.replace("NULL", None, inplace=True)  # Replace SQL NULLs with None (NaN in pandas)
    df.dropna(axis=1, how="all", inplace=True)  # Remove entirely empty columns

    # Define CSV file path
    csv_file_path = file_path.replace(".sql", ".csv")

    # Save DataFrame to CSV
    df.to_csv(csv_file_path, index=False)

    print(f"CSV file saved at: {csv_file_path}")
    return csv_file_path

# Example usage
sql_file_path = "data\product_report_data.sql"  # Change this to your actual .sql file path
sql_to_csv(sql_file_path)