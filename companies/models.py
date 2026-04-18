from django.db import models

class Company(models.Model):
    company_id   = models.CharField(max_length=50, primary_key=True)
    company_name = models.CharField(max_length=200, null=True)
    company_logo = models.TextField(null=True)
    about_company= models.TextField(null=True)
    website      = models.TextField(null=True)
    nse_profile  = models.TextField(null=True)
    bse_profile  = models.TextField(null=True)
    face_value   = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    book_value   = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    roce_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    roe_percentage  = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'dim_company'
        managed  = False

    def __str__(self):
        return self.company_name or self.company_id


class HealthScore(models.Model):
    company_id          = models.CharField(max_length=50)
    company_name        = models.CharField(max_length=200, null=True)
    overall_score       = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    score_profitability = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    score_growth        = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    score_leverage      = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    score_cashflow      = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    score_dividend      = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    score_coverage      = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    health_label        = models.CharField(max_length=20, null=True)
    computed_at         = models.DateTimeField(null=True)

    class Meta:
        db_table = 'fact_ml_scores'
        managed  = False

    def __str__(self):
        return f"{self.company_name} - {self.health_label}"


class ProfitLoss(models.Model):
    company_id           = models.CharField(max_length=50)
    year_label           = models.CharField(max_length=20, null=True)
    fiscal_year          = models.IntegerField(null=True)
    sales                = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    expenses             = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    operating_profit     = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    opm_percentage       = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_profit           = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    eps                  = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_profit_margin_pct= models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'fact_profit_loss'
        managed  = False


class BalanceSheet(models.Model):
    company_id    = models.CharField(max_length=50)
    year_label    = models.CharField(max_length=20, null=True)
    fiscal_year   = models.IntegerField(null=True)
    equity_capital= models.DecimalField(max_digits=20, decimal_places=2, null=True)
    reserves      = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    borrowings    = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    total_assets  = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    debt_to_equity= models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'fact_balance_sheet'
        managed  = False


class CashFlow(models.Model):
    company_id         = models.CharField(max_length=50)
    year_label         = models.CharField(max_length=20, null=True)
    fiscal_year        = models.IntegerField(null=True)
    operating_activity = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    investing_activity = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    financing_activity = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    free_cash_flow     = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    class Meta:
        db_table = 'fact_cash_flow'
        managed  = False
