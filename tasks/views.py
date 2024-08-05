
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from.models import Task
from.serializers import TaskSerializer
import logging

logger = logging.getLogger(__name__)

class TaskException(Exception):
    pass

# Define a custom error handler
def handle_error(exc):
    logger.error(exc)
    return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
 
    def create(self, request):
        try:
            task = TaskFactory.create_task(request.data)
            serializer = self.serializer_class(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except TaskException as e:
            return handle_error(e)
 
    def retrieve(self, request, pk=None):
        try:
            task = TaskSingleton.get_task(pk)
            serializer = self.serializer_class(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_error(e)
 
    class UpdateTaskMixin:
        def update(self, request, pk=None):
            try:
                task = self.get_object()
                task.update(request.data)
                serializer = self.serializer_class(task)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TaskException as e:
                return handle_error(e)
 
    def destroy(self, request, pk=None):
        try:
            task = self.get_object()
            task.delete()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_error(e)
 
class TaskFactory:
    @staticmethod
    def create_task(data):
        try:
            task = Task.objects.create(**data)
            return task
        except Exception as e:
            raise TaskException("Failed to create task")
 
class TaskSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskSingleton, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def get_task(pk):
        try:
            task = Task.objects.get(pk=pk)
            return task
        except Task.DoesNotExist:
            raise TaskException("Task not found")
 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'tasks.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'tasks': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}