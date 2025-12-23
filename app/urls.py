from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.main, name="main"),

    # 회원가입/로그인
    path('signup/', views.signup, name="signup"),
    path('login/', views.login_view, name="login"),
    path('check-username/', views.check_username, name='check_username'),  
    path('logout/', views.logout_view, name='logout'), 

    # 퀴즈
    path('quiz/', views.main_category_list, name="main_category_list"),                    
    path('quiz/<int:main_id>/', views.sub_category_list, name="sub_category_list"),       
    path('quiz/sub/<int:sub_id>/', views.quiz_view, name="quiz_view"),                    
    path('quiz/sub/<int:sub_id>/submit/', views.quiz_submit_router, name="quiz_submit"),    

    # 포인트 / 유저 정보 / 은행
    path("user/", views.user_info, name="user_info"),
    path("point/", views.point, name="point"),
    path("point/withdraw/", views.withdraw_view, name="withdraw"),
    path("point/withdraw/process/", views.withdraw_process, name="withdraw_process"),
    path("point/records/", views.point_records, name="point_records"),
    path("point/gift/", views.gift_view, name="gift"),
    path("point/gift/buy/", views.gift_buy, name="gift_buy"),
    path("user/bank/", views.bank_info_view, name="bank_info"),
    path("user/bank/save/", views.bank_info_save, name="bank_info_save"),
    
    # 공지
    path("notice/", views.notice_list, name="notice_list"),
    path("notice/create/", views.notice_create, name="notice_create"),
    path("notice/<int:pk>/", views.notice_detail, name="notice_detail"),  # ← 상세 페이지
    path("notice/delete/<int:notice_id>/", views.notice_delete, name="notice_delete"),
]
