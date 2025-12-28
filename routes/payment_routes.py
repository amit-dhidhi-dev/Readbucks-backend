# # app/routes/payment_routes.py
# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.responses import JSONResponse
# from services.razorpay_service import razorpay_service
# from utils.token import verify_access_token
# import os

# router = APIRouter(prefix="/payments", tags=["payments"])

# @router.post("/create-order")
# async def create_payment_order(
#     amount: float,
#     currency: str = "INR",
#     token: str = None
# ):
#     """
#     Create a new payment order
#     """
#     try:
#         # Verify user token if provided
#         user_id = None
#         if token:
#             payload = verify_access_token(token)
#             user_id = payload.get("user_id")
        
#         # Create order in Razorpay
#         order = razorpay_service.create_order(
#             amount=amount,
#             currency=currency,
#             notes={"user_id": user_id} if user_id else {}
#         )
        
#         return {
#             "success": True,
#             "order_id": order["id"],
#             "amount": order["amount"],
#             "currency": order["currency"],
#             "key": os.getenv("RAZORPAY_KEY_ID")
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/verify-payment")
# async def verify_payment(
#     razorpay_payment_id: str,
#     razorpay_order_id: str,
#     razorpay_signature: str
# ):
#     """
#     Verify payment signature after successful payment
#     """
#     try:
#         is_valid = razorpay_service.verify_payment(
#             razorpay_payment_id=razorpay_payment_id,
#             razorpay_order_id=razorpay_order_id,
#             razorpay_signature=razorpay_signature
#         )
        
#         if is_valid:
#             # Payment is verified, you can save to database here
#             # await save_payment_details(razorpay_payment_id, razorpay_order_id)
            
#             return {
#                 "success": True,
#                 "message": "Payment verified successfully",
#                 "payment_id": razorpay_payment_id,
#                 "order_id": razorpay_order_id
#             }
#         else:
#             return {
#                 "success": False,
#                 "message": "Payment verification failed"
#             }
            
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/order/{order_id}")
# async def get_order_details(order_id: str):
#     """
#     Get order details by order ID
#     """
#     try:
#         order = razorpay_service.fetch_order(order_id)
#         return order
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# app/routes/payment_routes.py
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from services.razorpay_service import razorpay_service
from utils.token import verify_access_token
import os
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/payments", tags=["payments"])

# Pydantic models for request validation
class CreateOrderRequest(BaseModel):
    amount: float
    currency: Optional[str] = "INR"
    receipt: Optional[str] = None

class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

@router.post("/create-order")
async def create_payment_order(
    request_data: CreateOrderRequest = Body(...),
    token: Optional[str] = None
):
    """
    Create a new payment order
    """
    try:
        print(f"Received request: {request_data}")
        
        # Verify user token if provided
        user_id = None
        if token:
            try:
                payload = verify_access_token(token)
                user_id = payload.get("user_id")
            except Exception as e:
                print(f"Token verification error: {e}")
                # Continue without user_id if token is invalid
        
        # Create order in Razorpay
        order = razorpay_service.create_order(
            amount=request_data.amount,
            currency=request_data.currency,
            receipt=request_data.receipt,
            notes={"user_id": user_id} if user_id else {}
        )
        
        response_data = {
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": os.getenv("RAZORPAY_KEY_ID")
        }
        
        print(f"Order created: {response_data}")
        return response_data
        
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-payment")
async def verify_payment(request_data: VerifyPaymentRequest):
    """
    Verify payment signature after successful payment
    """
    try:
        print(f"Verifying payment: {request_data}")
        
        is_valid = razorpay_service.verify_payment(
            razorpay_payment_id=request_data.razorpay_payment_id,
            razorpay_order_id=request_data.razorpay_order_id,
            razorpay_signature=request_data.razorpay_signature
        )
        
        if is_valid:
            # Payment is verified, you can save to database here
            print(f"Payment verified: {request_data.razorpay_payment_id}")
            
            return {
                "success": True,
                "message": "Payment verified successfully",
                "payment_id": request_data.razorpay_payment_id,
                "order_id": request_data.razorpay_order_id
            }
        else:
            print(f"Payment verification failed: {request_data.razorpay_payment_id}")
            return {
                "success": False,
                "message": "Payment verification failed"
            }
            
    except Exception as e:
        print(f"Verification error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))