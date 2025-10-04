from django.shortcuts import render
from restaurants.models import RestaurantApprovalRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from restaurants.models import TableBooking
from restaurants.models import Restaurant
from restaurants.models import MenuItem, Order, Review
from django.shortcuts import render
from django.db.models import Sum, Avg, Count
from datetime import date, timedelta, datetime
import calendar

def admin_dashboard_view(request):
    # Get filter parameters
    date_range = request.GET.get('date_range', 'all')
    custom_date = request.GET.get('custom_date', '')
    period = request.GET.get('period', 'monthly')
    
    today = date.today()
    
    # Date filtering logic
    if date_range == 'today':
        start_date = today
        end_date = today
        date_label = f"Today ({today.strftime('%b %d, %Y')})"
    elif date_range == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = today - timedelta(days=1)
        date_label = f"Yesterday ({start_date.strftime('%b %d, %Y')})"
    elif date_range == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
        date_label = f"Last 7 Days ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    elif date_range == 'month':
        start_date = today.replace(day=1)
        end_date = today
        date_label = f"This Month ({start_date.strftime('%B %Y')})"
    elif date_range == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
        date_label = f"This Year ({start_date.year})"
    elif date_range == 'custom' and custom_date:
        try:
            start_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
            end_date = start_date
            date_label = f"Custom Date ({start_date.strftime('%b %d, %Y')})"
        except:
            start_date = None
            end_date = None
            date_label = "All Time"
    else:
        start_date = None
        end_date = None
        date_label = "All Time"

    # Base querysets with proper date filtering
    orders_queryset = Order.objects.all()
    bookings_queryset = TableBooking.objects.all()
    
    if start_date and end_date:
        orders_queryset = orders_queryset.filter(timestamp__date__range=[start_date, end_date])
        bookings_queryset = bookings_queryset.filter(created_at__date__range=[start_date, end_date])

    # Active Menu Items with date filtering
    if start_date and end_date:
        active_menu_items = MenuItem.objects.filter(
            is_available=True,
            created_at__date__lte=end_date
        ).count()
        
        new_menu_items = MenuItem.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count()
    else:
        active_menu_items = MenuItem.objects.filter(is_available=True).count()
        first_day_month = today.replace(day=1)
        last_day_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        new_menu_items = MenuItem.objects.filter(
            created_at__range=(first_day_month, last_day_month)
        ).count()

    # Total Orders and Bookings
    total_orders = orders_queryset.count()
    total_bookings = bookings_queryset.count()
    total_orders_all = total_orders + total_bookings
    
    # Status counts with proper filtering
    total_confirmed = (orders_queryset.filter(status='confirmed').count() + 
                      bookings_queryset.filter(status='confirmed').count())
    total_delivered = orders_queryset.filter(status='delivered').count()
    total_pending = (orders_queryset.filter(status='pending').count() + 
                    bookings_queryset.filter(status='pending').count())
    total_preparing = orders_queryset.filter(status='preparing').count()
    
    # Completed and pending calculations
    completed_orders_all = total_delivered + bookings_queryset.filter(status='confirmed').count()
    pending_orders_all = (total_pending + total_preparing + 
                         orders_queryset.filter(status='confirmed').count())
    
    completed_pct = int((completed_orders_all / total_orders_all * 100) if total_orders_all else 0)

    # Revenue calculations with proper filtering
    order_revenue = orders_queryset.filter(status='delivered').aggregate(
        total=Sum('total_price'))['total'] or 0
    booking_revenue = bookings_queryset.filter(status='confirmed').aggregate(
        total=Sum('total_amount'))['total'] or 0
    current_revenue = float(order_revenue) + float(booking_revenue)

    # Revenue growth calculation
    prev_monthly_revenue = 0
    if start_date and end_date:
        # Calculate previous period based on current filter
        if date_range == 'today':
            prev_start = start_date - timedelta(days=1)
            prev_end = end_date - timedelta(days=1)
        elif date_range == 'yesterday':
            prev_start = start_date - timedelta(days=1)
            prev_end = end_date - timedelta(days=1)
        elif date_range == 'week':
            prev_start = start_date - timedelta(days=7)
            prev_end = end_date - timedelta(days=7)
        elif date_range == 'month':
            prev_start = (start_date - timedelta(days=30)).replace(day=1)
            prev_end = start_date - timedelta(days=1)
        elif date_range == 'year':
            prev_start = start_date.replace(year=start_date.year-1)
            prev_end = end_date.replace(year=end_date.year-1)
        elif date_range == 'custom':
            prev_start = start_date - timedelta(days=1)
            prev_end = end_date - timedelta(days=1)
        else:
            prev_start = None
            prev_end = None

        if prev_start and prev_end:
            prev_order_rev = Order.objects.filter(
                timestamp__date__range=[prev_start, prev_end],
                status='delivered'
            ).aggregate(total=Sum('total_price'))['total'] or 0
            prev_book_rev = TableBooking.objects.filter(
                created_at__date__range=[prev_start, prev_end],
                status='confirmed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            prev_monthly_revenue = float(prev_order_rev) + float(prev_book_rev)
    else:
        # For "All Time", compare with previous month
        first_day_month = today.replace(day=1)
        last_day_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        prev_month_end = first_day_month - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        
        prev_order_rev = Order.objects.filter(
            timestamp__range=(prev_month_start, prev_month_end),
            status='delivered'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        prev_book_rev = TableBooking.objects.filter(
            created_at__range=(prev_month_start, prev_month_end),
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        prev_monthly_revenue = float(prev_order_rev) + float(prev_book_rev)

    # Calculate revenue growth
    if prev_monthly_revenue > 0:
        revenue_growth = int(((current_revenue - prev_monthly_revenue) / prev_monthly_revenue) * 100)
    else:
        revenue_growth = 0 if current_revenue == 0 else 100

    # Net Profit and growth rate
    deduction_rate = 0.20
    net_profit = current_revenue * (1 - deduction_rate)
    growth_rate = abs(revenue_growth * 0.1)

    # Targets (always current month for progress bars)
    first_day_month = today.replace(day=1)
    last_day_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    
    monthly_orders_count = Order.objects.filter(
        timestamp__range=(first_day_month, last_day_month)
    ).count()
    monthly_bookings_count = TableBooking.objects.filter(
        created_at__range=(first_day_month, last_day_month)
    ).count()
    monthly_orders = monthly_orders_count + monthly_bookings_count
    target_monthly_orders = 3000

    # Customer Satisfaction (filtered if date range selected)
    if start_date and end_date:
        customer_satisfaction = Review.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).aggregate(avg=Avg('rating'))['avg'] or 0.0
    else:
        customer_satisfaction = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

    # Revenue Target
    target_revenue = 50000

    # Today's Stats (always current day)
    todays_orders = Order.objects.filter(timestamp__date=today).count()
    todays_bookings = TableBooking.objects.filter(created_at__date=today).count()
    todays_orders_total = todays_orders + todays_bookings
    
    todays_completed_orders = Order.objects.filter(timestamp__date=today, status='delivered').count()
    todays_completed_bookings = TableBooking.objects.filter(created_at__date=today, status='confirmed').count()
    todays_completed = todays_completed_orders + todays_completed_bookings
    
    todays_in_progress_orders = Order.objects.filter(timestamp__date=today, status='preparing').count()
    todays_in_progress_bookings = TableBooking.objects.filter(created_at__date=today, status='pending').count()
    todays_in_progress = todays_in_progress_orders + todays_in_progress_bookings

    # Alerts Count
    high_priority_reviews = Review.objects.filter(priority='high').count()
    pending_approvals = RestaurantApprovalRequest.objects.filter(is_resolved=False).count()
    alerts_count = high_priority_reviews + pending_approvals

    # Revenue Analytics Data for charts
    order_revs = []
    book_revs = []
    revenues = []
    month_names = []
    
    # Get last 3 months data for chart
    current = first_day_month
    for i in range(3):
        first = current.replace(day=1)
        last = first.replace(day=calendar.monthrange(current.year, current.month)[1])
        ord_rev = Order.objects.filter(
            timestamp__range=(first, last),
            status='delivered'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        book_rev = TableBooking.objects.filter(
            created_at__range=(first, last),
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        order_revs.append(float(ord_rev))
        book_revs.append(float(book_rev))
        revenues.append(float(ord_rev) + float(book_rev))
        month_names.append(first.strftime("%B"))
        current = first - timedelta(days=1)
    
    order_revs = order_revs[::-1]
    book_revs = book_revs[::-1]
    revenues = revenues[::-1]
    month_names = month_names[::-1]

    # Current revenue breakdown for pie chart
    order_revenue_current = order_revs[-1] if order_revs else 0
    booking_revenue_current = book_revs[-1] if book_revs else 0
    total_revenue_current = order_revenue_current + booking_revenue_current
    
    if total_revenue_current > 0:
        orders_pct = (order_revenue_current / total_revenue_current) * 100
        bookings_pct = (booking_revenue_current / total_revenue_current) * 100
    else:
        orders_pct = 0
        bookings_pct = 0

    # Dynamic data for different chart periods
    # Daily data (last 7 days)
    daily_data = []
    daily_labels = []
    for i in range(7):
        day = today - timedelta(days=i)
        start_of_day = datetime.combine(day, datetime.min.time())
        end_of_day = datetime.combine(day, datetime.max.time())
        
        daily_ord_rev = Order.objects.filter(
            timestamp__range=(start_of_day, end_of_day),
            status='delivered'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        daily_book_rev = TableBooking.objects.filter(
            created_at__range=(start_of_day, end_of_day),
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        daily_data.append({
            'orders': float(daily_ord_rev),
            'bookings': float(daily_book_rev),
            'total': float(daily_ord_rev) + float(daily_book_rev)
        })
        daily_labels.append(day.strftime("%a %d"))
    
    daily_data.reverse()
    daily_labels.reverse()
    
    # Weekly data (last 4 weeks)
    weekly_data = []
    weekly_labels = []
    for i in range(4):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        
        weekly_ord_rev = Order.objects.filter(
            timestamp__range=(week_start, week_end),
            status='delivered'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        weekly_book_rev = TableBooking.objects.filter(
            created_at__range=(week_start, week_end),
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        weekly_data.append({
            'orders': float(weekly_ord_rev),
            'bookings': float(weekly_book_rev),
            'total': float(weekly_ord_rev) + float(weekly_book_rev)
        })
        weekly_labels.append(f"Week {4-i}")
    
    weekly_data.reverse()
    weekly_labels.reverse()
    
    # Yearly data (last 3 years)
    yearly_data = []
    yearly_labels = []
    for i in range(3):
        year = today.year - i
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        
        yearly_ord_rev = Order.objects.filter(
            timestamp__range=(year_start, year_end),
            status='delivered'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        yearly_book_rev = TableBooking.objects.filter(
            created_at__range=(year_start, year_end),
            status='confirmed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        yearly_data.append({
            'orders': float(yearly_ord_rev),
            'bookings': float(yearly_book_rev),
            'total': float(yearly_ord_rev) + float(yearly_book_rev)
        })
        yearly_labels.append(str(year))
    
    yearly_data.reverse()
    yearly_labels.reverse()

    # Get user initials from full_name field
    user = request.user
    user_initials = ""
    
    if user.full_name:
        # Split full_name into parts
        name_parts = user.full_name.split()
        if len(name_parts) >= 2:
            # First letter of first name + first letter of last name
            user_initials = f"{name_parts[0][0]}{name_parts[-1][0]}".upper()
        elif len(name_parts) == 1:
            # Only one name - take first 2 letters
            user_initials = user.full_name[:2].upper()
        else:
            # No name available
            user_initials = user.email[:2].upper() if user.email else "ZZ"
    else:
        # Fallback to email if no full_name
        user_initials = user.email[:2].upper() if user.email else "ZZ"

    context = {
        'active_menu_items': active_menu_items,
        'new_menu_items': new_menu_items,
        'total_orders_all': total_orders_all,
        'completed_orders_all': completed_orders_all,
        'pending_orders_all': pending_orders_all,
        'completed_pct': completed_pct,
        'monthly_revenue': f"₹{current_revenue:,.2f}",
        'revenue_growth': revenue_growth,
        'net_profit': f"₹{net_profit:,.2f}",
        'growth_rate': f"{growth_rate:.1f}",
        'total_revenue': f"₹{current_revenue:,.2f}",
        'monthly_orders_str': f"{monthly_orders} / {target_monthly_orders}",
        'satisfaction_str': f"{customer_satisfaction:.1f} / 5.0",
        'revenue_str': f"₹{current_revenue:,.2f} / ₹{target_revenue:,.2f}",
        'monthly_progress': min((monthly_orders / target_monthly_orders * 100) if target_monthly_orders else 0, 100),
        'satisfaction_progress': min((customer_satisfaction / 5 * 100) if customer_satisfaction else 0, 100),
        'revenue_progress': min((current_revenue / target_revenue * 100) if target_revenue else 0, 100),
        'todays_orders': todays_orders_total,
        'todays_completed': todays_completed,
        'todays_in_progress': todays_in_progress,
        'alerts_count': alerts_count,
        'current_date': date_label,
        'selected_date_range': date_range,
        'custom_date': custom_date,
        'total_confirmed': total_confirmed,
        'total_delivered': total_delivered,
        'total_pending': total_pending,
        'total_preparing': total_preparing,
        'order_revs': order_revs,
        'book_revs': book_revs,
        'revenues': [r1 + r2 for r1, r2 in zip(order_revs, book_revs)],
        'month_names': month_names,
        'orders_pct': orders_pct,
        'bookings_pct': bookings_pct,
        'daily_data': daily_data,
        'daily_labels': daily_labels,
        'weekly_data': weekly_data,
        'weekly_labels': weekly_labels,
        'yearly_data': yearly_data,
        'yearly_labels': yearly_labels,
        'order_revenue_month': order_revenue_current,
        'booking_revenue_month': booking_revenue_current,
        'period': period,
        'user_initials': user_initials,
        'user_full_name': user.full_name or user.email or user.username,
    }
    return render(request, 'adminpanel/admin-dashboard.html', context)


from django.contrib.auth import logout
def custom_logout(request):
    logout(request)
    request.session.flush()  # Clear all session data
    return redirect('/authentication/loginsignup/')  # Adjust path as per your app














# from django.shortcuts import render
# from restaurants.models import RestaurantApprovalRequest
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from restaurants.models import TableBooking
# from restaurants.models import Restaurant
# from restaurants.models import MenuItem, Order, Review
# from django.shortcuts import render
# from django.db.models import Sum, Avg, Count
# from datetime import date, timedelta
# import calendar
# import datetime

# def admin_dashboard_view(request):
#     today = date.today()
#     first_day_month = today.replace(day=1)
#     last_day_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
#     first_day_year = today.replace(month=1, day=1)

#     # Active Menu Items
#     active_menu_items = MenuItem.objects.filter(is_available=True).count()
#     new_menu_items = MenuItem.objects.filter(created_at__range=(first_day_month, last_day_month)).count()
    
#     # Total Orders (Orders + Table Bookings)
#     total_orders = Order.objects.count()
#     total_bookings = TableBooking.objects.count()
#     total_orders_all = total_orders + total_bookings
    
#     # Status counts
#     total_confirmed = Order.objects.filter(status='confirmed').count() + TableBooking.objects.filter(status='confirmed').count()
#     total_delivered = Order.objects.filter(status='delivered').count()
#     total_pending = Order.objects.filter(status='pending').count() + TableBooking.objects.filter(status='pending').count()
#     total_preparing = Order.objects.filter(status='preparing').count()
    
#     # Completed orders (delivered for Order, confirmed for TableBooking)
#     completed_orders_all = total_delivered + TableBooking.objects.filter(status='confirmed').count()
#     pending_orders_all = total_pending + total_preparing + Order.objects.filter(status='confirmed').count()
#     completed_pct = int((completed_orders_all / total_orders_all * 100) if total_orders_all else 0)

#     # Monthly Orders
#     monthly_orders_count = Order.objects.filter(timestamp__range=(first_day_month, last_day_month)).count()
#     monthly_bookings_count = TableBooking.objects.filter(created_at__range=(first_day_month, last_day_month)).count()
#     monthly_orders = monthly_orders_count + monthly_bookings_count
#     target_monthly_orders = 3000

#     # Last 3 months revenues (only delivered orders and confirmed bookings)
#     order_revs = []
#     book_revs = []
#     revenues = []
#     month_names = []
#     current = first_day_month
#     for i in range(3):
#         first = current.replace(day=1)
#         last = first.replace(day=calendar.monthrange(current.year, current.month)[1])
#         ord_rev = Order.objects.filter(
#             timestamp__range=(first, last),
#             status='delivered'
#         ).aggregate(total=Sum('total_price'))['total'] or 0
#         book_rev = TableBooking.objects.filter(
#             created_at__range=(first, last),
#             status='confirmed'
#         ).aggregate(total=Sum('total_amount'))['total'] or 0
#         order_revs.append(float(ord_rev))
#         book_revs.append(float(book_rev))
#         revenues.append(float(ord_rev) + float(book_rev))
#         month_names.append(first.strftime("%B"))
#         current = first - timedelta(days=1)
#     order_revs = order_revs[::-1]
#     book_revs = book_revs[::-1]
#     revenues = revenues[::-1]
#     month_names = month_names[::-1]
#     max_revenue = max(revenues) if revenues else 1.0

#     # Current monthly revenue (latest month)
#     monthly_revenue = revenues[-1]
#     order_revenue_month = order_revs[-1]
#     booking_revenue_month = book_revs[-1]

#     # Pie Chart Data for current month
#     total_revenue = monthly_revenue
#     if total_revenue > 0:
#         orders_pct = (order_revenue_month / total_revenue) * 100
#         bookings_pct = 100 - orders_pct
#     else:
#         orders_pct = 0
#         bookings_pct = 0
#     donut_style = f"conic-gradient(#4169e1 0% {orders_pct}%, #9370db {orders_pct}% 100%)"
#     orders_legend = f"Orders: ₹{order_revenue_month:,.2f} ({orders_pct:.0f}%)"
#     bookings_legend = f"Bookings: ₹{booking_revenue_month:,.2f} ({bookings_pct:.0f}%)"

#     # Net Profit (deduct 20% as costs)
#     deduction_rate = 0.20
#     net_profit = monthly_revenue * (1 - deduction_rate)

#     # Calculate revenue growth (comparing to previous month)
#     if len(revenues) >= 2:
#         prev_monthly_revenue = revenues[-2]
#         if prev_monthly_revenue > 0:
#             revenue_growth = int(((monthly_revenue - prev_monthly_revenue) / prev_monthly_revenue) * 100)
#         else:
#             revenue_growth = 0 if monthly_revenue == 0 else 100
#     else:
#         revenue_growth = 0
    
#     growth_rate = abs(revenue_growth * 0.1)

#     # Customer Satisfaction
#     customer_satisfaction = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

#     # Revenue Target
#     target_revenue = 50000

#     # Today's Stats
#     todays_orders = Order.objects.filter(timestamp__date=today).count()
#     todays_bookings = TableBooking.objects.filter(created_at__date=today).count()
#     todays_orders_total = todays_orders + todays_bookings
    
#     todays_completed_orders = Order.objects.filter(timestamp__date=today, status='delivered').count()
#     todays_completed_bookings = TableBooking.objects.filter(created_at__date=today, status='confirmed').count()
#     todays_completed = todays_completed_orders + todays_completed_bookings
    
#     todays_in_progress_orders = Order.objects.filter(timestamp__date=today, status='preparing').count()
#     todays_in_progress_bookings = TableBooking.objects.filter(created_at__date=today, status='pending').count()
#     todays_in_progress = todays_in_progress_orders + todays_in_progress_bookings

#     # Alerts Count (only if alerts exist)
#     high_priority_reviews = Review.objects.filter(priority='high').count()
#     pending_approvals = RestaurantApprovalRequest.objects.filter(is_resolved=False).count()
#     alerts_count = high_priority_reviews + pending_approvals

#     context = {
#         'active_menu_items': active_menu_items,
#         'new_menu_items': new_menu_items,
#         'total_orders_all': total_orders_all,
#         'completed_orders_all': completed_orders_all,
#         'pending_orders_all': pending_orders_all,
#         'completed_pct': completed_pct,
#         'monthly_revenue': f"₹{monthly_revenue:,.2f}",
#         'revenue_growth': revenue_growth,
#         'net_profit': f"₹{net_profit:,.2f}",
#         'growth_rate': f"{growth_rate:.1f}",
#         'total_revenue': f"₹{monthly_revenue:,.2f}",
#         'monthly_orders_str': f"{monthly_orders} / {target_monthly_orders}",
#         'satisfaction_str': f"{customer_satisfaction:.1f} / 5.0",
#         'revenue_str': f"₹{monthly_revenue:,.2f} / ₹{target_revenue:,.2f}",
#         'monthly_progress': min((monthly_orders / target_monthly_orders * 100) if target_monthly_orders else 0, 100),
#         'satisfaction_progress': min((customer_satisfaction / 5 * 100) if customer_satisfaction else 0, 100),
#         'revenue_progress': min((monthly_revenue / target_revenue * 100) if target_revenue else 0, 100),
#         'todays_orders': todays_orders_total,
#         'todays_completed': todays_completed,
#         'todays_in_progress': todays_in_progress,
#         'alerts_count': alerts_count,
#         'current_date': today.strftime("%B %d, %Y"),
#         'total_confirmed': total_confirmed,
#         'total_delivered': total_delivered,
#         'total_pending': total_pending,
#         'total_preparing': total_preparing,
#         'order_revs': order_revs,
#         'book_revs': book_revs,
#         'revenues': [r1 + r2 for r1, r2 in zip(order_revs, book_revs)],
#         'month_names': month_names,
#         'max_revenue': max_revenue,
#         'donut_style': donut_style,
#         'orders_legend': orders_legend,
#         'bookings_legend': bookings_legend,
#         'orders_pct': orders_pct,
#         'bookings_pct': bookings_pct,
#     }
#     return render(request, 'adminpanel/admin-dashboard.html', context)






# 2nd way

# from django.shortcuts import render
# from restaurants.models import RestaurantApprovalRequest
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from restaurants.models import TableBooking
# from restaurants.models import Restaurant
# from restaurants.models import MenuItem, Order, Review
# from django.shortcuts import render
# from django.db.models import Sum, Avg, Count
# from datetime import date, timedelta
# import calendar

# def admin_dashboard_view(request):
#     today = date.today()
#     first_day_month = today.replace(day=1)
#     last_day_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
#     first_day_year = today.replace(month=1, day=1)

#     # Active Menu Items
#     active_menu_items = MenuItem.objects.filter(is_available=True).count()
#     new_menu_items = MenuItem.objects.filter(created_at__range=(first_day_month, last_day_month)).count()
    
#     # Total Orders (Orders + Table Bookings)
#     total_orders = Order.objects.count()
#     total_bookings = TableBooking.objects.count()
#     total_orders_all = total_orders + total_bookings
    
#     # Completed orders (delivered for Order, confirmed for TableBooking)
#     completed_orders = Order.objects.filter(status='delivered').count()
#     completed_bookings = TableBooking.objects.filter(status='confirmed').count()
#     completed_orders_all = completed_orders + completed_bookings
    
#     # Pending orders
#     pending_orders = Order.objects.filter(status__in=['pending', 'confirmed', 'preparing']).count()
#     pending_bookings = TableBooking.objects.filter(status='pending').count()
#     pending_orders_all = pending_orders + pending_bookings
    
#     completed_pct = int((completed_orders_all / total_orders_all * 100) if total_orders_all else 0)

#     # Monthly Orders
#     monthly_orders_count = Order.objects.filter(timestamp__range=(first_day_month, last_day_month)).count()
#     monthly_bookings_count = TableBooking.objects.filter(created_at__range=(first_day_month, last_day_month)).count()
#     monthly_orders = monthly_orders_count + monthly_bookings_count
#     target_monthly_orders = 3000

#     # Revenue Calculations (Monthly)
#     order_revenue_month = Order.objects.filter(
#         timestamp__range=(first_day_month, last_day_month),
#         payment_status='paid'
#     ).aggregate(total=Sum('total_price'))['total'] or 0
    
#     booking_revenue_month = TableBooking.objects.filter(
#         created_at__range=(first_day_month, last_day_month),
#         status__in=['confirmed', 'pending']
#     ).aggregate(total=Sum('total_amount'))['total'] or 0
    
#     monthly_revenue = float(order_revenue_month) + float(booking_revenue_month)

#     # Net Profit (deduct 20% as costs)
#     deduction_rate = 0.20
#     net_profit = monthly_revenue * (1 - deduction_rate)

#     # Calculate revenue growth (comparing to previous month)
#     prev_month_start = (first_day_month - timedelta(days=1)).replace(day=1)
#     prev_month_end = first_day_month - timedelta(days=1)
    
#     prev_order_revenue = Order.objects.filter(
#         timestamp__range=(prev_month_start, prev_month_end),
#         payment_status='paid'
#     ).aggregate(total=Sum('total_price'))['total'] or 0
    
#     prev_booking_revenue = TableBooking.objects.filter(
#         created_at__range=(prev_month_start, prev_month_end),
#         status__in=['confirmed', 'pending']
#     ).aggregate(total=Sum('total_amount'))['total'] or 0
    
#     prev_monthly_revenue = float(prev_order_revenue) + float(prev_booking_revenue)
    
#     if prev_monthly_revenue > 0:
#         revenue_growth = int(((monthly_revenue - prev_monthly_revenue) / prev_monthly_revenue) * 100)
#     else:
#         revenue_growth = 0 if monthly_revenue == 0 else 100
    
#     growth_rate = abs(revenue_growth * 0.1)

#     # Customer Satisfaction
#     customer_satisfaction = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

#     # Revenue Target
#     target_revenue = 50000

#     # Today's Stats
#     todays_orders = Order.objects.filter(timestamp__date=today).count()
#     todays_bookings = TableBooking.objects.filter(created_at__date=today).count()
#     todays_orders_total = todays_orders + todays_bookings
    
#     todays_completed_orders = Order.objects.filter(timestamp__date=today, status='delivered').count()
#     todays_completed_bookings = TableBooking.objects.filter(created_at__date=today, status='confirmed').count()
#     todays_completed = todays_completed_orders + todays_completed_bookings
    
#     todays_in_progress_orders = Order.objects.filter(timestamp__date=today, status='preparing').count()
#     todays_in_progress_bookings = TableBooking.objects.filter(created_at__date=today, status='pending').count()
#     todays_in_progress = todays_in_progress_orders + todays_in_progress_bookings

#     # Pie Chart Data
#     total_revenue = monthly_revenue
#     if total_revenue > 0:
#         orders_pct = (float(order_revenue_month) / total_revenue) * 100
#         bookings_pct = 100 - orders_pct
#     else:
#         orders_pct = 50
#         bookings_pct = 50
    
#     # Create conic gradient for donut chart
#     donut_style = f"conic-gradient(#4169e1 0% {orders_pct}%, #9370db {orders_pct}% 100%)"
#     orders_legend = f"Orders: ₹{float(order_revenue_month):,.2f} ({orders_pct:.0f}%)"
#     bookings_legend = f"Bookings: ₹{float(booking_revenue_month):,.2f} ({bookings_pct:.0f}%)"

#     # Goal Strings and Progress
#     monthly_orders_str = f"{monthly_orders} / {target_monthly_orders}"
#     satisfaction_str = f"{customer_satisfaction:.1f} / 5.0"
#     revenue_str = f"₹{monthly_revenue:,.2f} / ₹{target_revenue:,.2f}"
#     monthly_progress = min((monthly_orders / target_monthly_orders * 100) if target_monthly_orders else 0, 100)
#     satisfaction_progress = min((customer_satisfaction / 5 * 100) if customer_satisfaction else 0, 100)
#     revenue_progress = min((monthly_revenue / target_revenue * 100) if target_revenue else 0, 100)

#     # Alerts Count (only if alerts exist)
#     high_priority_reviews = Review.objects.filter(priority='high').count()
#     pending_approvals = RestaurantApprovalRequest.objects.filter(is_resolved=False).count()
#     alerts_count = high_priority_reviews + pending_approvals

#     context = {
#         'active_menu_items': active_menu_items,
#         'new_menu_items': new_menu_items,
#         'total_orders_all': total_orders_all,
#         'completed_orders_all': completed_orders_all,
#         'pending_orders_all': pending_orders_all,
#         'completed_pct': completed_pct,
#         'monthly_revenue': f"₹{monthly_revenue:,.2f}",
#         'revenue_growth': revenue_growth,
#         'net_profit': f"₹{net_profit:,.2f}",
#         'growth_rate': f"{growth_rate:.1f}",
#         'donut_style': donut_style,
#         'total_revenue': f"₹{total_revenue:,.2f}",
#         'orders_legend': orders_legend,
#         'bookings_legend': bookings_legend,
#         'orders_pct': f"{orders_pct:.1f}",
#         'bookings_pct': f"{bookings_pct:.1f}",
#         'monthly_orders_str': monthly_orders_str,
#         'satisfaction_str': satisfaction_str,
#         'revenue_str': revenue_str,
#         'monthly_progress': monthly_progress,
#         'satisfaction_progress': satisfaction_progress,
#         'revenue_progress': revenue_progress,
#         'todays_orders': todays_orders_total,
#         'todays_completed': todays_completed,
#         'todays_in_progress': todays_in_progress,
#         'alerts_count': alerts_count,
#         'current_date': today.strftime("%B %d, %Y"),
#     }
#     return render(request, 'adminpanel/admin-dashboard.html', context)


#3rd way

# from django.shortcuts import render
# from restaurants.models import RestaurantApprovalRequest
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from restaurants.models import TableBooking
# from restaurants.models import Restaurant
# from restaurants.models import MenuItem, Order, Review
# from django.shortcuts import render
# from django.db.models import Sum, Avg, Count
# from datetime import date, timedelta
# import calendar

# def admin_dashboard_view(request):
#     today = date.today()
#     first_day_month = today.replace(day=1)
#     last_day_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
#     first_day_year = today.replace(month=1, day=1)

#     # Active Menu Items
#     active_menu_items = MenuItem.objects.filter(is_available=True).count()
#     new_menu_items = MenuItem.objects.filter(created_at__range=(first_day_month, last_day_month)).count()
    
#     # Total Orders (Orders + Table Bookings)
#     total_orders = Order.objects.count()
#     total_bookings = TableBooking.objects.count()
#     total_orders_all = total_orders + total_bookings
    
#     # Completed orders (delivered for Order, confirmed for TableBooking)
#     completed_orders = Order.objects.filter(status='delivered').count()
#     completed_bookings = TableBooking.objects.filter(status='confirmed').count()
#     completed_orders_all = completed_orders + completed_bookings
#     completed_pct = int((completed_orders_all / total_orders_all * 100) if total_orders_all else 0)

#     # Monthly Orders
#     monthly_orders_count = Order.objects.filter(timestamp__range=(first_day_month, last_day_month)).count()
#     monthly_bookings_count = TableBooking.objects.filter(created_at__range=(first_day_month, last_day_month)).count()
#     monthly_orders = monthly_orders_count + monthly_bookings_count
#     target_monthly_orders = 3000

#     # Revenue Calculations (Monthly)
#     # Order uses 'timestamp' field
#     order_revenue_month = Order.objects.filter(
#         timestamp__range=(first_day_month, last_day_month),
#         payment_status='paid'
#     ).aggregate(total=Sum('total_price'))['total'] or 0
    
#     # TableBooking uses 'created_at' field
#     booking_revenue_month = TableBooking.objects.filter(
#         created_at__range=(first_day_month, last_day_month),
#         status__in=['confirmed', 'pending']
#     ).aggregate(total=Sum('total_amount'))['total'] or 0
    
#     monthly_revenue = float(order_revenue_month) + float(booking_revenue_month)

#     # Net Profit (deduct 20% as costs)
#     deduction_rate = 0.20
#     net_profit = monthly_revenue * (1 - deduction_rate)

#     # Calculate revenue growth (comparing to previous month)
#     prev_month_start = (first_day_month - timedelta(days=1)).replace(day=1)
#     prev_month_end = first_day_month - timedelta(days=1)
    
#     # Order uses 'timestamp'
#     prev_order_revenue = Order.objects.filter(
#         timestamp__range=(prev_month_start, prev_month_end),
#         payment_status='paid'
#     ).aggregate(total=Sum('total_price'))['total'] or 0
    
#     # TableBooking uses 'created_at'
#     prev_booking_revenue = TableBooking.objects.filter(
#         created_at__range=(prev_month_start, prev_month_end),
#         status__in=['confirmed', 'pending']
#     ).aggregate(total=Sum('total_amount'))['total'] or 0
    
#     prev_monthly_revenue = float(prev_order_revenue) + float(prev_booking_revenue)
    
#     if prev_monthly_revenue > 0:
#         revenue_growth = int(((monthly_revenue - prev_monthly_revenue) / prev_monthly_revenue) * 100)
#     else:
#         revenue_growth = 0 if monthly_revenue == 0 else 100
    
#     growth_rate = abs(revenue_growth * 0.1)  # Simplified growth rate calculation

#     # Customer Satisfaction
#     customer_satisfaction = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

#     # Revenue Target
#     target_revenue = 50000

#     # Today's Stats
#     # Order uses 'timestamp__date'
#     todays_orders = Order.objects.filter(timestamp__date=today).count()
#     # TableBooking uses 'created_at__date'
#     todays_bookings = TableBooking.objects.filter(created_at__date=today).count()
#     todays_orders_total = todays_orders + todays_bookings
    
#     todays_completed_orders = Order.objects.filter(timestamp__date=today, status='delivered').count()
#     todays_completed_bookings = TableBooking.objects.filter(created_at__date=today, status='confirmed').count()
#     todays_completed = todays_completed_orders + todays_completed_bookings
    
#     todays_in_progress_orders = Order.objects.filter(timestamp__date=today, status='preparing').count()
#     todays_in_progress_bookings = TableBooking.objects.filter(created_at__date=today, status='pending').count()
#     todays_in_progress = todays_in_progress_orders + todays_in_progress_bookings

#     # Pie Chart Data
#     total_revenue = monthly_revenue
#     if total_revenue > 0:
#         orders_pct = (float(order_revenue_month) / total_revenue) * 100
#         bookings_pct = 100 - orders_pct
#     else:
#         orders_pct = 0
#         bookings_pct = 0
    
#     donut_style = f"conic-gradient(#4169e1 0% {orders_pct}%, #9370db {orders_pct}% 100%)"
#     orders_legend = f"Orders: ${float(order_revenue_month):,.2f} ({orders_pct:.0f}%)"
#     bookings_legend = f"Bookings: ${float(booking_revenue_month):,.2f} ({bookings_pct:.0f}%)"

#     # Goal Strings and Progress
#     monthly_orders_str = f"{monthly_orders} / {target_monthly_orders}"
#     satisfaction_str = f"{customer_satisfaction:.1f} / 5.0"
#     revenue_str = f"${monthly_revenue:,.2f} / ${target_revenue:,.2f}"
#     monthly_progress = min((monthly_orders / target_monthly_orders * 100) if target_monthly_orders else 0, 100)
#     satisfaction_progress = min((customer_satisfaction / 5 * 100) if customer_satisfaction else 0, 100)
#     revenue_progress = min((monthly_revenue / target_revenue * 100) if target_revenue else 0, 100)

#     # Alerts Count (high priority reviews + pending approval requests)
#     high_priority_reviews = Review.objects.filter(priority='high').count()
#     pending_approvals = RestaurantApprovalRequest.objects.filter(is_resolved=False).count()
#     alerts_count = high_priority_reviews + pending_approvals

#     context = {
#         'active_menu_items': active_menu_items,
#         'new_menu_items': new_menu_items,
#         'total_orders_all': total_orders_all,
#         'completed_pct': completed_pct,
#         'monthly_revenue': f"${monthly_revenue:,.2f}",
#         'revenue_growth': revenue_growth,
#         'net_profit': f"${net_profit:,.2f}",
#         'growth_rate': f"{growth_rate:.1f}",
#         'donut_style': donut_style,
#         'total_revenue': f"${total_revenue:,.2f}",
#         'orders_legend': orders_legend,
#         'bookings_legend': bookings_legend,
#         'monthly_orders_str': monthly_orders_str,
#         'satisfaction_str': satisfaction_str,
#         'revenue_str': revenue_str,
#         'monthly_progress': monthly_progress,
#         'satisfaction_progress': satisfaction_progress,
#         'revenue_progress': revenue_progress,
#         'todays_orders': todays_orders_total,
#         'todays_completed': todays_completed,
#         'todays_in_progress': todays_in_progress,
#         'alerts_count': alerts_count,
#         'current_date': today.strftime("%B %d, %Y"),
#     }
#     return render(request, 'adminpanel/admin-dashboard.html', context)




# @login_required
# def admin_alert_view(request):
#     # Get only unresolved approval requests
#     # approval_requests = RestaurantApprovalRequest.objects.filter(is_resolved=False).select_related("restaurant", "restaurant__owner").order_by("-created_at")
#     # return render(request, "adminpanel/admin-alerts.html", {"approval_requests": approval_requests})
    
#     # Pending approvals
#     pending_requests = (
#         RestaurantApprovalRequest.objects
#         .filter(is_resolved=False, is_approved=False, is_rejected=False)
#         .select_related("restaurant", "restaurant__owner")
#         .order_by("-created_at")
#     )

#     # Approved restaurants
#     approved_requests = (
#         RestaurantApprovalRequest.objects
#         .filter(is_approved=True)
#         .select_related("restaurant", "restaurant__owner")
#         .order_by("-created_at")
#     )

#     # Rejected restaurants
#     rejected_requests = (
#         RestaurantApprovalRequest.objects
#         .filter(is_rejected=True)
#         .select_related("restaurant", "restaurant__owner")
#         .order_by("-created_at")
#     )

#     return render(request, "adminpanel/admin-alerts.html", {
#         "pending_requests": pending_requests,
#         "approved_requests": approved_requests,
#         "rejected_requests": rejected_requests,
#     })

@login_required
def admin_alert_view(request):
    # Pending approvals
    pending_requests = (
        RestaurantApprovalRequest.objects
        .filter(is_resolved=False, is_approved=False, is_rejected=False)
        .select_related("restaurant", "restaurant__owner")
        .order_by("-created_at")
    )

    # Approved restaurants
    approved_requests = (
        RestaurantApprovalRequest.objects
        .filter(is_approved=True)
        .select_related("restaurant", "restaurant__owner")
        .order_by("-created_at")
    )

    # Rejected restaurants
    rejected_requests = (
        RestaurantApprovalRequest.objects
        .filter(is_rejected=True)
        .select_related("restaurant", "restaurant__owner")
        .order_by("-created_at")
    )

    return render(request, "adminpanel/admin-alerts.html", {
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
    })

from django.core.paginator import Paginator
from restaurants.models import Order, OrderItem

def admin_orders_view(request):
    orders = (
        Order.objects
        .select_related('user', 'restaurant')
        .prefetch_related('order_items')
        .order_by('-timestamp')
    )
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'adminpanel/admin-orders.html', {
        'orders': page_obj
    })


from django.db.models import Prefetch
from restaurants.models import RestaurantOwnerProfile, RestaurantApprovalRequest

def admin_restaurants_view(request):
    # Prefetch RestaurantOwnerProfile through the owner (User) relationship
    owner_profile_prefetch = Prefetch(
        'owner__owner_profiles',  # Navigate from Restaurant.owner to User.owner_profiles
        queryset=RestaurantOwnerProfile.objects.all(),
        to_attr='profile_list'    # Store as a list in case multiple profiles exist (though OneToOne should limit to one)
    )

    # Fetch approved restaurants
    restaurants = (
        Restaurant.objects
        .select_related('owner')                  # Join with User
        .prefetch_related(owner_profile_prefetch) # Prefetch owner profiles
        .filter(is_approved=True)                # Only approved restaurants
        .order_by('-created_at')
    )

    # Fetch restaurant approval requests
    booking_profile_prefetch = Prefetch(
        'restaurant__owner_profile',
        queryset=RestaurantOwnerProfile.objects.all(),
        to_attr='profile_obj'
    )

    restaurants_booking = (
        RestaurantApprovalRequest.objects
        .select_related('restaurant', 'restaurant__owner')
        .prefetch_related(booking_profile_prefetch)
        .order_by('-created_at')
    )

    return render(request, 'adminpanel/admin-restaurants.html', {
        'restaurants': restaurants,
        'restaurant_booking': restaurants_booking
    })
    


def admin_table_booking_view(request):
    table_bookings = TableBooking.objects.all().order_by('-created_at')  # latest first
    return render(request, 'adminpanel/admin-table_booking.html', {
        'table_bookings': table_bookings
    })

from users.models import User

def admin_users_view(request):
    # Fetch all users with relevant fields
    users = User.objects.all().order_by('-created_at')  # Order by creation date (newest first)

    return render(request, 'adminpanel/admin-users.html', {
        'users': users
    })


@login_required
def approve_restaurant(request, pk):
    request_obj = get_object_or_404(RestaurantApprovalRequest, pk=pk)
    request_obj.is_approved = True
    request_obj.is_rejected = False  # Optional: clear reject flag
    request_obj.restaurant.is_approved = True
    request_obj.restaurant.save()
    request_obj.save()
    messages.success(request, "Restaurant approved ✅")
    return redirect('adminpanel:admin_alerts')


@login_required
def reject_restaurant(request, pk):
    request_obj = get_object_or_404(RestaurantApprovalRequest, pk=pk)
    request_obj.is_rejected = True
    request_obj.is_approved = False  # Optional: clear approve flag
    request_obj.restaurant.is_approved = False  # Explicitly mark it unapproved
    request_obj.restaurant.save()
    request_obj.save()
    messages.error(request, "Restaurant rejected ❌")
    return redirect('adminpanel:admin_alerts')

