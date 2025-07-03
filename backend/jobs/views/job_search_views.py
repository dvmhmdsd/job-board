from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..documents import JobDocument
from ..serializers import JobSerializer

@api_view(['GET'])
def search_jobs(request):
    query = request.GET.get('q', '')
    if not query:
        return Response([], status=200)

    search = JobDocument.search().query("multi_match", query=query, fields=['title', 'description', 'skills', 'location'])
    queryset = search.to_queryset()
    serializer = JobSerializer(queryset, many=True)
    
    return Response(serializer.data)
