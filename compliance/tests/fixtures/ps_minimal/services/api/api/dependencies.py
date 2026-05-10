from grid_adapters.accessibility import (
    AccessibilityAdapter,
    InMemoryAccessibilityAdapter,
)
from grid_adapters.audit import AuditAdapter, PostgresAuditAdapter
from grid_adapters.document_storage import LocalFilesystemAdapter, StorageAdapter
from grid_adapters.identity import IdentityAdapter, NoAuthAdapter
from grid_adapters.notifications import LogOnlyAdapter, NotificationsAdapter
from grid_adapters.payments import LogOnlyPaymentsAdapter, PaymentsAdapter


def get_identity_adapter() -> IdentityAdapter:
    return NoAuthAdapter()


def get_audit_adapter() -> AuditAdapter:
    return PostgresAuditAdapter()


def get_document_storage_adapter() -> StorageAdapter:
    return LocalFilesystemAdapter()


def get_notifications_adapter() -> NotificationsAdapter:
    return LogOnlyAdapter()


def get_payments_adapter() -> PaymentsAdapter:
    return LogOnlyPaymentsAdapter()


def get_accessibility_adapter() -> AccessibilityAdapter:
    return InMemoryAccessibilityAdapter()
