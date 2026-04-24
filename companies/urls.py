from django.urls import path
from .views import (
    CompanyListAPIView, CompanyDetailAPIView,
    company_charts_api, screener_api, health_scores_api
)

urlpatterns = [
    path('', CompanyListAPIView.as_view(), name='company-list-api'),
    path('screener/', screener_api, name='screener-api'),
    path('health-scores/', health_scores_api, name='health-scores-api'),
    path('<str:company_id>/', CompanyDetailAPIView.as_view(), name='company-detail-api'),
    path('<str:company_id>/charts/', company_charts_api, name='company-charts-api'),
]
