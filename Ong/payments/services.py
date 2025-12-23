from django.conf import settings
from django.utils.crypto import get_random_string
import requests
import json

class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = "https://api.paystack.co"
    
    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache',
        }
    
    def initialize_transaction(self, email, amount, reference, callback_url=None, channels=None):
        """Initialize a Paystack transaction
        
        channels can include: ['card', 'bank', 'ussd', 'qr', 'mobile_money', 'bank_transfer']
        - 'bank_transfer' enables Pay with Transfer (Dedicated Virtual Account)
        """
        url = f"{self.base_url}/transaction/initialize"
        
        payload = {
            'email': email,
            'amount': int(amount * 100),  # Paystack expects amount in kobo
            'reference': reference,
            'callback_url': callback_url,
            'currency': 'NGN'
        }
        
        # Add payment channels if specified
        if channels:
            payload['channels'] = channels
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )
            
            print(f"Paystack Response Status: {response.status_code}")
            print(f"Paystack Response: {response.text[:500]}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': False, 
                    'message': f'HTTP Error {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.Timeout:
            print("Paystack Error: Request timed out")
            return {'status': False, 'message': 'Request timed out. Please try again.'}
        except requests.exceptions.ConnectionError as e:
            print(f"Paystack Connection Error: {str(e)}")
            return {'status': False, 'message': 'Connection error. Please check your internet connection.'}
        except Exception as e:
            print(f"Paystack Error: {str(e)}")
            return {'status': False, 'message': str(e)}
    
    def verify_transaction(self, reference):
        """Verify a Paystack transaction"""
        url = f"{self.base_url}/transaction/verify/{reference}"
        
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': False,
                    'message': f'HTTP Error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {'status': False, 'message': str(e)}
    
    def create_transfer_recipient(self, name, account_number, bank_code):
        """Create a transfer recipient for restaurant payouts"""
        url = f"{self.base_url}/transferrecipient"
        
        payload = {
            'type': 'nuban',
            'name': name,
            'account_number': account_number,
            'bank_code': bank_code,
            'currency': 'NGN'
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': False,
                    'message': f'HTTP Error {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {'status': False, 'message': str(e)}
    
    def list_banks(self):
        """List all Nigerian banks"""
        url = f"{self.base_url}/bank"
        
        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': False, 'message': f'HTTP Error {response.status_code}'}
                
        except Exception as e:
            return {'status': False, 'message': str(e)}


def generate_payment_reference():
    """Generate unique payment reference"""
    return f"PAY_{get_random_string(10).upper()}"
