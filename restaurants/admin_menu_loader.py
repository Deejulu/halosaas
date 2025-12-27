
from django.contrib import messages
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

class MenuDataUploadForm(forms.Form):
    menu_file = forms.FileField(label="Upload menu_data.json")

@staff_member_required
def menu_data_loader_view(request):
    if request.method == 'POST':
        form = MenuDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            menu_file = form.cleaned_data['menu_file']
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                for chunk in menu_file.chunks():
                    tmp.write(chunk)
                tmp.flush()
                call_command('loaddata', tmp.name)
            messages.success(request, 'Menu data loaded successfully!')
            return HttpResponseRedirect(reverse('admin:menu-data-loader'))
    else:
        form = MenuDataUploadForm()
    return render(request, "admin/menu_data_loader.html", {'form': form})

def get_menu_data_loader_url():
    return path('menu-data-loader/', menu_data_loader_view, name='menu-data-loader')
