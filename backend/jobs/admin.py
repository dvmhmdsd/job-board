from django.contrib import admin

# Register your models here.
from .models import User, Applicant, Company, Job, Experience, JobApplication

admin.site.register(User)
admin.site.register(Applicant)
admin.site.register(Company)
admin.site.register(Job)
admin.site.register(Experience)
admin.site.register(JobApplication)

