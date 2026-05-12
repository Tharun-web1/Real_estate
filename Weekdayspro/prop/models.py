from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models import Q
import random
import re
import os
from datetime import timedelta


# ===== Enum Classes =====

class Role(models.TextChoices):
    OWNER = 'OWNER', 'Owner'
    MARKETER = 'MARKETER', 'Marketer'
    PROFESSIONAL = 'PROFESSIONAL', 'Professional'
    COMPANY = 'COMPANY', 'Company'
    FRANCHISE = 'FRANCHISE', 'Franchise'


class PlanType(models.TextChoices):
    MARKETER_EXPORT = 'MARKETER_EXPORT', 'Marketer Export'
    MARKETER_EXPORT_PRO = 'MARKETER_EXPORT_PRO', 'Marketer Export Pro'
    MARKETER_EXPORT_PREMIUM = 'MARKETER_EXPORT_PREMIUM', 'Marketer Export Premium'
    PROFESSIONAL_SINGLE = 'PROFESSIONAL_SINGLE', 'Professional Single'
    COMPANY_NORMAL = 'COMPANY_NORMAL', 'Company Normal'
    COMPANY_PRO = 'COMPANY_PRO', 'Company Pro'
    COMPANY_PREMIUM = 'COMPANY_PREMIUM','Company Premium'
    OWNER = 'OWNER', 'Owner'


