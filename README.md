# Google Cloud Batch Jobs for Compute-Intensive Tasks

This repository contains a set of scripts that demonstrate how to use Google Cloud Batch Jobs service for offloading compute-intensive tasks to the cloud, even when these tasks require GPU acceleration (although the GPU example is not included in the repository). The purpose of these scripts is to provide an example and guide on how to leverage Google Cloud Batch Jobs for running compute-intensive workloads efficiently.

## Contents

The repository consists of the following scripts:

1. **generate_large_csv.py**: This script is used to generate a large CSV file that will be used for the example. It creates a CSV file with a specified number of rows and three columns, filled with random integer values. The script ensures the creation of a "demo" directory if it doesn't exist and generates the large CSV file within it.

2. **split_csv_into_chunks.py**: This script is responsible for splitting the large CSV file into smaller chunks and uploading them to a Cloud Storage bucket. It reads the input CSV file, divides it into chunks of a specified size, and saves each chunk as a separate CSV file. The chunks are then uploaded to the specified Cloud Storage bucket in parallel. The script utilizes the Google Cloud Storage Python library for managing the bucket and file uploads.

3. **batch_jobs.py**: This script defines a function to create batch jobs using the Google Cloud Batch Jobs API. The create_script_job_with_bucket function demonstrates how to create a sample Batch Job that runs a custom command on Cloud Compute instances. It takes parameters such as the project ID, region, job name, bucket name, custom command, and the number of parallel tasks. The function configures the job with the specified parameters, including task specifications, resource requirements, retry count, and maximum run duration. It also sets labels and logging policies for the job.

4. **process_chunk.py**: This script represents the actual task that will be run as part of the batch job. It defines functions to process a chunk of data from a CSV file. The process_chunk function takes a chunk of data, performs calculations on each row, and returns the processed rows. The script also includes an example usage that demonstrates how to read a chunk from a CSV file, process it, and save the result to a new file. It showcases how to extract data from the chunk, perform computations, and write the processed result to an output file.

5. **orchestration.py**: This script serves as the main file of the demonstration, orchestrating the different parts together. It demonstrates the end-to-end workflow of using Google Cloud Batch Jobs for compute-intensive tasks. The script generates a large CSV file using the generate_large_csv script, splits it into smaller chunks using the split_csv_into_chunks script, uploads the chunks to a Cloud Storage bucket, and creates a batch job using the create_script_job_with_bucket script to process the chunks. It leverages the functionality provided by the other scripts and includes an example usage to illustrate the workflow.

