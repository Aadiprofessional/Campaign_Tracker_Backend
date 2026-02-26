import uuid
from django.db import models

class Campaign(models.Model):
    PLATFORM_CHOICES = [
        ('Google Ads', 'Google Ads'),
        ('Facebook', 'Facebook'),
        ('Instagram', 'Instagram'),
        ('LinkedIn', 'LinkedIn'),
        ('Email', 'Email'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Paused', 'Paused'),
        ('Completed', 'Completed'),
        ('Draft', 'Draft'),
    ]

    GOAL_CHOICES = [
        ('Brand Awareness', 'Brand Awareness'),
        ('Lead Generation', 'Lead Generation'),
        ('Sales', 'Sales'),
        ('Traffic', 'Traffic'),
        ('Engagement', 'Engagement'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Draft')
    budget = models.FloatField()
    amount_spent = models.FloatField(default=0.0)
    start_date = models.DateField()
    end_date = models.DateField()
    target_audience = models.TextField(blank=True, null=True)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES)
    roi = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
