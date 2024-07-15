import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MySecretKey'
    os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY') or 'sk-proj-vHbGimMSVyxKKCd0KKVXT3BlbkFJ7jH1F0rVIQAvJPokrAN7'
    # Ajoutez d'autres configurations si nécessaire
