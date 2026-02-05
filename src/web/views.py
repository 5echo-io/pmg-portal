from django.shortcuts import redirect

def landing(request):
    # Always start with login as requested.
    return redirect("/account/login/")
