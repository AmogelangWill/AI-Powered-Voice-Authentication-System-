from fastapi import HTTPException, status


def unauthorized(detail: str = "Unauthorized") -> HTTPException:
    # Centralized unauthorized response constructor.
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def bad_request(detail: str) -> HTTPException:
    # Centralized bad-request response constructor.
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
