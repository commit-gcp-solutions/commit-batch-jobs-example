import csv
import os

def process_chunk(chunk_data):
    processed_rows = []
    
    for row in chunk_data:
        number_1 = int(row['number_1'])
        number_2 = int(row['number_2'])
        number_3 = int(row['number_3'])
        
        processed_result = number_1 + number_2 - number_3
        row['processed_result'] = processed_result
        
        processed_rows.append(row)
    
    return processed_rows

# Example usage:

# Read a chunk of data from a CSV file
def read_chunk(chunk_file):
    with open(chunk_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        chunk_data = [row for row in reader]
    
    return chunk_data

# Process a chunk of data
def process_csv_chunk(chunk_file):
    # Extract the input file directory and base name
    input_dir = os.path.dirname(chunk_file)
    input_basename = os.path.basename(chunk_file)
    
    # Create the output directory if it doesn't exist
    output_dir = os.path.join(input_dir, 'processed')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    chunk_data = read_chunk(chunk_file)
    processed_rows = process_chunk(chunk_data)
    
    output_file = os.path.join(output_dir, input_basename.replace('.csv', '_processed.csv'))
    
    with open(f"{output_file}", 'w', newline='') as csvfile:
        fieldnames = processed_rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)
    
    print(f"Processed chunk '{chunk_file}' and saved the result to '{output_file}'.")

# Usage example:
BATCH_TASK_INDEX = os.environ.get('BATCH_TASK_INDEX', 0)
BATCH_TASK_INDEX_AS_INT = int(BATCH_TASK_INDEX)
FILE_NUMBER = str(BATCH_TASK_INDEX_AS_INT + 1)  # Convert the string to an integer
# Convert the string to an integer
process_csv_chunk(f'/mnt/share/large_data/chunk_{FILE_NUMBER}.csv')  # Process a single chunk file