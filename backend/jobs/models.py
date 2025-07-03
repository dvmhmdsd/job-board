from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .documents import JobDocument

class User(models.Model):
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.CharField(max_length=50, choices=[('applicant', 'Applicant'), ('company', 'Company')])
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    linkedin = models.URLField(max_length=255, blank=True)
    github = models.URLField(max_length=255, blank=True)
    resume = models.URLField(max_length=255, blank=True)
    skills = models.TextField()

    def __str__(self):
        return self.user.name


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    logo = models.URLField(max_length=255, blank=True)
    brief = models.TextField()
    website = models.URLField(max_length=255)

    def __str__(self):
        return self.name


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    application_url = models.URLField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    skills = models.TextField()
    status = models.CharField(max_length=50, choices=[('open', 'Open'), ('closed', 'Closed')])
    job_type = models.CharField(max_length=50, choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('internship', 'Internship')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

@receiver(post_save, sender=Job)
def update_job_document(sender, instance, **kwargs):
    JobDocument().update(instance)

@receiver(post_delete, sender=Job)
def delete_job_document(sender, instance, **kwargs):
    JobDocument().update(instance, action='delete')

class Experience(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="experiences")
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    skills = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class JobApplication(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    company_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('applied', 'Applied'), ('interview', 'Interview'), ('offered', 'Offered'), ('rejected', 'Rejected')])
    job_title = models.CharField(max_length=255)
    job_url = models.URLField(max_length=255)    
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.user.username} -> {self.job.title}"