class CompanySubscriptionType(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    PRO = 'PRO', 'Pro'
    PREMIUM = 'PREMIUM', 'Premium'
    


class MarketingSubscriptionType(models.TextChoices):
    EXPORT = 'EXPORT', 'Export'
    EXPORT_PRO = 'EXPORT_PRO', 'Export Pro'
    EXPORT_PREMIUM = 'EXPORT_PREMIUM', 'Export Premium'


class User(AbstractUser):
    # === your fields ===
    is_google_user = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    marketer_category = models.CharField(max_length=100, null=True, blank=True)
    company_category = models.CharField(max_length=100, null=True, blank=True)
    area_serves = models.CharField(max_length=255, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PROFESSIONAL)
    plan_type = models.CharField(max_length=30, choices=PlanType.choices, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    radius = models.IntegerField(default=5 )
    experience = models.IntegerField(null=True, blank=True)
    deals = models.CharField(max_length=255, null=True, blank=True)
    selected_duration = models.IntegerField(default=1)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    user_referral_code = models.CharField(max_length=50, null=True, blank=True, unique=True)
    referred_by_code = models.CharField(max_length=50, null=True, blank=True)
    profile_image_path = models.ImageField(upload_to='profile_images/', default='images/Default_profile_picture.jpeg', null=True, blank=True)
    company_logo_path = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    company_wallpaper_path = models.ImageField(upload_to='company_wallpapers/', null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.CharField(max_length=255, null=True, blank=True)
    click = models.BigIntegerField(default=0)
    leads = models.BigIntegerField(default=0)
    total_projects = models.IntegerField(null=True, blank=True)
    ongoing_projects = models.IntegerField(null=True, blank=True)
    completed_projects = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    company_subscription_start_date = models.DateField(null=True, blank=True)
    company_subscription_end_date = models.DateField(null=True, blank=True)
    marketer_subscription_start_date = models.DateField(null=True, blank=True)
    marketer_subscription_end_date = models.DateField(null=True, blank=True)
    professionals_subscription_start_date = models.DateField(null=True, blank=True)
    professionals_subscription_end_date = models.DateField(null=True, blank=True)
    company_subscription_type = models.CharField(max_length=50, choices=CompanySubscriptionType.choices, null=True, blank=True)
    marketing_subscription_type = models.CharField(max_length=50, choices=MarketingSubscriptionType.choices, null=True, blank=True)
    professionals_subscription_type = models.CharField(max_length=50, choices=MarketingSubscriptionType.choices, null=True, blank=True)
    owner_subscription_start_date = models.DateField(null=True, blank=True)
    owner_subscription_end_date = models.DateField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    # ✅ ADD THIS PROPERTY
    @property
    def is_user_online(self):
        if self.last_seen:
            return timezone.now() - self.last_seen <= timedelta(seconds=30)
        return False

    @property
    def is_subscription_active(self):
        today = timezone.now().date()
        if self.role == 'MARKETER' and self.marketer_subscription_end_date:
            return self.marketer_subscription_end_date >= today
        if self.role == 'COMPANY' and self.company_subscription_end_date:
            return self.company_subscription_end_date >= today
        if self.role == 'PROFESSIONAL' and self.professionals_subscription_end_date:
            return self.professionals_subscription_end_date >= today
        if self.role == 'OWNER' and self.owner_subscription_end_date:
            return self.owner_subscription_end_date >= today
        return False
    # ===== Important: Add UserManager =====
    objects = UserManager()

    def __str__(self):
        return self.username or "Unnamed User"

    @property
    def plan_price(self):
        prices = {
            'MARKETER_EXPORT': 7999,
            'MARKETER_EXPORT_PRO': 14999,
            'MARKETER_EXPORT_PREMIUM': 19999,
            'PROFESSIONAL_SINGLE': 4999,
            'COMPANY_NORMAL': 14999,
            'COMPANY_PRO': 19999,
            'COMPANY_PREMIUM' : 24999,
            'OWNER' : 17999,
        }
        return prices.get(self.plan_type, 0)

    # ===== Referral Code Generation =====
    def _generate_referral_code(self):
        id_part = str(self.id)
        role_part = (self.role[:2].upper() if self.role else "XX")
        name_clean = re.sub(r'[^A-Za-z0-9]', '', self.username or '')
        name_part = name_clean[:3].upper() if name_clean else "USR"
        random_part = str(random.randint(1000, 9999))
        return f"{role_part}{id_part}{name_part}{random_part}"

    def save(self, *args, **kwargs):
        # Save first to get PK
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Generate referral code if new
        if is_new and not self.user_referral_code:
            self.user_referral_code = self._generate_referral_code()
            # Update only this field to avoid recursion
            User.objects.filter(pk=self.pk).update(user_referral_code=self.user_referral_code)

class AddPropertyModel(models.Model):
    LOOKING_CHOICES = [
        ('Sell', 'Sale'),
        ('Rent', 'Rent'),
    ]
    
    FURNITURE_CHOICES = [
        ('Furnished', 'Furnished'),
        ('Semi-Furnished', 'Semi-Furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]

    furniture = models.CharField(
        max_length=20,
        choices=FURNITURE_CHOICES,
        blank=True,
        null=True
    )

    PROPERTY_CHOICES = [
        ('Plot', 'Plot'),
        ('House', 'House'),
        ('Flat', 'Flat'),
        ('Villa', 'Villa'),
        ('Farm', 'Farm Flat'),
        ('Lands', 'Lands'),
        ('Developmentlands', 'Development lands'),
        ('Disputelands', 'Dispute lands'),
        ('Commerciallands', 'Commercial lands'),
    ]
    furniture = models.CharField(
        max_length=20,
        choices=FURNITURE_CHOICES,
        null=True,
        blank=True
    )
  

    projectName = models.CharField(max_length=255, null=True, blank=True)
    extent = models.FloatField(null=True, blank=True)
    facing = models.CharField(max_length=100, null=True, blank=True)
    roadSize = models.CharField(max_length=100, null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    dimensions = models.CharField(max_length=255, null=True, blank=True)
    numberOfFloors = models.IntegerField(null=True, blank=True)
    numberOfBHK = models.IntegerField(null=True, blank=True)
    builtUpArea = models.FloatField(null=True, blank=True)
    openArea = models.FloatField(null=True, blank=True)
    rentalIncome = models.FloatField(null=True, blank=True)
    floorNo = models.IntegerField(null=True, blank=True)
    communityType = models.CharField(max_length=255, null=True, blank=True)
    carpetArea = models.FloatField(null=True, blank=True)
    landType = models.CharField(max_length=255, null=True, blank=True)
    soilType = models.CharField(max_length=255, null=True, blank=True)
    roadFacing = models.BooleanField(default=False)
    waterSource = models.CharField(max_length=255, null=True, blank=True)
    unitType = models.CharField(max_length=255, null=True, blank=True)
    zone = models.CharField(max_length=255, null=True, blank=True)
    developmentType = models.CharField(max_length=255, null=True, blank=True)
    expectedAdvance = models.FloatField(null=True, blank=True)
    ratio = models.CharField(max_length=255, null=True, blank=True)
    disputeDetails = models.TextField(null=True, blank=True)
    lookingToSell = models.BooleanField(default=False)
    problemDetails = models.TextField(null=True, blank=True)
    actualPrice = models.FloatField(null=True, blank=True)
    salePrice = models.FloatField(null=True, blank=True)
    price = models.FloatField(default=0)
    deposit=models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=20, default="Available")
    
    look = models.CharField(max_length=20, choices=LOOKING_CHOICES, null=True, blank=True)
    selectProperty = models.CharField(max_length=50, choices=PROPERTY_CHOICES, null=True, blank=True)

    reraApproved = models.BooleanField(default=False)
    approvalType = models.CharField(max_length=255, null=True, blank=True)
    amenities = models.JSONField(default=list, blank=True) 
    nearby_places = models.JSONField(default=list, blank=True, null=True)
    created_date = models.DateField(default=timezone.now)
    highlights = models.TextField(null=True, blank=True)

    propertyId = models.BigIntegerField(null=True, blank=True)
    is_notSold = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_legal_verified=models.BooleanField(default=False)
    

    verifiedBy = models.ForeignKey(User, related_name='verified_properties',
    on_delete=models.SET_NULL, null=True, blank=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    locationUrl = models.TextField(null=True, blank=True)
    is_verifiedproperty = models.BooleanField(default=False)

    user = models.ForeignKey(User, related_name='properties', on_delete=models.CASCADE)

    # Add direct file fields to the model
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    video = models.FileField(upload_to='property_videos/', null=True, blank=True)
    document = models.FileField(upload_to='property_documents/', null=True, blank=True)
    
    
    image1 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='property_images/', null=True, blank=True)
    image4 = models.ImageField(upload_to='property_images/', null=True, blank=True)

    @property
    def display_status(self):
        if self.is_verifiedproperty:
            return "Verified"
        if self.is_verified: # Franchise verified, awaiting owner confirmation
            return "Pending"
        return "Not Verified"

    def __str__(self):
        return f"{self.projectName} - {self.selectProperty}"



# franchise Form
class FranchiseApplication(models.Model):
    full_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    contact = models.CharField(max_length=20, null=False, blank=False) 
    location = models.CharField(max_length=100, null=False, blank=False)
    experience = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.full_name} - {self.location}"
    

    
class FranchiseProperty(models.Model):
    property = models.ForeignKey(AddPropertyModel, on_delete=models.CASCADE)

    # Store Property ID separately as requested
    property_id_number = models.IntegerField(null=True, blank=True)

    franchise = models.ForeignKey(User, on_delete=models.CASCADE)

    reviews = models.TextField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    verified_location = models.CharField(max_length=200, null=True, blank=True)
    video_file = models.FileField(upload_to="verification_videos/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for Property {self.property_id_number}"

class FranchisePropertyImage(models.Model):
    verification = models.ForeignKey(FranchiseProperty, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='verification_images/')

    def __str__(self):
        return f"Image for verification {self.verification.id}"

    
    
class FutureRequirement(models.Model):
    property_type = models.CharField(max_length=100)
    extent = models.CharField(max_length=100)
    bhk_type = models.CharField(max_length=50)
    facing = models.CharField(max_length=50)
    budget = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    approval_type = models.CharField(max_length=100)
    project_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)  # ðŸ‘ˆ important

    def _str_(self):
        return f"{self.property_type} - {self.city}"
    


# move request*************

class MoveRequest(models.Model):
    customer_name = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    alternate_number = models.CharField(max_length=20, blank=True, null=True)
    service_type = models.CharField(max_length=50)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    from_floor = models.CharField(max_length=50, blank=True, null=True)
    to_floor = models.CharField(max_length=50, blank=True, null=True)
    men_power = models.CharField(max_length=50, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} ({self.service_type})"
    

from django.db import models

class ContactForm(models.Model):
    customer_name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)
    renovation_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    additional_info = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.renovation_type}"

    # loan application

    
class LoanApplication(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()
    street_address = models.CharField(max_length=255)
    unit = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_purpose = models.CharField(max_length=100)
    application_date = models.DateField()
    employment_status = models.CharField(max_length=50)
    realtor = models.CharField(max_length=10)
    credit_score = models.CharField(max_length=50)
    agree = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.loan_purpose}"
    
    
    # add project**********
class AddProject(models.Model):
    
    POSITION_CHOICES = [
        ("READY", "Ready to Move"),
        ("UNDER", "Under Construction"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    plan_type = models.CharField(max_length=50, choices=PlanType.choices, null=True, blank=True)

    project_name = models.CharField(max_length=100)
    type_of_project = models.CharField(max_length=100)
    project_address = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_url = models.CharField(max_length=300, null=True, blank=True)
    number_of_units = models.CharField(max_length=100, null=True, blank=True)
    available_units = models.TextField(null=True, blank=True)
    available_facing = models.TextField(null=True, blank=True)
    available_sizes = models.TextField(null=True, blank=True)
    estbalis_year = models.IntegerField(null=True, blank=True)

    nearby_locations = models.JSONField(default=list, blank=True)
    
    rera_approved = models.BooleanField(null=True, blank=True)
    select_amenities = models.CharField(max_length=255, null=True, blank=True)
    highlights = models.TextField(null=True, blank=True)
    type_of_approval = models.CharField(max_length=200, null=True, blank=True)
    total_project_area = models.CharField(max_length=200, null=True, blank=True)
    contact_info = models.BigIntegerField(null=True, blank=True)
    pricing = models.BigIntegerField(null=True, blank=True)
    
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, null=True, blank=True)
    construction_time = models.CharField(max_length=100, null=True, blank=True)


    image = models.ImageField(upload_to='project_image/', null=True, blank=True)
    video = models.FileField(upload_to='project_video/', null=True, blank=True)
    document = models.FileField(upload_to='project_docs/', null=True, blank=True)

    def __str__(self):
        return self.project_name

 


class ProjectImage(models.Model):
    project = models.ForeignKey(AddProject, related_name="extra_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="project_extra/")

    def __str__(self):
        return f"Image for {self.project.project_name}"
    
class ProjectLegalDocument(models.Model):
    project = models.ForeignKey(AddProject, related_name="legal_documents", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="project_legal_docs/")

    def __str__(self):
        return f"{self.name} for {self.project.project_name}"

class SavedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(AddPropertyModel, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property")

    def _str_(self):
        return f"{self.user.username} saved {self.property.title}"
    
class SavedProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(AddProject, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} saved {self.project.project_name}"

    # companny contact
 
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, null=True, blank=True)
    requirement = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    cid = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_contact"

    def __str__(self):
        return self.name
    


class Reels(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reel = models.FileField(upload_to='reels/', null=True, blank=True)
    description = models.CharField(max_length=50)
    link = models.URLField(blank=True, null=True)
    likeCount = models.IntegerField(default=0)
    commentCount = models.IntegerField(default=0)
    shareCount = models.IntegerField(default=0)
    viewers = models.ManyToManyField(User, related_name='viewed_reels', blank=True)
    linked_property = models.ForeignKey(AddPropertyModel, on_delete=models.SET_NULL, null=True, blank=True)
   
    @property
    def view_count(self):
        return self.viewers.count()
    
class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    reel=models.ForeignKey(Reels,on_delete=models.CASCADE)
    comment=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    def _str_(self):
        return self.comment
    
 
    

class ProfileLeadsModel(models.Model):
    leadFrom=models.ForeignKey(User,on_delete=models.CASCADE,related_name="profileleads_sent")
    created_at=models.DateTimeField(auto_now_add=True)
    leadTo=models.ForeignKey(User,on_delete=models.CASCADE,related_name="profileleads_recived")
    
class PropertyLeadsModel(models.Model):
    leadFrom=models.ForeignKey(User,on_delete=models.CASCADE,related_name="propertyleads_sent")
    created_at=models.DateTimeField(auto_now_add=True)
    leadTo=models.ForeignKey(User,on_delete=models.CASCADE,related_name="propertyleads_recived")
    property=models.ForeignKey(AddPropertyModel,on_delete=models.CASCADE)


class ProjectLeadsModel(models.Model):
    leadFrom=models.ForeignKey(User,on_delete=models.CASCADE,related_name="projectleads_sent")
    created_at=models.DateTimeField(auto_now_add=True)
    leadTo=models.ForeignKey(User,on_delete=models.CASCADE,related_name="projectleads_recived")
    project=models.ForeignKey(AddProject,on_delete=models.CASCADE)




 

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, related_name='chats_initiated', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chats_received', on_delete=models.CASCADE)
    property = models.ForeignKey(AddPropertyModel, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2', 'property')

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}" + (
            f" ({self.property.title})" if self.property else ""
        )

class ChatMessage(models.Model):
    chat = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    # STATUS
    is_sent = models.BooleanField(default=True)
    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    # FEATURES
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=True, blank=True)



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=300, blank=True, null=True)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
from django.db import models
class SlideImage(models.Model):
    SLIDE_CHOICES = (
        ("desktop", "Desktop"),
        ("mobile", "Mobile"),
    )
    image = models.ImageField(upload_to='slideshow/')
    slide_type = models.CharField(max_length=10, choices=SLIDE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.slide_type} - {self.id}"

 
# =========================
# TABLE 2 - Post Feed
# =========================
class PostFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    MEDIA_TYPE = (
        ('image', 'Image'),
        ('video', 'Video'),
    )

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE)
    image = models.ImageField(upload_to='feed_images/', blank=True, null=True)
    video = models.FileField(upload_to='feed_videos/', blank=True, null=True)

    description = models.TextField()
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description[:30]


# =========================
# TABLE 3 - Image Posts
# =========================
class ImagePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    MEDIA_TYPE = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE, default='image')
    image = models.ImageField(upload_to='image_posts/', null=True, blank=True)
    video = models.FileField(upload_to='video_posts/', null=True, blank=True)
    heading = models.CharField(max_length=255, null=True, blank=True)
    news_content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.heading if self.heading else str(self.id)

