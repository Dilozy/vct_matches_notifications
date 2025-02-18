from timezonefinder import TimezoneFinder


def get_timezone_by_coordinates(latitude: float, longitude: float) -> str:
    """
    Определяет временной пояс по координатам.
    Возвращает строку с названием временного пояса или None, если определить не удалось.
    """
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    
    return timezone_str if timezone_str else None
