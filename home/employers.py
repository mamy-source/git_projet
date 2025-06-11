from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import EmployeeProfile, Service

@login_required
def employee_profile_view(request):
    try:
        profile = request.user.employee_profile
    except EmployeeProfile.DoesNotExist:
        return redirect('create_employee_profile')
    
    services = profile.services.all()
    all_services = Service.objects.all()
    context = {
        'profile': profile,
        'services': services,
        'all_services': all_services
    }
    return render(request, 'employers/profile.html', context)

@login_required
def create_employee_profile(request):
    if hasattr(request.user, 'employee_profile'):
        return redirect('employee_profile')
    
    all_services = Service.objects.all()
    
    if request.method == 'POST':
        # Process form data manually
        hourly_rate = request.POST.get('hourly_rate')
        work_schedule = request.POST.get('work_schedule')
        selected_services = request.POST.getlist('services')
        image = request.FILES.get('image')
        
        # Create profile
        profile = EmployeeProfile.objects.create(
            user=request.user,
            hourly_rate=hourly_rate,
            work_schedule=work_schedule,
            image=image
        )
        
        # Add services
        profile.services.set(selected_services)
        
        return redirect('employee_profile')
    
    return render(request, 'employers/create_profile.html', {
        'all_services': all_services
    })

@login_required
def update_employee_profile(request):
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    all_services = Service.objects.all()
    
    if request.method == 'POST':
        # Update profile data
        profile.hourly_rate = request.POST.get('hourly_rate')
        profile.work_schedule = request.POST.get('work_schedule')
        
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        
        profile.save()
        
        # Update services
        selected_services = request.POST.getlist('services')
        profile.services.set(selected_services)
        
        return redirect('employee_profile')
    
    return render(request, 'employers/update_profile.html', {
        'profile': profile,
        'all_services': all_services,
        'selected_services': profile.services.all()
    })

@login_required
def employee_list_view(request):
    employees = EmployeeProfile.objects.select_related('user').all()
    return render(request, 'employers/list.html', {'employees': employees})

@login_required
def employee_detail_view(request, user_id):
    employee = get_object_or_404(EmployeeProfile, user__id=user_id)
    services = employee.services.all()
    return render(request, 'employers/detail.html', {
        'employee': employee,
        'services': services
    })