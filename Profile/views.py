from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import jwt
from django.conf import settings
# Create your views here.

@login_required
def profile(request):
    return render(request, 'profile/profile.html', {'user': request.user})
