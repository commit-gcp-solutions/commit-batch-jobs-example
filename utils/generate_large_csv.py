import csv
import random
import os

def generate_large_csv(filename, num_rows):
    # create the demo directory if it doesn't exist
    if not os.path.exists('demo'):
        os.makedirs('demo')

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['number_1', 'number_2', 'number_3'])
        
        for _ in range(num_rows):
            row = [random.randint(1, 100) for _ in range(3)]
            writer.writerow(row)
    
    print(f"Large CSV file '{filename}' generated successfully.")
