from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.utils import timezone

from apps.common.models import NBaseWithOwnerModel

from .action import Action
from .asset import Asset
from .project import Project


class TASK_RUNNING_STATUS(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    RUNNING = "RUNNING", _("Running")
    COMPLETED = "FINISHED", _("Finished")
    FAILED = "FAILED", _("Failed")


class Task(NBaseWithOwnerModel):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(
        Project,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    system_prompt = models.TextField()
    assets = models.ManyToManyField(
        Asset,
        related_name="assets",
        default=list,
    )
    actions = models.ManyToManyField(
        Action,
        related_name="actions",
        default=list,
    )
    status = models.CharField(
        max_length=20,
        choices=TASK_RUNNING_STATUS.choices,
        default=TASK_RUNNING_STATUS.PENDING,
    )
    description = models.TextField(null=True, blank=True)
    result_file_url = models.URLField(blank=True, null=True)
    
    # Store process results
    process_results = JSONField(default=list, blank=True)
    total_files = models.IntegerField(default=0)
    processed_files = models.IntegerField(default=0)
    failed_files = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
        
    def add_process_result(self, source_type, source_path, status, asset=None, error=None, result_data=None):
        """Add a process result to the task"""
        result = {
            'source_type': source_type,
            'source_path': source_path,
            'status': status,
            'timestamp': timezone.now().isoformat(),
            'result_data': result_data
        }
        
        if asset:
            result['asset_id'] = str(asset.id)
            result['asset_name'] = asset.name
            
        if error:
            result['error'] = str(error)
            
        if not self.process_results:
            self.process_results = []
            
        self.process_results.append(result)
        
        # Update counters
        self.processed_files += 1
        if status == 'error':
            self.failed_files += 1
            
        self.save()
        
    def set_total_files(self, count):
        """Set the total number of files to be processed"""
        self.total_files = count
        self.save()
        
    def get_progress(self):
        """Get task progress as percentage"""
        if self.total_files == 0:
            return 0
        return (self.processed_files / self.total_files) * 100
