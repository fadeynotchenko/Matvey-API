from dotenv import load_dotenv
from urllib.parse import quote_plus as quote
import os

load_dotenv()

user = str(os.getenv('DB_USER'))
password = str(os.getenv('PASSWORD'))
host = str(os.getenv('HOST'))
replica_set = str(os.getenv('REPLICA_SET'))
auth_source = str(os.getenv('AUTH_SOURCE'))
tls_ca_file = str(os.getenv('TLS_CA_FILE'))
db_client = str(os.getenv('DB_CLIENT'))

# Формирование URL для подключения
url = f'mongodb://{quote(user)}:{quote(password)}@{host}/?replicaSet={replica_set}&authSource={auth_source}'

