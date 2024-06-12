from django.urls import include, path

urlpatterns = [
    path('v1/curator/', include('api.v1.curator.urls')),
    path('v1/client/', include('api.v1.client.urls')),
    path('v1/lms-crm/', include('api.v1.lms_crm.urls')),
]
