"""
URL configuration for Offline app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SyncQueueViewSet, ConflictRecordViewSet, SyncBatchViewSet

router = DefaultRouter()
router.register(r'sync-queue', SyncQueueViewSet, basename='offline-sync-queue')
router.register(r'conflicts', ConflictRecordViewSet, basename='offline-conflict')
router.register(r'batches', SyncBatchViewSet, basename='offline-batch')

urlpatterns = [
    path('sync/', SyncQueueViewSet.as_view({'post': 'sync_all'}), name='offline-sync-all'),
] + router.urls
