from django.db import models
from users.models import AppUser

# Create your models here.

class Connection(models.Model):
    """Model to track connections between users in Sub4Sub Connect"""
    
    # The user who initiated the connection
    from_user = models.ForeignKey(
        AppUser, 
        on_delete=models.CASCADE, 
        related_name='connections_sent'
    )
    
    # The user who received the connection
    to_user = models.ForeignKey(
        AppUser, 
        on_delete=models.CASCADE, 
        related_name='connections_received'
    )
    
    # Connection status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    ]
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional message when sending connection request
    message = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
        verbose_name = "Connection"
        verbose_name_plural = "Connections"
    
    def __str__(self):
        return f"{self.from_user.first_name} → {self.to_user.first_name} ({self.status})"
    
    @property
    def is_mutual(self):
        """Check if this is a mutual connection (both users have accepted)"""
        return (
            self.status == 'accepted' and 
            Connection.objects.filter(
                from_user=self.to_user,
                to_user=self.from_user,
                status='accepted'
            ).exists()
        )
