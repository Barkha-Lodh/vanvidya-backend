#from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


# ==========================================
# USER PROFILE MODEL
# ==========================================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_no = models.CharField(max_length=15, unique=True)
    is_first_time_user = models.BooleanField(default=True)
    skipped_intro = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# ==========================================
# PLANT MODEL
# ==========================================
class Plant(models.Model):

    PLANT_TYPE_CHOICES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('both', 'Both'),
    ]

    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]

    TOXICITY_CHOICES = [
        ('non_toxic', 'Non-Toxic'),
        ('toxic_pets', 'Toxic to Pets'),
        ('toxic_humans', 'Toxic to Humans'),
        ('highly_toxic', 'Highly Toxic'),
    ]

    EDIBILITY_CHOICES = [
        ('edible', 'Edible'),
        ('non_edible', 'Non-Edible'),
        ('medicinal', 'Medicinal'),
        ('poisonous', 'Poisonous'),
    ]

    # Basic Information
    common_name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200)
    hindi_name = models.CharField(max_length=200, blank=True)
    plant_type = models.CharField(
        max_length=50,
        choices=PLANT_TYPE_CHOICES
    )
    size = models.CharField(
        max_length=50,
        choices=SIZE_CHOICES
    )

    # Safety Information
    toxicity = models.CharField(
        max_length=50,
        choices=TOXICITY_CHOICES
    )
    edibility = models.CharField(
        max_length=50,
        choices=EDIBILITY_CHOICES
    )

    # Care Information
    watering = models.TextField(
        blank=True,
        help_text="Watering instructions"
    )
    sunlight = models.TextField(
        blank=True,
        help_text="Sunlight requirements"
    )
    soil_type = models.TextField(
        blank=True,
        help_text="Soil type and pH"
    )
    temperature = models.CharField(
        max_length=100,
        blank=True,
        help_text="Temperature range"
    )
    care_tips = models.TextField(
        blank=True,
        help_text="General care tips"
    )

    # Additional Information
    fun_facts = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    is_common = models.BooleanField(
        default=False,
        help_text="Mark for offline caching"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"

    class Meta:
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
        ordering = ['common_name']


# ==========================================
# DISEASE MODEL
# ==========================================
class Disease(models.Model):

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='diseases'
    )
    name = models.CharField(max_length=200)
    symptoms = models.TextField(help_text="Disease symptoms")
    treatment = models.TextField(help_text="Treatment instructions")
    severity = models.CharField(
        max_length=50,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    prevention = models.TextField(
        blank=True,
        help_text="Prevention tips"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.plant.common_name}"

    class Meta:
        verbose_name = 'Disease'
        verbose_name_plural = 'Diseases'


# ==========================================
# LOGBOOK MODEL
# ==========================================
class Logbook(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logbook_entries'
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE
    )
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='logbook_images/',
        null=True,
        blank=True
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Where plant was found"
    )
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plant.common_name}"

    class Meta:
        verbose_name = 'Logbook Entry'
        verbose_name_plural = 'Logbook Entries'
        ordering = ['-date']


# ==========================================
# REMINDER MODEL
# ==========================================
class Reminder(models.Model):

    REMINDER_TYPE_CHOICES = [
        ('watering', 'Watering'),
        ('fertilizing', 'Fertilizing'),
        ('repotting', 'Repotting'),
        ('pruning', 'Pruning'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    reminder_type = models.CharField(
        max_length=50,
        choices=REMINDER_TYPE_CHOICES
    )
    frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES
    )
    next_reminder_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        plant_name = self.plant.common_name if self.plant else "General"
        return f"{self.user.username} - {self.reminder_type} - {plant_name}"

    class Meta:
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'
        ordering = ['next_reminder_date']


# ==========================================
# ADMIN MODEL (SECURE - Password Hashed!)
# ==========================================
class Admin(models.Model):

    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('plant_manager', 'Plant Manager'),
        ('data_entry', 'Data Entry'),
    ]

    # Linked to Django User (password auto-hashed)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='data_entry'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.role}"

    @property
    def email(self):
        return self.user.email

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
