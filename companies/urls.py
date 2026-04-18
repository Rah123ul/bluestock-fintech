from django.urls import path
from .views import CompanyListAPIView, CompanyDetailAPIView

urlpatterns = [
    path('', CompanyListAPIView.as_view(), name='company-list-api'),
    path('<str:company_id>/', CompanyDetailAPIView.as_view(), name='company-detail-api'),
]
