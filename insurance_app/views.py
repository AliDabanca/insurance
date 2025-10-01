import unicodedata
from django.forms import CharField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Func
from django.db.models.functions import Lower
from django.db import models, transaction
from .models import Customer, PolicyType, InsuranceCompany, Policy, Referans
from .forms import CustomerForm, PolicyForm, ReferansForm
from django.http import JsonResponse
from datetime import date, timedelta

# PostgreSQL UNACCENT fonksiyonu
class Unaccent(Func):
    function = 'UNACCENT'
    output_field = models.CharField()


# Türkçe karakterleri normalleştirme
def normalize_turkish(text):
    replacements = (
        ("ç", "c"),
        ("ğ", "g"),
        ("ı", "i"),
        ("ö", "o"),
        ("ş", "s"),
        ("ü", "u"),
    )
    text = text.lower()
    for a, b in replacements:
        text = text.replace(a, b)
    return text


# ----------------- CUSTOMER LIST -----------------
def customer_list(request):
    search_name = request.GET.get('search_name', '').strip()
    filter_policy = request.GET.get('filter_policy', 'Tümü')
    filter_company = request.GET.get('filter_company', 'Tümü')

    show_customers = (len(search_name) >= 3) or filter_policy != 'Tümü' or filter_company != 'Tümü'

    if not show_customers:
        customers = Customer.objects.none()
    else:
        customers = Customer.objects.prefetch_related(
            'policies__policy_type',
            'policies__insurance_company'
        )
        if len(search_name) >= 3:
            search_normalized = normalize_turkish(search_name)
            customers = customers.annotate(
                name_unaccent=Lower(Unaccent('name')),
                profession_unaccent=Lower(Unaccent('profession')),
                city_unaccent=Lower(Unaccent('city'))
            ).filter(
                Q(name_unaccent__icontains=search_normalized) |
                Q(phone_number__icontains=search_normalized) |
                Q(profession_unaccent__icontains=search_normalized) |
                Q(city_unaccent__icontains=search_normalized) |
                Q(tc_id__icontains=search_normalized) |
                Q(policies__plate_number__icontains=search_normalized)
            )

        if filter_policy != 'Tümü':
            customers = customers.filter(policies__policy_type__name=filter_policy)
        if filter_company != 'Tümü':
            customers = customers.filter(policies__insurance_company__name=filter_company)

        customers = customers.distinct().order_by('name')

    policy_types = PolicyType.objects.all().order_by('name')
    insurance_companies = InsuranceCompany.objects.all().order_by('name')

    for pt in policy_types:
        pt.is_selected = (pt.name == filter_policy)
    for company in insurance_companies:
        company.is_selected = (company.name == filter_company)

    # --- YAKLAŞAN POLİÇELER ---
    today = date.today()
    next_30 = today + timedelta(days=30)
    upcoming_policies_qs = Policy.objects.filter(
        end_date__range=[today, next_30]
    ).select_related("customer", "policy_type").order_by("end_date")

    upcoming_policies = []
    for policy in upcoming_policies_qs:
        days_left = (policy.end_date - today).days
        upcoming_policies.append({
            "customer": policy.customer,
            "policy_type": policy.policy_type,
            "end_date": policy.end_date,
            "days_left": days_left,
        })

    context = {
        'customers': customers,
        'search_name': search_name,
        'policy_types': policy_types,
        'insurance_companies': insurance_companies,
        'filter_policy_is_all': (filter_policy == 'Tümü'),
        'filter_company_is_all': (filter_company == 'Tümü'),
        'show_customers': show_customers,
        'upcoming_policies': upcoming_policies,  # artık tüm poliçeler
        'today': today,
    }
    return render(request, 'customer_list.html', context)


# ----------------- CREATE CUSTOMER -----------------
def create_customer(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        policy_form = PolicyForm(request.POST)

        if customer_form.is_valid() and policy_form.is_valid():
            try:
                with transaction.atomic():
                    customer = customer_form.save()
                    policy = policy_form.save(commit=False)
                    policy.customer = customer
                    policy.save()
                messages.success(request, 'Yeni müşteri ve poliçe başarıyla eklendi!')
                return redirect('customer_list')
            except Exception as e:
                messages.error(request, f'Kayıt sırasında bir hata oluştu: {str(e)}')
        else:
            error_messages = []
            for field, errors in customer_form.errors.items():
                for error in errors:
                    error_messages.append(f"Müşteri {field}: {error}")
            for field, errors in policy_form.errors.items():
                for error in errors:
                    error_messages.append(f"Poliçe {field}: {error}")
            if error_messages:
                messages.error(request, "Lütfen aşağıdaki hataları düzeltin: " + "; ".join(error_messages))
    else:
        customer_form = CustomerForm()
        policy_form = PolicyForm()

    return render(request, 'create_customer.html', {
        'customer_form': customer_form,
        'policy_form': policy_form,
    })


# ----------------- CUSTOMER DETAIL -----------------
def customer_detail(request, pk):
    customer = get_object_or_404(
        Customer.objects.prefetch_related('policies__policy_type', 'policies__insurance_company'),
        pk=pk
    )
    return render(request, 'customer_detail.html', {'customer': customer})


# ----------------- REFERANSLAR -----------------
def referanslar_view(request):
    query = request.GET.get('q', '').strip()
    data = []

    if query:
        query_norm = normalize_turkish(query)
        referanslar = Referans.objects.annotate(
            ad_norm=Lower(Unaccent('ad_soyadi'))
        ).filter(ad_norm__icontains=query_norm).order_by('ad_soyadi')

        for r in referanslar:
            try:
                adet = int(r.police_adet)
            except (ValueError, TypeError):
                adet = 0

            if adet <= 2:
                color = "bg-primary text-white"
            elif adet <= 4:
                color = "bg-success text-white"
            else:
                color = "bg-warning"

            data.append({
                'ad_soyadi': r.ad_soyadi,
                'police_adet': r.police_adet,
                'referans': r.referans,
                'aciklama': r.aciklama,
                'color': color
            })

    if request.method == 'POST':
        form = ReferansForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Yeni referans başarıyla eklendi!')
            return redirect('referanslar')
    else:
        form = ReferansForm()

    return render(request, 'referanslar.html', {
        'data': data,
        'query': query,
        'form': form
    })


def referanslar_search(request):
    query = request.GET.get('q', '').strip()
    data = []

    if query:
        query_norm = normalize_turkish(query)
        referanslar = Referans.objects.annotate(
            ad_norm=Lower(Unaccent('ad_soyadi'))
        ).filter(ad_norm__icontains=query_norm).order_by('ad_soyadi')

        for r in referanslar:
            try:
                adet = int(r.police_adet)
            except (ValueError, TypeError):
                adet = 0

            if adet <= 2:
                color = "bg-primary text-white"
            elif adet <= 4:
                color = "bg-success text-white"
            else:
                color = "bg-warning"

            data.append({
                'ad_soyadi': r.ad_soyadi,
                'police_adet': r.police_adet,
                'referans': r.referans,
                'aciklama': r.aciklama,
                'color': color
            })

    return JsonResponse({'data': data})
