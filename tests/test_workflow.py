import unittest
from app.core.workflow import LoanWorkflowStateMachine, InvalidStateTransitionError
from app.core.enums import LoanStatus

class TestLoanWorkflow(unittest.TestCase):
    def test_valid_workflow_transitions(self):
        self.assertTrue(LoanWorkflowStateMachine.can_transition(LoanStatus.DRAFT, LoanStatus.SUBMITTED))
        self.assertTrue(LoanWorkflowStateMachine.can_transition(LoanStatus.SUBMITTED, LoanStatus.CREDIT_REVIEW))
        self.assertTrue(LoanWorkflowStateMachine.can_transition(LoanStatus.CREDIT_REVIEW, LoanStatus.APPROVED))
        self.assertTrue(LoanWorkflowStateMachine.can_transition(LoanStatus.APPROVED, LoanStatus.DISBURSED))
        self.assertTrue(LoanWorkflowStateMachine.can_transition(LoanStatus.DISBURSED, LoanStatus.ACTIVE))
        self.assertTrue(LoanWorkflowStateMachine.can_transition(LoanStatus.ACTIVE, LoanStatus.SETTLED))

    def test_invalid_workflow_transitions(self):
        with self.assertRaises(InvalidStateTransitionError):
            LoanWorkflowStateMachine.validate_transition(LoanStatus.DRAFT, LoanStatus.DISBURSED)
        
        with self.assertRaises(InvalidStateTransitionError):
            LoanWorkflowStateMachine.validate_transition(LoanStatus.SETTLED, LoanStatus.ACTIVE)

if __name__ == "__main__":
    unittest.main()

