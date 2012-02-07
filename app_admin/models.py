from django.contrib import admin
from appadmin.admin import AppAdminSite

# replace default AdminSite with AppAdminSite
admin.site = AppAdminSite()
admin_site = admin.site
