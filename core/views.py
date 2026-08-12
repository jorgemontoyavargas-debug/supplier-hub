from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from config.version import VERSION


def health(request):
    try:
        connection.ensure_connection()
        database_status = "ok"
        status_code = 200
    except Exception:
        database_status = "unavailable"
        status_code = 503
    return JsonResponse(
        {
            "status": "ok" if status_code == 200 else "degraded",
            "service": "supplier-hub",
            "version": VERSION,
            "database": database_status,
        },
        status=status_code,
    )


def home(request):
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    memberships = request.user.memberships.select_related("organization")
    notifications = request.user.notifications.filter(read_at__isnull=True)[:10]
    return render(
        request,
        "core/dashboard.html",
        {"memberships": memberships, "notifications": notifications},
    )

# Create your views here.
