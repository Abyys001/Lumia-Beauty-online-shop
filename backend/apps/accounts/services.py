import requests
from django.conf import settings


class KavenegarService:
  BASE_URL = 'https://api.kavenegar.com/v1'

  @classmethod
  def send_otp(cls, phone: str, code: str) -> bool:
    api_key = settings.KAVENEGAR_API_KEY
    if not api_key:
      return settings.DEBUG

    url = f'{cls.BASE_URL}/{api_key}/verify/lookup.json'
    try:
      response = requests.post(
        url,
        data={
          'receptor': phone,
          'token': code,
          'template': settings.KAVENEGAR_TEMPLATE,
        },
        timeout=10,
      )
      return response.status_code == 200
    except requests.RequestException:
      return False
