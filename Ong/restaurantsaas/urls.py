from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home  # Make sure this import works
from restaurants.views import accept_staff_invite

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('restaurants/', include('restaurants.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('reviews/', include('reviews.urls')),
    
    # Staff invite acceptance (global URL)
    path('staff/accept-invite/<str:invite_code>/', accept_staff_invite, name='accept_staff_invite'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)