class StorySeen(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_stories')
    post = models.ForeignKey(ImagePost, on_delete=models.CASCADE, related_name='seen_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

# =========================
# Signals for Cleanup
# =========================
@receiver(post_delete, sender=ImagePost)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding ImagePost object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
    if instance.video:
        if os.path.isfile(instance.video.path):
            os.remove(instance.video.path)

# =========================
# TABLE 4 - News Posts Feed
# =========================
class NewsPost(models.Model):
    MEDIA_TYPE = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text Only'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE, default='image')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    video = models.FileField(upload_to='news_videos/', blank=True, null=True)

    heading = models.CharField(max_length=255, blank=True, null=True)
    news_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.heading if self.heading else self.news_content[:20]

class NewsKeyword(models.Model):
    keyword = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword
class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.poll.question} - {self.option_text}"

    @property
    def vote_count(self):
        return self.votes.count()

class PollVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, related_name='votes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('match', 'Property Match'),
        ('system', 'System Update'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

# =========================
# Notification Signals
# =========================

@receiver(post_save, sender=AddPropertyModel)
def notify_property_match(sender, instance, created, **kwargs):
    if created:
        location = instance.address or ""
        # Find users whose registered location is mentioned in the property address
        users = User.objects.filter(location__isnull=False).exclude(location="")
        for user in users:
            if user.location.lower() in location.lower() and user != instance.user:
                Notification.objects.create(
                    user=user,
                    notification_type='match',
                    title="Property Match Found!",
                    message=f"A new {instance.selectProperty} in {user.location} has been posted.",
                    link=f"/property/{instance.id}/"
                )

@receiver(post_save, sender=AddProject)
def notify_project_match(sender, instance, created, **kwargs):
    if created:
        location = instance.project_address or ""
        users = User.objects.filter(location__isnull=False).exclude(location="")
        for user in users:
            if user.location.lower() in location.lower() and user != instance.user:
                Notification.objects.create(
                    user=user,
                    notification_type='match',
                    title="New Project in Your Area!",
                    message=f"A new project '{instance.project_name}' has been launched in {user.location}.",
                    link=f"/project/{instance.id}/"
                )

@receiver(post_save, sender=ChatMessage)
def notify_new_message(sender, instance, created, **kwargs):
    if created:
        recipient = instance.chat.user2 if instance.sender == instance.chat.user1 else instance.chat.user1
        # Check if a message notification already exists for this chat to avoid spam
        # Or just create one for each message. The user asked for "notification count"
        Notification.objects.create(
            user=recipient,
            notification_type='message',
            title=f"New Message from {instance.sender.username}",
            message=instance.message[:50],
            link=f"/{instance.chat.id}/"
        )

class PropertyInteraction(models.Model):
    INTERACTION_CHOICES = [('view', 'View'), ('enquiry', 'Enquiry')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    property = models.ForeignKey(AddPropertyModel, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(AddProject, on_delete=models.CASCADE, null=True, blank=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES, default='view')
    timestamp = models.DateTimeField(auto_now_add=True)

class ScheduledNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_notifications')
    notification_type = models.CharField(max_length=50)
    scheduled_for = models.DateTimeField()
    sent = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_logs')
    channel = models.CharField(max_length=20) # Email, SMS, WA
    notification_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    message = models.TextField(null=True, blank=True)
