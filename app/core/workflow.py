from typing import Set, Dict
from app.core.enums import LoanStatus

class InvalidStateTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass

class LoanWorkflowStateMachine:
    """
    Finite State Machine managing enterprise credit approval lifecycle.
    """
    
    _ALLOWED_TRANSITIONS: Dict[LoanStatus, Set[LoanStatus]] = {
        LoanStatus.DRAFT: {LoanStatus.SUBMITTED, LoanStatus.REJECTED},
        LoanStatus.SUBMITTED: {LoanStatus.CREDIT_REVIEW, LoanStatus.REJECTED},
        LoanStatus.CREDIT_REVIEW: {LoanStatus.APPROVED, LoanStatus.REJECTED},
        LoanStatus.APPROVED: {LoanStatus.DISBURSED, LoanStatus.REJECTED},
        LoanStatus.DISBURSED: {LoanStatus.ACTIVE},
        LoanStatus.ACTIVE: {LoanStatus.SETTLED, LoanStatus.DEFAULTED},
        LoanStatus.SETTLED: set(),
        LoanStatus.DEFAULTED: {LoanStatus.SETTLED},
        LoanStatus.REJECTED: set(),
    }

    @classmethod
    def can_transition(cls, current_status: LoanStatus, target_status: LoanStatus) -> bool:
        allowed = cls._ALLOWED_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def validate_transition(cls, current_status: LoanStatus, target_status: LoanStatus) -> None:
        if not cls.can_transition(current_status, target_status):
            raise InvalidStateTransitionError(
                f"Cannot transition loan from '{current_status.value}' to '{target_status.value}'. "
                f"Allowed target states: {[s.value for s in cls._ALLOWED_TRANSITIONS.get(current_status, set())]}"
            )
