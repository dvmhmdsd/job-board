from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Job

@registry.register_document
class JobDocument(Document):
    class Index:
        name = 'jobs'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Job
        fields = [
            'title',
            'description',
            'location',
            'skills',
        ]
