# Using Spark SQL Streaming with Pub/Sub Lite

The samples in this directory show how to read messages from and write messages to Pub/Sub Lite from an [Apache Spark] cluster using the [Pub/Sub Lite Spark Connector].

Visit this Maven [link](https://search.maven.org/artifact/com.google.cloud/pubsublite-spark-sql-streaming) to download the connector's uber jar. The uber jar has a "with-dependencies" suffix. You will need to include it on the driver and executor classpaths when submitting a Spark job, typically in the `--jars` flag.

## Before you begin

1. Install the [Cloud SDK].
   > *Note:* This is not required in [Cloud Shell]
   > because Cloud Shell has the Cloud SDK pre-installed.

1. Create a new Google Cloud project via the
   [*New Project* page] or via the `gcloud` command line tool.

   ```sh
   export PROJECT_ID=your-google-cloud-project-id
   gcloud projects create $PROJECT_ID
   ```
   Or use an existing Google Cloud project.
   ```sh
   export PROJECT_ID=$(gcloud config get-value project)
   ```

1. [Enable billing].

1. Setup the Cloud SDK to your GCP project.

   ```sh
   gcloud init
   ```

1. [Enable the APIs](https://console.cloud.google.com/flows/enableapi?apiid=pubsublite,dataproc,storage_component): Pub/Sub Lite, Dataproc, Cloud Storage.

1. Create a Pub/Sub Lite [topic] and [subscription] in a supported [location].

   ```bash
   export TOPIC_ID=your-topic-id
   export SUBSCRIPTION_ID=your-subscription-id
   export LOCATION=your-location

   gcloud pubsub lite-topics create $TOPIC_ID \
     --location=$LOCATION \
     --partitions=1 \
     --per-partition-bytes=30GiB

   gcloud pubsub lite-subscriptions create $SUBSCRIPTION_ID \
      --location=$LOCATION \
      --topic=$TOPIC_ID
   ```

1. Create a Cloud Storage bucket.

   ```bash
   export BUCKET_ID=your-gcs-bucket-id

   gsutil mb gs://$BUCKET_ID
   ```

## Python setup

1. [Install Python and virtualenv].

1. Clone the `python-docs-samples` repository.

    ```bash
    git clone https://github.com/GoogleCloudPlatform/python-docs-samples.git
    ```

1. Navigate to the sample code directory.

    ```bash
    cd python-docs-samples/pubsublite/spark-connector
    ```

1. Create a virtual environment and activate it.

    ```bash
    virtualenv env
    source env/bin/activate
    ```
   > Once you are finished with the tutorial, you can deactivate
   > the virtualenv and go back to your global Python environment
   > by running `deactivate`.

1. Install the required packages.
    ```bash
    python -m pip install -U -r requirements.txt
    ```

## Creating a Spark cluster on Dataproc

1. Go to [Cloud Console for Dataproc].

1. Go to Clusters, then [Create Cluster].
   > **Note:** When setting up the cluster, you must choose
   > [Dataproc Image Version 1.5] under ___Versioning___ because
   > the connector currently only supports Spark 2.4.8.
   > Additionally, in ___Manage security (optional)___, you
   > must enable the cloud-platform scope for your cluster by
   > checking "Allow API access to all Google Cloud services in
   > the same project" under ___Project access___.

   Here is an equivalent example using a `gcloud` command, with an additional optional argument to enable component gateway:

    ```sh
    export CLUSTER_ID=your-cluster-id
    export CLOUD_REGION=your-region

    gcloud dataproc clusters create $CLUSTER_ID \
      --region $CLOUD_REGION \
      --image-version 1.5-debian10 \
      --scopes 'https://www.googleapis.com/auth/cloud-platform' \
      --enable-component-gateway
    ```

## Writing to Pub/Sub Lite

[spark_streaming_to_pubsublite_example.py](spark_streaming_to_pubsublite_example.py) creates a streaming source of consecutive numbers with timestamps for 60 seconds and writes them to a Pub/Sub topic.

To submit a write job:

```sh
export PROJECT_NUMBER=$(gcloud projects list --filter="projectId:$PROJECT_ID" --format="value(PROJECT_NUMBER)")

gcloud dataproc jobs submit pyspark spark_streaming_to_pubsublite_example.py \
    --region=$CLOUD_REGION \
    --cluster=$CLUSTER_ID \
    --jars=https://search.maven.org/remotecontent?filepath=com/google/cloud/pubsublite-spark-sql-streaming/0.3.1/pubsublite-spark-sql-streaming-0.3.1-with-dependencies.jar \
    --driver-log-levels=root=INFO \
    --properties=spark.master=yarn \
    -- $PROJECT_NUMBER $LOCATION $TOPIC_ID
```

The preceding command hardcodes the connector version. Visit this Maven [link](https://search.maven.org/artifact/com.google.cloud/pubsublite-spark-sql-streaming) to learn and download the latest version of the connector's uber jar.

Visit the job URL in the command output or the jobs panel in [Cloud Console for Dataproc] to monitor the job progress.

## Reading from Pub/Sub Lite

[spark_streaming_from_pubsublite_example.py](spark_streaming_from_pubsublite_example.py) reads messages formatted as dataframe rows from a Pub/Sub subscription and prints them out to the console.

To submit a read job:

```sh
gcloud dataproc jobs submit pyspark spark_streaming_from_pubsublite_example.py \
    --region=$CLOUD_REGION \
    --cluster=$CLUSTER_ID \
    --jars=https://search.maven.org/remotecontent?filepath=com/google/cloud/pubsublite-spark-sql-streaming/0.3.1/pubsublite-spark-sql-streaming-0.3.1-with-dependencies.jar \
    --driver-log-levels=root=INFO \
    --properties=spark.master=yarn \
    -- $PROJECT_NUMBER $LOCATION $SUBSCRIPTION_ID
```
The preceding command hardcodes the connector version. Visit this Maven [link](https://search.maven.org/artifact/com.google.cloud/pubsublite-spark-sql-streaming) to learn and download the latest version of the connector's uber jar.

Here is some example output:

```none
+--------------------+---------+------+---+----+--------------------+--------------------+----------+
|        subscription|partition|offset|key|data|   publish_timestamp|     event_timestamp|attributes|
+--------------------+---------+------+---+----+--------------------+--------------------+----------+
|projects/50200928...|        0| 89523|  0|   .|2021-09-03 23:01:...|2021-09-03 22:56:...|        []|
|projects/50200928...|        0| 89524|  1|   .|2021-09-03 23:01:...|2021-09-03 22:56:...|        []|
|projects/50200928...|        0| 89525|  2|   .|2021-09-03 23:01:...|2021-09-03 22:56:...|        []|
```

[Apache Spark]: https://spark.apache.org/
[Pub/Sub Lite Spark Connector]: https://github.com/googleapis/java-pubsublite-spark
[Cloud Console for Dataproc]: https://console.cloud.google.com/dataproc/

[Cloud SDK]: https://cloud.google.com/sdk/docs/
[Cloud Shell]: https://console.cloud.google.com/cloudshell/editor/
[*New Project* page]: https://console.cloud.google.com/projectcreate
[Enable billing]: https://cloud.google.com/billing/docs/how-to/modify-project/
[*Create service account key* page]: https://console.cloud.google.com/apis/credentials/serviceaccountkey/
[GCP Console IAM page]: https://console.cloud.google.com/iam-admin/iam/
[Granting roles to service accounts]: https://cloud.google.com/iam/docs/granting-roles-to-service-accounts/
[Creating and managing service accounts]: https://cloud.google.com/iam/docs/creating-managing-service-accounts/

[Install Python and virtualenv]: https://cloud.google.com/python/setup/
[Create Cluster]: https://pantheon.corp.google.com/dataproc/clustersAdd
[Dataproc Image Version 1.5]: https://cloud.google.com/dataproc/docs/concepts/versioning/dataproc-release-1.5
[location]: https://cloud.google.com/pubsub/lite/docs/locations
[topic]: https://cloud.google.com/pubsub/lite/docs/topics
[subscription]: https://cloud.google.com/pubsub/lite/docs/subscriptions