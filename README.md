Django AppAdmin
===============

There is not an easy way in the django-admin to add app-level views to the
home page and app-page (/admin/, /admin/app/) without lots of template
inheritance and subclassing AdminSite.  And even once you do that there is a
surprise in store: if you want to add some actions to you `app_index`, you
have to provide implement *two* views, not one (one for the admin home —
`index` — and another for the app page — `app_index`) but two view methods.
In most cases one view will do the job, and AppAdmin will use `index` if
`app_index` is not provided.

AppAdmin also provides classes and templates that make building admin-like
pages easy.  For instance, the `AsAdminForm` class provides an `as_admin`
method that outputs the classes and wrappers you'll need to make a form that
looks like other django admin forms.

Installation
------------

    pip install -e git://github.com/fusionbox/django-app-admin.git#egg=django-app-admin

 AppAdminSite Usage
--------------------

Add `app_admin` to your `INSTALLED_APPS`.

In `urls.py`, add the following:

``` python
from django.contrib import admin
from app_admin.admin import AppAdminSite

# replace default AdminSite with AppAdminSite
admin.site = AppAdminSite()
admin_site = admin.site
```

 Other classes
---------------

+ `AsAdminForm` - Extend to have an as_admin method on your forms.

 Templates
-----------

+ `admin/app_admin/submit.html` - outputs (*just*) a "Save" button.
+ `admin/app_admin/app_bucket.html` - for use on the home page.
+ `admin/app_admin/app_index.html` - the /admin/app-name/ page.
+ `admin/app_admin/index.html` - Outputs the entire home page.
  It is probably better to override app_bucket.html, not this one.
