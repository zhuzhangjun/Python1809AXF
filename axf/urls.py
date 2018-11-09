from django.conf.urls import url

from axf import views

urlpatterns = [
    url(r'^$',views.home,name='home'),  # 首页

    url(r'^home/$',views.home,name='home'),  # 首页
    url(r'^market/(\d+)/(\d+)/(\d+)/$',views.market,name='market'),  # 超市
    url(r'^cart/$',views.cart,name='cart'),  # 购物车
    url(r'^mine/$',views.mine,name='mine'),  # 我的

    url(r'^login/$',views.login,name='login'),  # 登录
    url(r'^register/$',views.register,name='register'),  # 注册页面
    url(r'^quit/$',views.quit,name='quit'),  # 退出登录

    url(r'addcart/$',views.addcart,name='addcart'), # 加操作
    url(r'subcart/$',views.subcart,name='subcart'), # 减操作

    # url(r'changecartstatus/$',views.changecartstatus,name='changecartstatus'),  # 修改选中状态
]