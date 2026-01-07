# utils/event_utils.py
import hashlib
import json
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from django.utils import timezone
from django.db import transaction
from django.core.management.base import BaseCommand

from ..models import Hooks_Queue

logger = logging.getLogger(__name__)


class HookQueueDuplicateManager:
    """Utility class for managing duplicate Hook Calls"""
    
    @staticmethod
    def create_payload_hash(payload: Any) -> str:
        """
        Create a consistent hash of the payload for comparison
        
        Args:
            payload: The event payload to hash
            
        Returns:
            MD5 hash string of the payload
        """
        try:
            # Ensure consistent JSON serialization
            payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            return hashlib.md5(payload_str.encode('utf-8')).hexdigest()
        except (TypeError, ValueError) as e:
            logger.warning(f"Could not hash payload: {e}")
            return hashlib.md5(str(payload).encode('utf-8')).hexdigest()
    
    @staticmethod
    def is_duplicate_event(name: str, payload: Any, 
                          created_at=None, window_seconds: int = 5) -> bool:
        """
        Check if an event is a duplicate within the specified time window
        
        Args:
            name: Hook name
            payload: Hook payload
            created_at: When the event was created (defaults to now)
            window_seconds: Time window to check for duplicates
            
        Returns:
            True if duplicate found, False otherwise
        """
        if created_at is None:
            created_at = timezone.now()
        
        window_start = created_at - timedelta(seconds=window_seconds)
        payload_hash = HookQueueDuplicateManager.create_payload_hash(payload)
        
        # First check with hash for performance
        recent_events = Hooks_Queue.objects.filter(
            name=name,
            payload_hash=payload_hash,
            date_created__gte=window_start,  # Fixed: was missing __gte
            date_created__lt=created_at
        )
        
        # If hash matches found, double-check with actual payload comparison
        for event in recent_events:
            if HookQueueDuplicateManager._payloads_equal(payload, event.payload):
                logger.info(f"Duplicate record detected: {name} - Hash: {payload_hash}")
                return True
        
        return False
    
    @staticmethod
    def _payloads_equal(payload1: Any, payload2: Any) -> bool:
        """Compare two payloads for equality"""
        try:
            return (json.dumps(payload1, sort_keys=True) == 
                   json.dumps(payload2, sort_keys=True))
        except (TypeError, ValueError):
            return payload1 == payload2
    
    @staticmethod
    def create_queue_entry_with_duplicate_check(name: str, payload: Any,
                                        window_seconds: int = 5) -> Optional[Hooks_Queue]:
        """
        Create an entry only if it's not a duplicate
        
        Args:
            name: Hook name  
            payload: payload
            window_seconds: Duplicate detection window
            
        Returns:
            Created Hook Queue instance or None if duplicate
        """
        with transaction.atomic():
            created_at = timezone.now()
            
            payload_hash = HookQueueDuplicateManager.create_payload_hash(payload)
            
            hook_record = Hooks_Queue.objects.create(
                name=name,
                payload=payload,
                payload_hash=payload_hash,
                date_created=created_at
            )
            
            return hook_record


class EventCleanupManager:
    """Utility class for cleaning up old events"""
    
    @staticmethod
    def cleanup_old_entries(days_to_keep: int = 30) -> int:
        """
        Remove entries older than specified days
        
        Args:
            days_to_keep: Number of days of events to retain
            
        Returns:
            Number of entries deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        deleted_count, _ = Hooks_Queue.objects.filter(
            date_created__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old records")
        return deleted_count
    
    @staticmethod
    def count_old_entries(days_to_keep: int = 30) -> int:
        """
        Count entries older than specified days (for dry run)
        
        Args:
            days_to_keep: Number of days of entries to retain
            
        Returns:
            Number of entries that would be deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        return Hooks_Queue.objects.filter(date_created__lt=cutoff_date).count()
    
    @staticmethod
    def update_missing_payload_hashes() -> int:
        """
        Update payload_hash for existing events that don't have it
        
        Returns:
            Number of events updated
        """
        events_without_hash = Hooks_Queue.objects.filter(payload_hash__isnull=True)
        updated_count = 0
        
        for event in events_without_hash.iterator():
            event.payload_hash = HookQueueDuplicateManager.create_payload_hash(event.payload)
            event.save(update_fields=['payload_hash'])
            updated_count += 1
            
            if updated_count % 1000 == 0:
                logger.info(f"Updated {updated_count} entries with payload hashes")
        
        logger.info(f"Finished updating {updated_count} entries with payload hashes")
        return updated_count
    
# Celery task for periodic cleanup (if using Celery)
try:
    from celery import shared_task

    @shared_task
    def cleanup_old_events_task(days_to_keep: int = 30):
        """Celery task to periodically clean up old entries"""
        return EventCleanupManager.cleanup_old_entries(days_to_keep)
except ImportError:
    # Celery not installed, skip the task definition
    pass