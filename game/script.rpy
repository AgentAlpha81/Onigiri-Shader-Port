label start:
    "Это первое технодемо кастомных векторов, где будут продемонстрированы шейдеры рейкастинга от Onigiri."
    "Кастомные векторы для Ren'Py используются для управления камерой."
    "Управление: WASD - ходить, Space - подняться вверх, Shift - опуститься вниз."
    menu:
        "Какой шейдер смотрим?"
        "Raycasting а.к.а. 3D на 2D-движке":
            call screen onigiri("onigiri_raycasting")
            
        "Raytracing без RTX":
            call screen onigiri("onigiri_raytracing")