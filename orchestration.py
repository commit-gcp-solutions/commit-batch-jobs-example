import os
import random
from utils.generate_large_csv import generate_large_csv
from utils.split_csv_into_chunks import split_csv
from utils.batch_jobs import create_script_job_with_bucket
from dotenv import load_dotenv

load_dotenv()

# Get the project ID, region, and bucket name from the environment variables
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
region = os.environ["GOOGLE_CLOUD_REGION"]
bucket_name = os.environ["GOOGLE_CLOUD_BUCKET_NAME"]

# Generate a large CSV file with 1 million rows and 3 columns
input_file = 'demo/large_data.csv'
generate_large_csv(input_file, 1000000)

# Split the large CSV file into smaller chunks and upload them to the Cloud Storage bucket
input_file = 'demo/large_data.csv'
output_dir = os.path.splitext(input_file)[0] + '_chunks'
bucket_name = 'neuklix-demo-bucket'
num_chunks = split_csv(input_file, 10000, output_dir, bucket_name)
print(f"The file was divided into {num_chunks} chunks.")

# create a random 4 digit number to be used as a job name
job_name = f"script-job-{random.randint(1000, 9999)}"
create_script_job_with_bucket(
    project_id, 
    region, 
    job_name, 
    bucket_name, 
    custom_command="sudo apt-get install python3-pip -y; cd /mnt/share/scripts/process_chunk; pip3 install -r requirements.txt; python3 process_chunk.py", 
    # num_of_parallel_tasks=num_chunks
    num_of_parallel_tasks=1
)