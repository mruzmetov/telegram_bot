from datetime import datetime

def get_time_left(deadline_str):
    deadline = datetime.strptime(deadline_str, "%d/%m/%Y %H:%M:%S")
    now = datetime.now()
    delta = deadline - now

    if delta.total_seconds() <= 0:
        return "⚠️ Muddati tugadi!"
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    return f"{days} kun, {hours} soat, {minutes} daqiqa"
