import json
from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import Company, HealthScore, ProfitLoss, BalanceSheet, CashFlow
from .serializers import CompanyListSerializer, CompanyDetailSerializer

class CompanyListAPIView(generics.ListAPIView):
    queryset = Company.objects.all().order_by('company_name')
    serializer_class = CompanyListSerializer

class CompanyDetailAPIView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyDetailSerializer
    lookup_field = 'company_id'

def home(request):
    scores = HealthScore.objects.all()
    top = scores.order_by('-overall_score')[:6]
    return render(request, 'home.html', {
        'total_companies': Company.objects.count(),
        'excellent_count': scores.filter(health_label='EXCELLENT').count(),
        'good_count': scores.filter(health_label='GOOD').count(),
        'poor_count': scores.filter(health_label='POOR').count(),
        'top_companies': top,
    })

def company_list(request):
    search = request.GET.get('search', '')
    label = request.GET.get('label', '')
    companies = Company.objects.all().order_by('company_name')
    if search:
        companies = companies.filter(company_name__icontains=search) | \
                    companies.filter(company_id__icontains=search)
    scores = {s.company_id: s for s in HealthScore.objects.all()}
    result = []
    for c in companies:
        h = scores.get(c.company_id)
        if label and (not h or h.health_label != label):
            continue
        result.append({
            'company_id': c.company_id,
            'company_name': c.company_name,
            'roce_percentage': c.roce_percentage,
            'roe_percentage': c.roe_percentage,
            'health_label': h.health_label if h else 'N/A',
            'overall_score': h.overall_score if h else 0,
        })
    return render(request, 'company_list.html', {
        'companies': result,
        'search_query': search,
    })

def company_detail(request, company_id):
    company = get_object_or_404(Company, company_id=company_id)
    health = HealthScore.objects.filter(company_id=company_id).first()
    pl_qs = ProfitLoss.objects.filter(company_id=company_id).order_by('fiscal_year')
    cf_qs = CashFlow.objects.filter(company_id=company_id).order_by('fiscal_year')
    pl_data = [{'year': r.year_label, 'sales': float(r.sales or 0),
                'net_profit': float(r.net_profit or 0)} for r in pl_qs]
    cf_data = [{'year': r.year_label,
                'operating': float(r.operating_activity or 0),
                'investing': float(r.investing_activity or 0),
                'free_cash_flow': float(r.free_cash_flow or 0)} for r in cf_qs]
    return render(request, 'company_detail.html', {
        'company': company,
        'health': health,
        'profit_loss_json': json.dumps(pl_data),
        'cash_flow_json': json.dumps(cf_data),
    })
