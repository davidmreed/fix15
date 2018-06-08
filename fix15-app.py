import fix15
import boto3
import tempfile
import os
from flask import Flask, request, jsonify, render_template, session, url_for
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['REDIS_URL']
app.config['CELERY_RESULT_BACKEND'] = os.environ['REDIS_URL']
app.config['CELERY_TASK_SERIALIZER' = 'json'

celery = Celery(app.name)
celery.conf.update(app.config)

@celery.task(bind=True)
def process_s3_file(self, file_name):
    bucket = boto3.resource('s3').Bucket(BUCKET_NAME)

    # Pull down the input file from S3.
    # Input file name will have been uniqued to a GUID.
    bucket.download_file(file_name, file_name)

    # Get the size of the downloaded file
    file_size = os.stat(file_name).ST_SIZE

    with tempfile.NamedTemporaryFile(encoding='utf-8') as output_file:
        with open(file_name, 'rb') as input_file:
            fix15.process_file(input_file, 
                            output_file, 
                            skip_headers=True, 
                            progress=lambda bytes: self.update_state('PROGRESS', meta={ 'progress': bytes/file_size }))

        bucket.upload_file(output_file.name, output_file.name)

@app.route('/', methods=['GET', 'POST'])
def index():
    pass

@app.route('/sign_s3/')
def sign_s3():
    S3_BUCKET = os.environ.get('S3_BUCKET')

    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = {"acl": "public-read", "Content-Type": file_type},
        Conditions = [
            {"acl": "public-read"}, # FIXME: is this correct?
            {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )

    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })


@app.route('/process_csv', methods=['POST'])
def process():
    task = process_s3_file.apply_async()

    return jsonify({}), 202, {'Location': flask.url_for('get_progress', task_id=task.id)}

@app.route('/status/<task_id>')
def get_progress(task_id):
    task = process_s3_file.AsyncResult(task_id)

    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'progress': 0,
            'status': 'Waiting...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'progress': task.info.get('progress'),
            'status': 'Processing...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'progress': 100,
            'status': 'Done'
            # Include the link to S3 here.
        }
    elif task.state == 'FAILURE':
        # something went wrong in the background job
        response = {
            'state': task.state,
            'progress': 0,
            'status': str(task.info),  # this is the exception raised
        }
    
    return jsonify(response)
