from datetime import date, datetime
from typing import List, Any
from asgiref.sync import sync_to_async
from apps.main.models import *
from apps.superadmin.models import *
from django.db.models import F, ExpressionWrapper, DurationField
from datetime import timedelta


@sync_to_async
def get_employee(user_id):
    try:
        user = Employee.objects.filter(user_id=user_id).first()
        return user
    except:
        return None


@sync_to_async
def add_employee(user_id, full_name, admin_id):
    # try:
    Employee.objects.create(user_id=user_id, name=full_name).save()
    admin = Administrator.objects.filter(telegram_id=admin_id).first()
    emp = Employee.objects.filter(user_id=user_id).first()
    emp.filial = admin.filial
    emp.save()
    return emp
    # except Exception as exx:
    #     print(exx)
    #     return None

@sync_to_async
def get_telegram_user(user_id: int) -> TelegramUser:
    try:
        return TelegramUser.objects.get(user_id=user_id)
    except TelegramUser.DoesNotExist:
        return None

@sync_to_async
def add_telegram_user(user_id, username, first_name, last_name):
    try:
        user = TelegramUser.objects.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        return user
    except Exception as exx:
        print(exx)
        return None


@sync_to_async
def get_all_filials():
    return list(Filial.objects.all())
    
    
@sync_to_async
def get_employees() -> List[Employee]:
    eps = Employee.objects.all()
    return eps


@sync_to_async
def get_employees() -> List[Employee]:
    eps = Employee.objects.all()
    return eps


@sync_to_async
def is_user_employee(user_id: int) -> bool:
    return Employee.objects.filter(user_id=user_id).exists()


@sync_to_async
def is_user_admin(user_id: int) -> bool:
    return Administrator.objects.filter(telegram_id=user_id).exists()


@sync_to_async
def get_admins_by_filial(filial_id: int):
    return list(Administrator.objects.filter(filial_id=filial_id))


@sync_to_async
def get_all_admin_ids() -> list[int]:
    user_ids = list(Administrator.objects.values_list('telegram_id', flat=True))
    print(user_ids)
    return user_ids


@sync_to_async
def get_all_addresses()-> list[str]:
    return list(Location.objects.filter(name__isnull=False).values_list("name", flat=True))


@sync_to_async
def get_filial_location(user_id):
    admin = Administrator.objects.filter(telegram_id=user_id).first()
    return Location.objects.filter(filial = admin.filial).last()


@sync_to_async
def save_location(name, lat, lon, user_id):
    try:
        admin = Administrator.objects.get(telegram_id=user_id)
        location = Location.objects.filter(filial=admin.filial).first()
        if location:
            # Mavjud locationni yangilaymiz
            location.name = name
            location.latitude = lat
            location.longitude = lon
            location.save()
        else:
            # Yangi location yaratamiz
            Location.objects.create(
                filial=admin.filial,
                name=name,
                latitude=lat,
                longitude=lon
            )    
    except Exception as exx:
        print(exx)
        return None
    
    
        
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

async def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="myuzbot (jigar@t.me)")
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        return location.address if location else "Nomaʼlum manzil"
    except GeocoderTimedOut:
        return "Geocoding vaqti tugadi"
    

@sync_to_async
def create_employee_if_not_exists(user_id, full_name):
    if not Employee.objects.filter(user_id=user_id).exists():
        Employee.objects.create(user_id=user_id, full_name=full_name)
        

@sync_to_async
def get_all_weekdays():
    return list(Weekday.objects.all())


@sync_to_async
def save_work_schedule(user_id, data):
    admin = Administrator.objects.filter(telegram_id=user_id).first()

    employee = Employee.objects.filter(user_id=data["employee_id"]).first()
    if not employee:
        raise Exception("Foydalanuvchi topilmadi!")
    
    weekdays = Weekday.objects.filter(name__in=data["selected_weekdays"])
    ws = WorkSchedule.objects.create(
        employee=employee,
        start=data["start"],
        end=data["end"],
        admin=admin
    )
    ws.weekday.set(weekdays)
    

@sync_to_async
def delete_employee_by_user_id(user_id: int) -> bool:
    employee = Employee.objects.filter(user_id=user_id).first()
    if employee:
        employee.delete()
        return True  # O'chirildi
    return False  # Topilmadi


@sync_to_async
def get_employee_schedule_text(employee_id: int) -> str:
    try:
        emp = Employee.objects.filter(user_id=employee_id).first()
        if not emp:
            return "❌ Xodim topilmadi."

        schedules = WorkSchedule.objects.filter(employee_id=emp.id).prefetch_related('weekday')
        
        if not schedules:
            return "⚠️ Ish jadvali mavjud emas."

        jadval_matni = "🗓 Sizning ish jadvalingiz:\n\n"
        for schedule in schedules:
            kunlar = ", ".join([w.name for w in schedule.weekday.all()])
            vaqt = f"{schedule.start.strftime('%H:%M')} - {schedule.end.strftime('%H:%M')}"
            jadval_matni += f"📅 {kunlar} | ⏰ {vaqt}\n"

        return jadval_matni
    except Exception as e:
        print(f"Xatolik: {e}")
        return "⚠️ Ish jadvali topilmadi yoki xato yuz berdi."

