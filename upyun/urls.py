from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('upyun.views',

    url(r'^upload_img/$', 'upload_img'),
    url(r'^test/$', 'test'),
)
