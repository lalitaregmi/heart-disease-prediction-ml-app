from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.pop('last_assessment_prediction', None)
        extra_fields.pop('last_assessment_probability', None)
        extra_fields.pop('last_assessment_timestamp', None)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if password is None:
             raise ValueError('Superuser must have a password.')

        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email Address')
    name = models.CharField(max_length=150, verbose_name='Full Name')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    last_assessment_prediction = models.IntegerField(null=True, blank=True, verbose_name='Last Prediction (0=Low, 1=High)')
    last_assessment_probability = models.FloatField(null=True, blank=True, verbose_name='Last Probability')
    last_assessment_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Last Assessment Time')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return self.is_superuser

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split(' ')[0] if self.name else self.email


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('Prevention', 'Prevention'),
        ('Risk Factors', 'Risk Factors'),
        ('Treatment', 'Treatment'),
        ('Lifestyle', 'Lifestyle'),
        ('Research', 'Research'),
        ('News', 'News'),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_staff': True},
        related_name='articles'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='News')
    image = models.ImageField(upload_to='articles/images/', blank=True, null=True)
    excerpt = models.CharField(max_length=255, blank=True, null=True, help_text="A short summary shown in list views.")
    content = models.TextField()
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False) 

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class PreventionTip(models.Model):
    CATEGORY_CHOICES = [
        ('Diet', 'Diet'),
        ('Exercise', 'Exercise'),
        ('Lifestyle', 'Lifestyle'),
        ('Medication', 'Medication'),
        ('Stress Management', 'Stress Management'),
        ('Monitoring', 'Monitoring'),
    ]

    title = models.CharField(max_length=100) 
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome class name (e.g., 'fa-heartbeat')")
    content = models.TextField(max_length=255) 
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_staff': True},
        related_name='prevention_tips'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['category', 'title']


# class lastAssessment(models.Model):
    
# class Sharedresult(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
#     bmi = models.FloatField()
#     smoking = models.CharField(max_length=10)
#     alcohol_drinking = models.CharField(max_length=10)
#     stroke = models.CharField(max_length=10)
#     physical_health = models.IntegerField()
#     mental_health = models.IntegerField()
#     diff_walking = models.CharField(max_length=10)
#     sex = models.CharField(max_length=10)
#     age_category = models.CharField(max_length=20)
#     race = models.CharField(max_length=20)
#     diabetic = models.CharField(max_length=20)
#     physical_activity = models.CharField(max_length=10)
#     gen_health = models.CharField(max_length=20)
#     sleep_time = models.IntegerField()
#     asthma = models.CharField(max_length=10)
#     kidney_disease = models.CharField(max_length=10)
#     skin_cancer = models.CharField(max_length=10)
    
#     predicted_label = models.IntegerField()
#     probability_of_high_risk = models.FloatField()
#     predicted_condition_text = models.CharField(max_length=30)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.email} - {self.predicted_condition_text} - {self.timestamp.strftime('%Y-%m-%d')}"

