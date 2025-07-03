from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_search_index(self, job_id, action='index'):
    from .documents import JobDocument
    from .models import Job
    try:
        job = Job.objects.get(id=job_id)
        if action == 'delete':
            JobDocument().update(job, action='delete')
        else:
            JobDocument().update(job)
    except Job.DoesNotExist:
        # Handle case where job might be deleted before task runs
        pass
    except Exception as exc:
        # Log the exception and retry the task
        print(f"Error updating search index for job {job_id}: {exc}")
        raise self.retry(exc=exc)
