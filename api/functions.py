import datetime

def custom_serializer(obj):
    if isinstance(obj, datetime.datetime):
        # Format datetime objects as "MM/DD/YYYY HH:MM"
        print("LOOK AT THIS ITEM", obj.strftime('%m/%d/%Y %H:%M'))
        return obj.strftime('%m/%d/%Y %H:%M')
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")