from pydantic import BaseModel
from enum import Enum

class PaymentState(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"

class Payment(BaseModel):
    paymentId: str | None = None
    userId: str
    created: str | None = None
    processed: str | None = None
    state: PaymentState = PaymentState.PENDING
    accountNumber: str
    amount: float
    description: str | None = None
    extPaymentDetails: str | None = None