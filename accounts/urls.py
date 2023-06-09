from django.urls import path
from . import views

urlpatterns = [
    path('interviewee_register/', views.IntervieweeRegisterAPI.as_view(), name = 'Interviewee Registration'),
    path('interviewee_update/', views.IntervieweeAPI.as_view()),
    path('interviewee_get/<str:sapid>', views.IntervieweeSapAPI.as_view()),
    path('login/', views.LoginAPI.as_view(), name = 'login'),
    path('application/',views.ApplicationView.as_view(), name = 'application'),
    path('resources/', views.ResourcesAPI.as_view(), name = 'resources'),
    path('tasks/', views.TaskAPI.as_view(), name='tasks'),
    path('interviews/', views.InterviewAPI.as_view(), name='interviews'),
    path('appl_num/<str:sapid>', views.NumberOfApplicationAPI, name='countofappl'),
    path('interviewee_panel/',views.IntervieweePanelAPI.as_view(), name='interview panels'),

#Interviewer APIs
    path('panel_details/', views.PanelAPI.as_view(), name='panel'),
    path('panel_details_all/',views.All_Panel_data.as_view(),name='all_panels'),
    path('view_candidate/<str:sapid>', views.Candidate_test_API.as_view(), name='candidate_view'),
    path('scorecard_get/<str:sapid>/<str:stack>', views.ScorecardGetAPI.as_view(), name='scorecard_get'),
    path('remarks/', views.RemarksAPI.as_view(), name='remarks'),
    path('score/', views.ScoreAPI.as_view(), name='score'),
    path('scheduling/',views.Scheduler.as_view(), name = 'Scheduler'),
    path('question/<str:stack>',views.QuestionAPI.as_view(), name = 'question'),
    path('scheduled/',views.schedule_interviews,name='scheduler')
]