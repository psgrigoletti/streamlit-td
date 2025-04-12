import os
from dotenv import load_dotenv
from pathlib import Path


# Carregar variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


# Configurações da API do Tesouro Direto
TESOURO_API_URL = os.getenv(
    'TESOURO_API_URL',
    'https://www.tesourotransparente.gov.br/ckan/dataset/'
    'df56aa42-484a-4a59-8184-7676580c81e3/resource/'
    '796d2059-14e9-44e3-80c9-2d9e30b405c1/download/'
    'PrecoTaxaTesouroDireto.csv'
)

# Configurações da API do BCB
BCB_API_URL = os.getenv(
    'BCB_API_URL',
    'https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados'
)

# Configurações de email
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Configurações de cache
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hora em segundos

# Configurações do Redis
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Segurança
USUARIO = os.getenv('USUARIO')
SENHA = os.getenv('SENHA')