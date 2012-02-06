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


Installation
------------

    pip install -e git://github.com/fusionbox/django-app-admin.git#egg=django-app-admin

Usage
-----
Add `app_admin` to your `INSTALLED_APPS`.
