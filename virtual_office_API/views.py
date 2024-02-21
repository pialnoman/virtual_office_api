from django.shortcuts import redirect


def redirect_view(request):
    response = redirect('/vo-admin/admin/')
    # response = redirect('/admin/')
    return response