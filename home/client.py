from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ClientProfile, Service, EmployeeProfile

@login_required
def client_profile_view(request):
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        client_profile = ClientProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Traitement des données du formulaire
        receive_promotions = 'receive_promotions' in request.POST
        favorite_employee_id = request.POST.get('favorite_employee')
        favorite_services_ids = request.POST.getlist('favorite_services')
        
        # Mise à jour du profil
        client_profile.receive_promotions = receive_promotions
        
        if favorite_employee_id:
            try:
                favorite_employee = EmployeeProfile.objects.get(id=favorite_employee_id)
                client_profile.favorite_employee = favorite_employee
            except EmployeeProfile.DoesNotExist:
                client_profile.favorite_employee = None
        else:
            client_profile.favorite_employee = None
        
        client_profile.favorite_services.set(favorite_services_ids)
        client_profile.save()
        return redirect('client_profile')
    
    # Récupération des données pour le formulaire
    all_services = Service.objects.all()
    all_employees = EmployeeProfile.objects.all()
    
    context = {
        'profile': client_profile,
        'all_services': all_services,
        'all_employees': all_employees,
    }
    return render(request, 'client_profile.html', context)