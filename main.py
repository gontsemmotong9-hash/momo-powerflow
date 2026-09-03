import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

# Configuration (Replace with actual credentials in production or sandbox env)
MOMO_BASE_URL = "https://sandbox.momodevelopment.mtn.com"
PRIMARY_KEY = "your_subscription_primary_key"
API_USER_ID = "your_api_user_uuid"
API_SECRET = "your_api_secret"
TARGET_ENVIRONMENT = "sandbox"  # Use 'mtnsandbox' or production env as needed

class PaymentRequest(BaseModel):
    meter_number: str
    phone_number: str  # Format: e.g., "27788033288"
    amount: str        # Format: e.g., "50"

async def get_momo_access_token(client: httpx.AsyncClient) -> str:
    """Fetch bearer token using Basic Auth (API User ID + API Secret)."""
    url = f"{MOMO_BASE_URL}/collection/token/"
    headers = {
        "Ocp-Apim-Subscription-Key": PRIMARY_KEY
    }
    response = await client.post(
        url, 
        auth=(API_USER_ID, API_SECRET), 
        headers=headers
    )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, 
            detail="Failed to authenticate with MoMo API"
        )
    
    return response.json().get("access_token")

@app.post("/api/momo/request-to-pay")
async def request_to_pay(payload: PaymentRequest) -> Dict[str, Any]:
    reference_id = str(uuid.uuid4())
    
    async with httpx.AsyncClient() as client:
        # Step 1: Obtain Authorization Token
        access_token = await get_momo_access_token(client)
        
        # Step 2: Prepare Request to Pay
        url = f"{MOMO_BASE_URL}/collection/v1_0/requesttopay"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": TARGET_ENVIRONMENT,
            "Ocp-Apim-Subscription-Key": PRIMARY_KEY,
            "Content-Type": "application/json"
        }
        
        body = {
            "amount": payload.amount,
            "currency": "ZAR",  # Set currency code as per target environment
            "externalId": f"METER_{payload.meter_number}",
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": payload.phone_number
            },
            "payerMessage": f"Electricity recharge for meter {payload.meter_number}",
            "payeeNote": "MoMo PowerFlow Purchase"
        }
        
        # Step 3: Send Payment Initiation Request
        response = await client.post(url, json=body, headers=headers)
        
        # HTTP 202 Accepted indicates the transaction request has been successfully queued
        if response.status_code == 202:
            return {
                "status": "PENDING",
                "reference_id": reference_id,
                "message": "Payment request initiated successfully. Awaiting user authorization."
            }
        
        raise HTTPException(
            status_code=response.status_code, 
            detail=f"MoMo Request Failed: {response.text}"
        )