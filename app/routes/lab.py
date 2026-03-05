"""Lab routes with intentional vulnerabilities for DevSecOps training.

These endpoints are DISABLED by default (LAB_MODE=0).
They contain intentional security vulnerabilities for educational purposes.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, PlainTextResponse

from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lab", tags=["lab"])


def check_lab_mode() -> None:
    """Check if lab mode is enabled, raise 403 if not."""
    settings = get_settings()
    if not settings.lab_mode:
        raise HTTPException(
            status_code=403,
            detail="Lab endpoints are disabled. Set LAB_MODE=1 to enable."
        )


# VULNERABILITY 3: Open Redirect
# This endpoint is vulnerable to open redirect attacks
# Attackers can redirect users to malicious sites
@router.get("/unsafe-redirect")
def unsafe_redirect(next: Annotated[str, Query()] = "/") -> RedirectResponse:
    """
    Redirect to arbitrary URL - VULNERABLE TO OPEN REDIRECT!
    
    Example attack: /lab/unsafe-redirect?next=https://evil.com
    SAST tools like Semgrep can detect this pattern.
    """
    check_lab_mode()
    
    # VULNERABILITY: No validation of redirect target
    logger.warning(f"Redirecting to unvalidated URL: {next}")
    return RedirectResponse(url=next)


# FIX: Safe redirect with allowlist
# Uncomment the function below and comment out the one above:
#
# @router.get("/safe-redirect")
# def safe_redirect(next: Annotated[str, Query()] = "/") -> RedirectResponse:
#     """Redirect with URL validation."""
#     check_lab_mode()
#     
#     # Allowlist of safe redirect paths
#     allowed_paths = ["/", "/notes", "/health"]
#     allowed_hosts = ["localhost", "127.0.0.1"]
#     
#     # Parse and validate URL
#     from urllib.parse import urlparse
#     parsed = urlparse(next)
#     
#     # Only allow relative URLs or specific hosts
#     if parsed.netloc:
#         if parsed.netloc not in allowed_hosts:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Redirect to external sites not allowed"
#             )
#     
#     if parsed.path not in allowed_paths:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Redirect path not allowed. Allowed: {allowed_paths}"
#         )
#     
#     return RedirectResponse(url=next)


# VULNERABILITY 4: Unsafe input handling
# This endpoint uses eval() which is extremely dangerous
# SAST tools will flag this as critical vulnerability
@router.get("/echo")
def unsafe_echo(data: Annotated[str, Query()] = "hello") -> PlainTextResponse:
    """
    Echo endpoint with unsafe input handling - CRITICAL VULNERABILITY!
    
    This uses eval() which allows arbitrary code execution.
    Example attack: /lab/echo?data=__import__('os').system('whoami')
    """
    check_lab_mode()
    
    # VULNERABILITY: Using eval() on user input - NEVER DO THIS!
    try:
        # This is intentionally dangerous for demonstration
        result = eval(f"'{data}'.upper()")  # noqa: S307
        logger.warning(f"Unsafe eval executed on input: {data}")
        return PlainTextResponse(content=str(result))
    except Exception as e:
        logger.error(f"Error in unsafe eval: {e}")
        return PlainTextResponse(content=f"Error: {str(e)}", status_code=500)


# FIX: Safe input handling
# Uncomment the function below and comment out the one above:
#
# @router.get("/echo-safe")
# def safe_echo(data: Annotated[str, Query(max_length=100)] = "hello") -> PlainTextResponse:
#     """Echo endpoint with safe input handling."""
#     check_lab_mode()
#     
#     # Safe string manipulation - no code execution
#     # Validate and sanitize input
#     if not data.isprintable():
#         raise HTTPException(
#             status_code=400,
#             detail="Input contains non-printable characters"
#         )
#     
#     # Simple, safe string operation
#     result = data.upper()
#     logger.info(f"Safe echo processed: {data}")
#     return PlainTextResponse(content=result)


@router.get("/render")
def unsafe_render(template: Annotated[str, Query()] = "Hello {name}") -> dict[str, str]:
    """
    Template rendering with potential injection - VULNERABILITY!
    
    This could be exploited for Server-Side Template Injection (SSTI).
    """
    check_lab_mode()
    
    # VULNERABILITY: Using format() on user-controlled template
    # This can lead to information disclosure or code execution
    try:
        # Dangerous: user controls the format string
        result = template.format(
            name="User",
            secret="SENSITIVE_DATA_EXPOSED"  # This could leak sensitive info
        )
        logger.warning(f"Unsafe template render: {template}")
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# FIX: Safe template rendering
# Uncomment the function below and comment out the one above:
#
# @router.get("/render-safe")
# def safe_render(name: Annotated[str, Query(max_length=50)] = "User") -> dict[str, str]:
#     """Template rendering with safe, controlled template."""
#     check_lab_mode()
#     
#     # Safe: application controls the template, user only provides data
#     # Validate input
#     if not name.replace(" ", "").isalnum():
#         raise HTTPException(
#             status_code=400,
#             detail="Name must contain only alphanumeric characters and spaces"
#         )
#     
#     # Use a fixed template
#     template = "Hello {name}!"
#     result = template.format(name=name)
#     logger.info(f"Safe template render for: {name}")
#     return {"result": result}
