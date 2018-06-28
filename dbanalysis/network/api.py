urlpatterns = [
    path('api/stopdata/<int:stopid>/<str:request>',views.get_stop_data),
    path('api/timetable/<int:stopid>/<int:from>/<int:to>', views.get_timetable)
    path('api/routes/<str:routeid>/<str:request>',views.get_route_details)
    path('api/all-stops',views.get_all_stops)
    
]
