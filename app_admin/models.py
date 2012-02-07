from django.contrib import admin
from app_admin.admin import AppAdminSite

# replace default AdminSite with AppAdminSite
admin.site = AppAdminSite()
admin_site = admin.site
