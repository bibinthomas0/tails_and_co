from django.urls import path,include
from owner import views

urlpatterns = [
path('deletecategory/<int:id>/',views.Deletecategory,name='deletecategory'),
path('adminusers',views.Adminusers,name='adminusers'),
path('admindashboard',views.AdminDashboard,name='admindashboard'),
path('adminlogin',views.Adminlogin,name='adminlogin'),
path('addproduct',views.Addproduct,name='addproduct'),
path('registration',views.Adminregistration,name='registration'),
path('adminotp',views.Adminotppage,name='adminotp'),
path('deleteuser/<int:id>/',views.Deleteuser,name='deleteuser'),
path('admincategory',views.Admincategory,name='admincategory'),
path('block/<int:id>/',views.block,name='block'),
# path('addvariations/<int:id>',views.Addvariations,name='addvariations'),
path('variations/<int:id>',views.Variations,name='variations'),
path('imagess/<id>/',views.Imagess,name='imagess'),
# path('addcategory',views.Deletecategory,name='deletecategory'),
path('deletesubcategory/<int:id>/',views.Deletesubcategory,name='deletesubcategory'),
path('addsubcategory',views.Addsubcategory,name='addsubcategory'),
path('deleteproduct/<int:id>/',views.Productdelete,name='deleteproduct'),
path('ordermanagement',views.Orders,name='ordermanagement'),
path('update_order_status/<int:id>/',views.update_order_status,name='update_order_status'),
path('variantedit/<int:id>/',views.variantedit,name='variantedit'),
path('deletevariant/<int:id>/',views.deletevariant,name='deletevariant'),
path('adminlogout',views.adminlogout,name='adminlogout'),
path('admincoupon', views.Admincoupon, name='admincoupon'),
path('adminorder_deatails/<int:id>/', views.adminorder_deatails, name='adminorder_deatails'),
path('order_cancel/<int:id>/', views.order_cancel, name='order_cancel'),
path('deleteimage/<int:id>/', views.deleteimage, name='deleteimage'),
path('cropimage', views.cropimage, name='cropimage'),
path('croper', views.croper, name='croper'),
path('deactivatecoupon/<int:id>/', views.deactivatecoupon, name='deactivatecoupon'),
path('returns', views.Returns, name='returns'),
path('returndetails/<int:id>/', views.returndetails, name='returndetails'),
path('update_return_status/<int:id>/', views.update_return_status, name='update_return_status'),
path('owner_notifications', views.owner_notifications, name='owner_notifications'),
path('orderchartsdaily/', views.sales_chart_daily, name='orderchartsdaily'),
path('orderchartsweekly/', views.sales_chart_weekly, name='orderchartsweekly'),
path('orderchartsmonthly/', views.sales_chart_monthly, name='orderchartsmonthly'),
path('order_filter/', views.order_filter_view, name='order_filter'),
path('order_return_filter/', views.order_return_filter_view, name='order_return_filter'),

]