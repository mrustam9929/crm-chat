from datetime import datetime


def get_filter_date(data) -> tuple:
    """Вернет, если есть, отрезок даты если есть"""
    has_date = False
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    if start_date and end_date:
        has_date = True
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    return has_date, start_date, end_date
