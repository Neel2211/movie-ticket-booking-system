from fastapi import APIRouter, Depends, Header, HTTPException, status, Response
from sqlalchemy.orm import Session
import uuid
import json

from app.database import get_db
from app.models import PaymentModel
from app.schemas import PaymentCreateRequest, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def process_payment(
    payload: PaymentCreateRequest,
    response: Response,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db)
):
    # Challenge 2: Idempotency Check
    existing_payment = db.query(PaymentModel).filter(PaymentModel.idempotency_key == idempotency_key).first()
    if existing_payment:
        # If a cached response exists, return it to prevent duplicate charges/actions
        if existing_payment.response_payload:
            return json.loads(existing_payment.response_payload)
        
        return existing_payment

    # Simulate Mock Payment Gateway logic (Condition 1e / Challenge 3A/3C)
    gateway_status = "SUCCESS"
    gateway_tx_id = f"txn_{uuid.uuid4().hex[:12]}"
    
    if payload.amount <= 0:
        gateway_status = "FAILED"
        gateway_tx_id = None

    new_payment = PaymentModel(
        booking_id=payload.booking_id,
        amount=payload.amount,
        currency=payload.currency,
        status=gateway_status,
        gateway_transaction_id=gateway_tx_id,
        idempotency_key=idempotency_key
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Cache response payload as JSON string for safe idempotent replays
    # We dump using model_dump() with mode='json' so datetime serializes cleanly
    resp_obj = PaymentResponse.model_validate(new_payment)
    new_payment.response_payload = json.dumps(resp_obj.model_dump(mode="json"))
    db.commit()

    return new_payment

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_status(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return payment

@router.get("/booking/{booking_id}", response_model=PaymentResponse)
def get_payment_by_booking(booking_id: int, db: Session = Depends(get_db)):
    payment = db.query(PaymentModel).filter(PaymentModel.booking_id == booking_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record for this booking not found")
    return payment

@router.post("/{payment_id}/refund", status_code=status.HTTP_200_OK)
def compensate_payment_saga(payment_id: int, db: Session = Depends(get_db)):
    """
    SAGA Compensation Endpoint: 
    Triggers a refund/rollback for a given payment if a downstream service fails.
    """
    payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    if payment.status == "REFUNDED":
        return {"message": "Payment already refunded", "payment_id": payment.id, "status": "REFUNDED"}
    
    # Update payment status to REFUNDED (Compensating action)
    payment.status = "REFUNDED"
    db.commit()
    db.refresh(payment)
    
    return {
        "message": "SAGA Compensation executed successfully: Payment refunded.",
        "payment_id": payment.id,
        "booking_id": payment.booking_id,
        "status": payment.status,
        "gateway_transaction_id": payment.gateway_transaction_id
    }