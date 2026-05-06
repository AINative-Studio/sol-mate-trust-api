from fastapi import HTTPException, status


class SolMateError(HTTPException):
    pass


class UserNotFoundError(SolMateError):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class PersonaNotFoundError(SolMateError):
    def __init__(self):
        super().__init__(status_code=404, detail="Persona not found")


class PersonaExpiredError(SolMateError):
    def __init__(self):
        super().__init__(status_code=403, detail="Persona has expired")


class RoomNotFoundError(SolMateError):
    def __init__(self):
        super().__init__(status_code=404, detail="Room not found")


class RoomAccessDeniedError(SolMateError):
    def __init__(self, reason: str = "Access denied"):
        super().__init__(status_code=403, detail=reason)


class StakeRequiredError(SolMateError):
    def __init__(self, amount: float, action: str):
        super().__init__(
            status_code=402,
            detail=f"Stake of {amount} USDC required to {action}",
        )


class StakeNotFoundError(SolMateError):
    def __init__(self):
        super().__init__(status_code=404, detail="Stake not found")


class InsufficientStakeError(SolMateError):
    def __init__(self, required: float, provided: float):
        super().__init__(
            status_code=402,
            detail=f"Insufficient stake: {provided} USDC provided, {required} USDC required",
        )


class MatchNotFoundError(SolMateError):
    def __init__(self):
        super().__init__(status_code=404, detail="Match not found")


class MessagingBlockedError(SolMateError):
    def __init__(self, reason: str):
        super().__init__(status_code=403, detail=f"Messaging blocked: {reason}")


class ConsentRequiredError(SolMateError):
    def __init__(self):
        super().__init__(status_code=403, detail="Consent has not been granted")


class BlockedUserError(SolMateError):
    def __init__(self):
        super().__init__(status_code=403, detail="This user has been blocked")


class AttestationError(SolMateError):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class EscrowError(SolMateError):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class SafetyError(SolMateError):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)
