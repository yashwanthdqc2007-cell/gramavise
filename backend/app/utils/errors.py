from fastapi import HTTPException, status


class GramaViseException(Exception):
    """Base exception for application domain errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class EntityNotFoundException(GramaViseException):
    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidFinancialParametersException(GramaViseException):
    def __init__(self, details: list):
        super().__init__(
            message=f"Financial parameters validation failed: {', '.join(details)}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
