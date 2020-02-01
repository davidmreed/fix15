import fix15
import boto3
import tempfile
import json
import os
import uuid
from flask import Flask, request, jsonify, render_template, session, url_for
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['REDIS_URL']
app.config['CELERY_RESULT_BACKEND'] = os.environ['REDIS_URL']
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['BUCKET_NAME'] = os.environ['BUCKET_NAME']

celery = Celery(app.name)
celery.conf.update(app.config)

@celery.task(bind=True)
def process_s3_file(self, file_name, original_file_name):
    bucket = boto3.resource('s3').Bucket(app.config['BUCKET_NAME'])

    # Pull down the input file from S3.
    # Input file name will have been uniqued to a GUID.
    bucket.download_file(file_name, file_name)

    # Get the size of the downloaded file
    file_size = os.stat(file_name).ST_SIZE

    # Generate a unique converted file name.
    uniqued_name = uuid.uuid4() + '.csv'

    with tempfile.NamedTemporaryFile(encoding='utf-8') as output_file:
        with open(file_name, 'rb') as input_file:
            fix15.process_file(input_file, 
                               output_file, 
                               skip_headers=True, 
                               progress=lambda bytes: self.update_state('PROGRESS', meta={ 'progress': bytes/file_size }))

        bucket.upload_file(output_file.name, 'outputs/' + uniqued_name)

    self.update_state('SUCCESS', 
                      meta={ 
                          'result_url': 'https://%s.s3.amazonaws.com/outputs/%s' % (app.config['BUCKET_NAME'], uniqued_name),
                          'download_name': os.path.splitext(original_file_name)[0] + '.fix15.csv'
                      }
                     )

@app.route('/', methods=['GET', 'POST'])
def index():
    pass

@app.route('/sign_s3/')
def sign_s3():
    S3_BUCKET = app.config['BUCKET_NAME']

    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')

    uniqued_name = uuid.uuid4() + '.csv'

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = uniqued_name,
        Fields = {"acl": "private", "Content-Type": 'text/csv'},
        Conditions = [
            {"acl": "private"},
            {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )

    return json.dumps({
        'data': presigned_post,
        'filename': uniqued_name,
        'url': 'https://%s.s3.amazonaws.com/inputs/%s' % (S3_BUCKET, uniqued_name)
    })


@app.route('/process_csv', methods=['POST'])
def process():
    task = process_s3_file.apply_async()

    return jsonify({}), 202, {'Location': Flask.url_for('get_progress', task_id=task.id)}

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
            'status': 'Done',
            'result_url': task.info.get('result_url'),
            'download_name': task.info.get('download_name')
        }
    elif task.state == 'FAILURE':
        # something went wrong in the background job
        response = {
            'state': task.state,
            'progress': 0,
            'status': str(task.info),  # this is the exception raised
        }
    
    return jsonify(response)
