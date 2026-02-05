from django.shortcuts import redirect

def landing(request):
    # If user is authenticated, redirect to portal, otherwise to login
    if request.user.is_authenticated:
        return redirect("/portal/")
    return redirect("/account/login/")
