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

class MonthlyPerformance(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='monthly_performances')
    month = models.DateField()
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    spend = models.FloatField(default=0.0)
    revenue = models.FloatField(default=0.0)
    roi = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('campaign', 'month')
        indexes = [
            models.Index(fields=['campaign']),
        ]

    def save(self, *args, **kwargs):
        if self.spend > 0:
            self.roi = ((self.revenue - self.spend) / self.spend) * 100
        else:
            self.roi = 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campaign.name} - {self.month}"
