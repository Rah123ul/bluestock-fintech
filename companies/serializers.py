from rest_framework import serializers
from .models import Company, HealthScore, ProfitLoss, BalanceSheet, CashFlow

class HealthScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScore
        fields = ['overall_score', 'health_label', 'score_profitability',
                  'score_growth', 'score_leverage', 'score_cashflow',
                  'score_dividend', 'score_coverage']

class CompanyListSerializer(serializers.ModelSerializer):
    health_score  = serializers.SerializerMethodField()
    health_label  = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = ['company_id', 'company_name', 'company_logo',
                  'website', 'roce_percentage', 'roe_percentage',
                  'health_score', 'health_label']

    def get_health_score(self, obj):
        h = HealthScore.objects.filter(company_id=obj.company_id).first()
        return float(h.overall_score) if h and h.overall_score else None

    def get_health_label(self, obj):
        h = HealthScore.objects.filter(company_id=obj.company_id).first()
        return h.health_label if h else None

class CompanyDetailSerializer(serializers.ModelSerializer):
    health         = serializers.SerializerMethodField()
    profit_loss    = serializers.SerializerMethodField()
    balance_sheet  = serializers.SerializerMethodField()
    cash_flow      = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = ['company_id', 'company_name', 'company_logo',
                  'about_company', 'website', 'nse_profile', 'bse_profile',
                  'face_value', 'book_value', 'roce_percentage',
                  'roe_percentage', 'health', 'profit_loss',
                  'balance_sheet', 'cash_flow']

    def get_health(self, obj):
        h = HealthScore.objects.filter(company_id=obj.company_id).first()
        return HealthScoreSerializer(h).data if h else None

    def get_profit_loss(self, obj):
        qs = ProfitLoss.objects.filter(company_id=obj.company_id).order_by('fiscal_year')
        return [{'year': r.year_label, 'sales': float(r.sales or 0),
                 'net_profit': float(r.net_profit or 0),
                 'opm_pct': float(r.opm_percentage or 0)} for r in qs]

    def get_balance_sheet(self, obj):
        qs = BalanceSheet.objects.filter(company_id=obj.company_id).order_by('fiscal_year')
        return [{'year': r.year_label,
                 'borrowings': float(r.borrowings or 0),
                 'reserves': float(r.reserves or 0),
                 'debt_to_equity': float(r.debt_to_equity or 0)} for r in qs]

    def get_cash_flow(self, obj):
        qs = CashFlow.objects.filter(company_id=obj.company_id).order_by('fiscal_year')
        return [{'year': r.year_label,
                 'operating': float(r.operating_activity or 0),
                 'investing': float(r.investing_activity or 0),
                 'free_cash_flow': float(r.free_cash_flow or 0)} for r in qs]
