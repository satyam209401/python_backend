from App.src.utils.audit_logger import AuditLogger


async def server_exception_handler(request, exc: Exception):
    return AuditLogger.handle_exception(exc, request=request)
