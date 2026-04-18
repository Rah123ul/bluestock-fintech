from django.contrib import admin
from django.urls import path, include
from companies.views import home, company_list, company_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/companies/', include('companies.urls')),
    path('', home, name='home'),
    path('companies/', company_list, name='company-list'),
    path('companies/<str:company_id>/', company_detail, name='company-detail'),
]