@sync_to_async
def get_daily_report(filial):
    today = datetime.today().date()  # faqat sana

    records = (
        Attendance.objects.filter(employee__filial_id=filial.id, date=today)
        .annotate(
            worked_hours=ExpressionWrapper(
                F("check_out") - F("check_in"),
                output_field=DurationField()
            )
        )
        .select_related("employee")
    )

    lines = []
    for rec in records:
        worked = rec.worked_hours or timedelta()
        hours, remainder = divmod(int(worked.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)

        lines.append(
            f"👤 {rec.employee.name}\n"
            f" ⏰ Keldi: {rec.check_in.strftime('%H:%M') if rec.check_in else '-'}\n"
            f" 🚪 Ketdi: {rec.check_out.strftime('%H:%M') if rec.check_out else '-'}\n"
            f" ⌛ Ishlagan: {hours:02d}:{minutes:02d}"
        )
    if not lines:
        return "Bugun hech kim kelmadi."
    return "\n\n".join(lines)

# @sync_to_async
# def generate_attendance_excel_file(start_date, end_date, file_name="hisobot.xlsx"):
#     import os
#     import pandas as pd
#     from datetime import datetime, timedelta

#     data = []
#     current_date = start_date
#     while current_date <= end_date:
#         weekday_name = current_date.strftime('%A').lower()
#         weekday = Weekday.objects.filter(name_en__iexact=weekday_name).first()
#         if not weekday:
#             current_date += timedelta(days=1)
#             continue

#         schedules = WorkSchedule.objects.filter(weekday=weekday).select_related('employee')

#         for schedule in schedules:
#             emp = schedule.employee
#             attendance = Attendance.objects.filter(employee=emp, date=current_date).first()
#             check_in = attendance.check_in if attendance else None
#             check_out = attendance.check_out if attendance else None

#             in_diff = out_diff = None
#             if check_in:
#                 delta_in = datetime.combine(current_date, check_in) - datetime.combine(current_date, schedule.start)
#                 in_diff = int(delta_in.total_seconds() // 60)
#             if check_out:
#                 delta_out = datetime.combine(current_date, check_out) - datetime.combine(current_date, schedule.end)
#                 out_diff = int(delta_out.total_seconds() // 60)
#             print(schedule.id)
#             data.append({
#                 "Sana": current_date.strftime("%d.%m.%Y"),
#                 "Xodim": emp.name,
#                 "Xafta kuni": weekday.name,
#                 "Kutilgan kirish": schedule.start.strftime("%H:%M"),
#                 "Amalda kirgan": check_in.strftime("%H:%M") if check_in else "-",
#                 "Kech/erta kirish (min)": in_diff,
#                 "Kutilgan chiqish": schedule.end.strftime("%H:%M"),
#                 "Amalda chiqqan": check_out.strftime("%H:%M") if check_out else "-",
#                 "Kech/erta chiqish (min)": out_diff,
#             })

#         current_date += timedelta(days=1)

#     df = pd.DataFrame(data)

#     dir_path = "media/reports"
#     os.makedirs(dir_path, exist_ok=True)
#     full_path = os.path.join(dir_path, file_name)

#     with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name="Hisobot")
        
#     print(full_path)

#     return full_path

@sync_to_async
def generate_attendance_excel_file(user_id, start_date, end_date, file_name="hisobot.xlsx"):
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    
    
    admin = Administrator.objects.filter(telegram_id=user_id).first()
    data = []
    current_date = start_date
    while current_date <= end_date:
        weekday_name = current_date.strftime('%A').lower()
        weekday = Weekday.objects.filter(name_en__iexact=weekday_name).first()
        if not weekday:
            current_date += timedelta(days=1)
            continue

        schedules = WorkSchedule.objects.filter(weekday=weekday, employee__filial_id = admin.filial.id).all()

        for schedule in schedules:
            if not schedule.employee.created_at.date() <= current_date.date():
                continue
            emp = schedule.employee
            attendance = Attendance.objects.filter(employee=emp, date=current_date).first()
            check_in = attendance.check_in if attendance else None
            check_out = attendance.check_out if attendance else None

            in_diff = out_diff = None
            if check_in:
                delta_in = datetime.combine(current_date, check_in) - datetime.combine(current_date, schedule.start)
                in_diff = int(delta_in.total_seconds() // 60)
            if check_out:
                delta_out = datetime.combine(current_date, check_out) - datetime.combine(current_date, schedule.end)
                out_diff = int(delta_out.total_seconds() // 60)

            data.append({
                "Sana": current_date.strftime("%d.%m.%Y"),
                "Xodim": emp.name,
                "Xafta kuni": weekday.name,
                "Kutilgan kirish": schedule.start.strftime("%H:%M"),
                "Amalda kirgan": check_in.strftime("%H:%M") if check_in else "-",
                "Kech/erta kirish (min)": in_diff,
                "Kutilgan chiqish": schedule.end.strftime("%H:%M"),
                "Amalda chiqqan": check_out.strftime("%H:%M") if check_out else "-",
                "Kech/erta chiqish (min)": out_diff,
            })

        current_date += timedelta(days=1)

    df = pd.DataFrame(data)

    dir_path = "files/reports"
    os.makedirs(dir_path, exist_ok=True)
    full_path = os.path.join(dir_path, file_name)
    df.to_excel(full_path, index=False)
    print(full_path)
    return full_path
