from datetime import datetime
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Car, Brand, BodyType, GearboxType, FuelType, DriveType


def home(request):
    """Главная страница сайта"""
    recommended_cars = list(Car.objects.filter(is_recommended=True).select_related(
        'brand', 'body', 'gearbox', 'fuel', 'drive'
    ).order_by('-created_at'))
    recommended_car_pages = [
        recommended_cars[index:index + 4]
        for index in range(0, len(recommended_cars), 4)
    ]
    
    context = {
        'recommended_cars': recommended_cars,
        'recommended_car_pages': recommended_car_pages,
    }
    return render(request, "index.html", context)


def cars(request):
    """Каталог автомобилей с полноценной безопасной фильтрацией"""
    # Оптимизация запроса: сразу подгружаем связанные ForeignKey модели
    cars_list = Car.objects.all().select_related(
        'brand', 'body', 'gearbox', 'fuel', 'drive'
    ).order_by('-created_at')

    # Получаем параметры фильтра из GET-запроса
    brand_id = request.GET.get('brand')
    model_query = request.GET.get('model')
    price_from = request.GET.get('price_from')
    price_to = request.GET.get('price_to')
    year_from = request.GET.get('year_from')
    year_to = request.GET.get('year_to')
    body_id = request.GET.get('body')
    gearbox_id = request.GET.get('gearbox')
    fuel_id = request.GET.get('fuel')
    drive_id = request.GET.get('drive')
    engine_volume = request.GET.get('engine_volume')

    # Безопасное применение фильтров (проверяем, что значение не пустое)
    if brand_id and brand_id.strip():
        cars_list = cars_list.filter(brand_id=brand_id)

    if model_query and model_query.strip():
        cars_list = cars_list.filter(name__icontains=model_query.strip())

    if price_from and price_from.isdigit():
        cars_list = cars_list.filter(price__gte=int(price_from))

    if price_to and price_to.isdigit():
        cars_list = cars_list.filter(price__lte=int(price_to))

    if year_from and year_from.isdigit():
        cars_list = cars_list.filter(year__gte=int(year_from))

    if year_to and year_to.isdigit():
        cars_list = cars_list.filter(year__lte=int(year_to))

    if body_id and body_id.strip():
        cars_list = cars_list.filter(body_id=body_id)

    if gearbox_id and gearbox_id.strip():
        cars_list = cars_list.filter(gearbox_id=gearbox_id)

    if fuel_id and fuel_id.strip():
        cars_list = cars_list.filter(fuel_id=fuel_id)

    if drive_id and drive_id.strip():
        cars_list = cars_list.filter(drive_id=drive_id)

    if engine_volume and engine_volume.strip():
        cars_list = cars_list.filter(engine__icontains=engine_volume.strip())

    paginator = Paginator(cars_list, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    context = {
        'cars': page_obj.object_list,
        'page_obj': page_obj,
        'query_params': query_params,
        'all_brands': Brand.objects.all(),
        'all_bodies': BodyType.objects.all(),
        'all_gearboxes': GearboxType.objects.all(),
        'all_fuels': FuelType.objects.all(),
        'all_drives': DriveType.objects.all(),
        'years_list': list(range(datetime.now().year, 1989, -1)),
    }
    return render(request, "cars.html", context)


def car_detail_view(request, slug):
    """Детальная страница автомобиля"""
    car = get_object_or_404(
        Car.objects.select_related('brand', 'body', 'gearbox', 'fuel', 'drive'), 
        slug=slug
    )
    
    # Похожие автомобили (той же марки, исключая текущий)
    similar_cars = Car.objects.filter(brand=car.brand).exclude(pk=car.pk).select_related(
        'brand', 'body', 'gearbox', 'fuel', 'drive'
    )[:3]

    context = {
        'car': car,
        'similar_cars': similar_cars,
    }
    return render(request, 'car_detail.html', context)


def contacts(request):
    """Страница контактов"""
    return render(request, "contacts.html")