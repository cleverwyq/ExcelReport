"""ExcelReport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from .views import RedirectPage, ListPage, \
    GetCodePage, RunPage, DimensionMeasureView, \
    SaveReportView, Test, DownloadReportView, SendJson

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', RedirectPage.as_view(), name="redirect"),
    url(r'^auth/', GetCodePage.as_view(), name="getcode"),
    url(r'^list/', ListPage.as_view(), name="to"),
    url(r'^run/', RunPage.as_view(), name="run report"),
    url(r'^views/', DimensionMeasureView.as_view(), name="report fields"),
    url(r'^test/', Test.as_view(), name="test"),
    url(r'^fields/', SaveReportView.as_view(), name="Save Report"),
    url(r'^dl/', DownloadReportView.as_view(), name="Download"),
    url(r'^givemejson/', SendJson.as_view(), name="tt")
]
