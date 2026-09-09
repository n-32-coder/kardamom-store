from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from .models import Customer


class CustomerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = ('username', 'email', 'phone')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to KARDAMOM!')
            return redirect('home')
    else:
        form = CustomerCreationForm()
    return render(request, 'customers/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'customers/profile.html', {'customer': request.user})
