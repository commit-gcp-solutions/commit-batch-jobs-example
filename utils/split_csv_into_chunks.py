import csv
import os
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor

def split_csv(input_file, chunk_size, output_dir, bucket_name):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extract the directory name from the input_file path
    input_dirname = os.path.dirname(input_file)
    # Get the base name of the input_file without the extension
    input_filename = os.path.splitext(os.path.basename(input_file))[0]

    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header row

        chunk_num = 1
        current_chunk = []
        current_chunk_size = 0
        chunks_to_upload = []

        for row in reader:
            current_chunk.append(row)
            current_chunk_size += 1

            if current_chunk_size >= chunk_size:
                output_file = os.path.join(output_dir, f'chunk_{chunk_num}.csv')
                write_chunk_to_csv(output_file, header, current_chunk)
                chunks_to_upload.append(output_file)

                chunk_num += 1
                current_chunk = []
                current_chunk_size = 0

        # Write the remaining rows to the last chunk
        if current_chunk:
            output_file = os.path.join(output_dir, f'chunk_{chunk_num}.csv')
            write_chunk_to_csv(output_file, header, current_chunk)
            chunks_to_upload.append(output_file)

        print("CSV file split into chunks successfully.")

        # Upload chunks to the Cloud Storage bucket in parallel
        upload_chunks_to_bucket(bucket_name, chunks_to_upload, input_dirname, input_filename)

    return chunk_num - 1  # Return the count of chunks

def write_chunk_to_csv(filename, header, rows):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for row in rows:
            writer.writerow(row)

def upload_chunk_to_bucket(bucket_name, chunk_file, input_dirname, input_filename):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    # Construct the destination blob path by appending the input filename and the chunk filename
    dest_blob_path = os.path.join(input_filename, os.path.basename(chunk_file))
    
    blob = bucket.blob(dest_blob_path)
    blob.upload_from_filename(chunk_file)
    print(f"Uploaded {chunk_file} to Cloud Storage bucket: {bucket_name}")

def upload_chunks_to_bucket(bucket_name, chunk_files, input_dirname, input_filename):
    with ThreadPoolExecutor() as executor:
        for chunk_file in chunk_files:
            executor.submit(upload_chunk_to_bucket, bucket_name, chunk_file, input_dirname, input_filename)
    
    print("All chunks uploaded to Cloud Storage successfully.")
