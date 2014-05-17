Что это?
=========

Библиотека классов, отвечающих за фильтрацию queryset'ов django. Фильтр - это callable (т. е. функция),
принимающая queryset и возвращающая queryset::

    filtered_queryset = filtr(Model.objects.all())

Хотя основной usecase - Пример объя


