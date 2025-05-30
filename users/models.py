# users/models.py
from django.db import models
from django.contrib.auth.models import User

# No custom user models needed for this phase, using Django's built-in User.
# If profile information beyond username/email/password is needed later,
# consider creating a UserProfile model with a OneToOneField to User.

# Example UserProfile (if needed later):
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     # Add profile fields like phone_number, address, etc.
#     phone_number = models.CharField(max_length=20, blank=True, null=True)
#     # ... other fields ...
# 
#     def __str__(self):
#         return f"{self.user.username}'s Profile"

