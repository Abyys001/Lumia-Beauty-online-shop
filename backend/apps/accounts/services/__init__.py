"""Account domain services."""

__all__ = ['AuthAuditService', 'issue_tokens']


def __getattr__(name: str):
    if name == 'AuthAuditService':
        from .audit import AuthAuditService
        return AuthAuditService
    if name == 'issue_tokens':
        from .tokens import issue_tokens
        return issue_tokens
    raise AttributeError(name)
