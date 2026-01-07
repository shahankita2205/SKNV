from django.db import models

class Hooks_Queue(models.Model):
    name = models.TextField(blank=False,null=False)
    payload = models.TextField(blank=True,null=True)
    requester_ip = models.TextField(blank=False,null=False)
    processed = models.BooleanField(blank=False,default=False)
    payload_hash = models.CharField(max_length=32, null=True, blank=True)
    date_created  = models.DateTimeField(auto_now_add=True)
    date_processed = models.DateTimeField(blank=True,null=True)

    class Meta:
        db_table = "hooks_queue"
        indexes = [
            models.Index(fields=['name', 'date_created', 'id'], 
                        name='idx_hq_duplicate_check'),
            models.Index(fields=['date_created'], 
                        name='idx_hq_date_created'),
            models.Index(fields=['payload_hash'], 
                        name='idx_hq_payload_hash'),
        ]

    def __str__(self):
        return self.name
    