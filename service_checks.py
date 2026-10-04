"""Read-only provider diagnostics. Never return exception text or credentials."""
import os,json
import httpx

def check_mux():
    with httpx.Client(timeout=10) as client:
        r=client.get('https://api.mux.com/video/v1/assets',params={'limit':1},auth=(os.environ['MUX_TOKEN_ID'],os.environ['MUX_TOKEN_SECRET']))
        r.raise_for_status()
    return 'Aksè Mux verifye.'

def check_storage():
    import boto3
    from botocore.config import Config
    client=boto3.client('s3',endpoint_url=os.environ['S3_ENDPOINT_URL'],region_name=os.environ['S3_REGION'],aws_access_key_id=os.environ['S3_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['S3_SECRET_ACCESS_KEY'],config=Config(signature_version='s3v4',connect_timeout=5,read_timeout=10,retries={'max_attempts':0},request_checksum_calculation='when_required'))
    for bucket in [os.environ['S3_BUCKET'],os.environ['PRIVATE_SUBMISSION_BUCKET']]:
        client.head_bucket(Bucket=bucket)
    return 'Aksè de bucket yo verifye; teste chajman yon foto tou.'

def check_firebase():
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    public=json.loads(os.environ['FIREBASE_PUBLIC_CONFIG'])
    private=json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])
    if public.get('projectId')!=private.get('project_id'):
        raise ValueError('project mismatch')
    credentials=service_account.Credentials.from_service_account_info(private,scopes=['https://www.googleapis.com/auth/firebase.messaging'])
    transport=Request()
    credentials.refresh(lambda **kwargs: transport(**dict(kwargs,timeout=10)))
    return 'Otantifikasyon Firebase verifye; livrezon notifikasyon poko teste.'

def run_check(name):
    try:return {'ok':True,'message':{'Mux':check_mux,'Storage':check_storage,'Firebase':check_firebase}[name]()}
    except Exception:return {'ok':False,'message':'Tès la echwe. Verifye kle yo, dwa aksè ak koneksyon sèvis la.'}
