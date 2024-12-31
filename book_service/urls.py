from rest_framework import routers

from book_service import views

router = routers.DefaultRouter()
router.register(r'books', views.BookViewSet)


urlpatterns = []
urlpatterns += router.urls


app_name = 'book_service'
