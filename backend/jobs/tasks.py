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


@shared_task
def reconcile_search_index():
    from .documents import JobDocument
    from .models import Job
    
    # Get all job IDs from the database
    db_job_ids = set(Job.objects.values_list('id', flat=True))
    
    # Get all job IDs from the search index
    search_job_ids = {int(hit.meta.id) for hit in JobDocument.search().scan()}
    
    # Jobs to be indexed (in DB but not in search index)
    to_index = db_job_ids - search_job_ids
    for job_id in to_index:
        update_search_index.delay(job_id, action='index')
        
    # Jobs to be deleted (in search index but not in DB)
    to_delete = search_job_ids - db_job_ids
    for job_id in to_delete:
        update_search_index.delay(job_id, action='delete')