## Usage
In order to run this demo, you will need to have a Google Cloud account and a project with the Batch Jobs API enabled. You will also need to install the Google Cloud SDK and set up authentication. Please refer to the [Google Cloud documentation](https://cloud.google.com/sdk/docs/quickstart) for more information on how to set up the SDK and authentication.

### Setting Up the Environment
1. The first step is to clone the repository and install the required dependencies. You can do this by running the following commands:
```bash
git clone <repo>
cd <repo>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Then, create a bucket for storing the CSV, it's chunks and the output of the batch job. This bucket should contain the process_chunk script and it's requirements.txt file. You can create a bucket using the following command:
```bash
gsutil mb -l <region> gs://<bucket_name>
```

3. To upload the process_chunk script and it's requirements.txt file to the bucket, run the following commands:
```bash
gsutil cp -r ./process_chunk/   gs://<bucket_name>/scripts
```

4. Next, take the .env.example file and rename it to .env. Then, fill in the values for the environment variables in the .env file. The environment variables are used to configure the batch job and the Cloud Storage bucket. The following table provides a description of each environment variable:

| Variable Name | Description |
| ------------- | ----------- |
| GOOGLE_CLOUD_PROJECT | The ID of the Google Cloud project where the batch job will be created. |
| GOOGLE_CLOUD_REGION | The region where the batch job will be executed. |
| GOOGLE_CLOUD_BUCKET_NAME | The name of the Cloud Storage bucket where the CSV chunks are uploaded. |

5. Finally, once all the environment variables are set, you can run the orchestration script to execute the end-to-end workflow. You can do this by running the following command:
```bash
python orchestration.py
```

## Detailed Explanation: batch_jobs.py

The `batch_jobs.py` script is a crucial part of the repository, as it demonstrates how to create and configure batch jobs using the Google Cloud Batch Jobs API. This script provides a function called `create_script_job_with_bucket` that allows you to create a sample batch job for executing a custom command on Cloud Compute instances. Let's explore the different aspects of this script in detail:

### Purpose

The `batch_jobs.py` script aims to showcase the creation and configuration of batch jobs using the Google Cloud Batch Jobs API. It provides a function that demonstrates how to define the necessary specifications, resources, and settings for a batch job. Below is a detailed explanation of what the script does:

#### Importing Required Libraries
The script starts by importing the necessary libraries:
```python
from google.cloud import batch_v1
```

The `google.cloud.batch_v1` module is imported to access the Batch Jobs API.

#### Function create_script_job_with_bucket
The script defines a function named create_script_job_with_bucket that creates and configures a batch job. Let's go through the function step by step:

#### Function Parameters

The create_script_job_with_bucket function accepts the following parameters:
- **project_id (str)**: The ID of the Google Cloud project where the batch job will be created.
- **region (str)**: The region where the batch job will be executed.
- **job_name (str)**: The name of the batch job.
- **bucket_name (str)**: The name of the Cloud Storage bucket where the CSV chunks are uploaded.
- **command (str)**: The custom command to be executed by the batch job.
- **num_tasks (int)**: The number of parallel tasks to be executed.

These parameters provide the necessary information for creating and configuring the batch job according to the desired specifications.
Feel free to modify these parameters to suit your needs.

#### Initializing Batch Service Client
The function initializes an instance of `batch_v1.BatchServiceClient()` to interact with the Batch Jobs API:
```python
client = batch_v1.BatchServiceClient()
```

#### Task Configuration
The function defines a task object of type `batch_v1.TaskSpec()` that represents the configuration for the tasks to be executed in the job:
```python
task = batch_v1.TaskSpec()
```

Inside the task object, a runnable object of type batch_v1.Runnable() is created, which represents the command or script to be executed by the task:
```python
runnable = batch_v1.Runnable()
runnable.script = batch_v1.Runnable.Script()
```

The `runnable.script.text` property is set to the custom_command provided as a parameter, representing the command or script to be executed by the task. In this example the script with the task logic along with it's requirements.txt has been uploaded to the Google Cloud Storage Bucket that is mounted on the instance. It is important to note that the command that we pass to the batch job is the command that will be executed on the instance, so we need to make sure that whatever we execute, is available on the filesystem of the instance.

#### Input and Output Files
The function configures the input and output files for the batch job by specifying a Cloud Storage bucket and the mount path:
```python
gcs_bucket = batch_v1.GCS()
gcs_bucket.remote_path = bucket_name
gcs_volume = batch_v1.Volume()
gcs_volume.gcs = gcs_bucket
gcs_volume.mount_path = "/mnt/share"
task.volumes = [gcs_volume]
```

This configuration enables the task to access files stored in the specified bucket and mount them at the specified path.

#### Resource Requirements
The function sets the resource requirements for the tasks by configuring the `task.compute_resource` object:
```python
resources = batch_v1.ComputeResource()
resources.cpu_milli = 500
resources.memory_mib = 16
task.compute_resource = resources
```

- `resources.cpu_milli` specifies the CPU requirement in milliseconds per CPU-second. In this case, the task requires 50% of a single CPU.
- `resources.memory_mib` specifies the memory requirement in Mebibytes (MiB).

#### Task Retry and Duration
The function sets the maximum retry count and maximum run duration for the tasks:
```python
task.max_retry_count = 2
task.max_run_duration = "3600s"
```

- `task.max_retry_count` specifies the maximum number of times a task can be retried if it fails.
- `task.max_run_duration` specifies the maximum duration the task is allowed to run.

#### Task Group Configuration
Tasks are grouped inside a job using TaskGroups. The function creates a group object of type `batch_v1.TaskGroup()` and configures it:
```python
group = batch_v1.TaskGroup()
group.task_count = num_of_parallel_tasks
group.task_spec = task
```

- `group.task_count` specifies the number of parallel tasks to be executed.
- `group.task_spec` references the task configuration defined earlier.

#### Allocation Policy
The function configures the allocation policy for the job, specifying the virtual machine type for the tasks:
```python
allocation_policy = batch_v1.AllocationPolicy()
policy = batch_v1.AllocationPolicy.InstancePolicy()
policy.machine_type = "e2-standard-4"
instances = batch_v1.AllocationPolicy.InstancePolicyOrTemplate()
instances.policy = policy
allocation_policy.instances = [instances]
```
- `policy.machine_type` specifies the machine type to be used for the tasks. In this case, "e2-standard-4" is used.

#### Job Configuration
The function creates a job object of type `batch_v1.Job()` and configures it:
```python
job = batch_v1.Job()
job.task_groups = [group]
job.allocation_policy = allocation_policy
job.labels = {"env": "testing", "type": "script", "mount": "bucket"}
job.logs_policy = batch_v1.LogsPolicy()
job.logs_policy.destination = batch_v1.LogsPolicy.Destination.CLOUD_LOGGING
```

- `job.task_groups` references the group configuration defined earlier.
- `job.allocation_policy` references the allocation policy configuration.
- `job.labels` sets labels for the job, which can be used for identification or categorization purposes.
- `job.logs_policy` configures the logging policy for the job. In this case, it specifies that the logs should be sent to Cloud Logging.

#### Create Job Request
The function creates a create_request object of type `batch_v1.CreateJobRequest()` and configures it:
```python
create_request = batch_v1.CreateJobRequest()
create_request.job = job
create_request.job_id = job_name
create_request.parent = f"projects/{project_id}/locations/{region}"
```

- `create_request.job` references the job configuration.
- `create_request.job_id` specifies the ID of the job.
- `create_request.parent` specifies the parent resource of the job, which includes the project ID and region.

#### Submitting the Job
The function submits the job for execution by calling the client.create_job method:
```python
return client.create_job(create_request)
```

The create_job method sends a request to the Batch Jobs API to create the specified batch job with the provided configurations. It returns a Job object representing the created job.

## Conclusion

The `batch_jobs.py` script is a crucial component of this repository, demonstrating how to create and configure batch jobs using the Google Cloud Batch Jobs API. The `create_script_job_with_bucket` function showcases the process of defining the specifications, resources, and settings for a batch job, and submits the job for execution. By understanding the detailed explanation of this script, users can leverage the provided example to integrate Google Cloud Batch Jobs into their own compute-intensive workflows.