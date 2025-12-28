# app/services/razorpay_service.py
import razorpay
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

class RazorpayService:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
    
    def create_order(self, amount: float, currency: str = "INR", 
                    receipt: str = None, notes: dict = None):
        """
        Create a new order in Razorpay
        amount: Amount in smallest currency unit (paise for INR)
        """
        try:
            # Convert amount to paise (for INR)
            amount_in_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_in_paise,
                "currency": currency,
                "payment_capture": 1  # Auto capture payment
            }
            
            if receipt:
                order_data["receipt"] = receipt
            
            if notes:
                order_data["notes"] = notes
            
            order = self.client.order.create(data=order_data)
            return order
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")
    
    def verify_payment(self, razorpay_payment_id: str, razorpay_order_id: str, 
                      razorpay_signature: str):
        """Verify payment signature"""
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def fetch_order(self, order_id: str):
        """Fetch order details"""
        try:
            return self.client.order.fetch(order_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

razorpay_service = RazorpayService()