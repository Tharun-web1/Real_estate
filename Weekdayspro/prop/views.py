from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate

import prop
import json
from django.contrib.auth import login, authenticate
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import  get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm
from .models import User


def register_user(request):
    # Only redirect if they have completed registration (indicated by having a phone number)
    if request.user.is_authenticated and request.user.phone:
        return redirect("prop:home")
    
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)

        if form.is_valid():
            # Create user but don't save yet
            user = form.save(commit=False)

            # Get role safely
            role = form.cleaned_data.get("role")

            # ==========================
            # COMMON FIELDS
            # ==========================
            user.description = request.POST.get("description")
            user.experience = request.POST.get("experience")
            user.deals = request.POST.get("deals")
            user.location = request.POST.get("location")

            # ==========================
            # ROLE BASED LOGIC
            # ==========================

            if role == "PROFESSIONAL":
                user.category = form.cleaned_data.get("category")
                user.plan_type = "PROFESSIONAL_SINGLE"

            elif role == "OWNER":
                user.category = form.cleaned_data.get("category")

            elif role == "MARKETER":
                marketer_categories = form.cleaned_data.get("marketer_category")

                if marketer_categories:
                    user.marketer_category = ",".join(marketer_categories)

                selected_plan = form.cleaned_data.get("plan_type")
                user.plan_type = selected_plan

                #  Activate subscription only if plan selected
                if selected_plan:
                    user.marketing_subscription_type = selected_plan.replace("MARKETER_", "")

                    user.marketer_subscription_start_date = date.today()
                    user.marketer_subscription_end_date = date.today() + timedelta(days=30)

            # Save user
            user.save()

            # Login user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, "Account created successfully!")
            return redirect("prop:profile")

        else:
            print(form.errors)

    else:
        form = UserRegisterForm()

    return render(request, "register.html", {"form": form})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password

@csrf_exempt
def register_step1_ajax(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            data = request.POST

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        location = data.get("location")
        referred_by_code = data.get("referred_by_code")

        if not username or not email or not password:
            return JsonResponse({"success": False, "message": "Required fields missing"}, status=400)

        if User.objects.filter(username=username).exists():
            # If user exists but is not logged in, we should check if they can just log in
            # but for security we just tell them it exists. 
            # However, if it's the CURRENT session's user, it might be a retry.
            return JsonResponse({"success": False, "message": "Username already exists. Please login."}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already exists. Please login."}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            location=location,
            referred_by_code=referred_by_code
        )
        
        # Log in the user immediately
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return JsonResponse({"success": True, "message": "Signup successfully!"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

@login_required
@csrf_exempt
def register_step2_ajax(request):
    if request.method == "POST":
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except:
                data = request.POST
        else:
            data = request.POST

        user = request.user
        user.role = data.get("role")
        user.description = data.get("description")
        user.company_name = data.get("company_name")
        
        # Handle experience (IntegerField)
        exp = data.get("experience")
        user.experience = int(exp) if exp and str(exp).isdigit() else None
        
        user.deals = data.get("deals")
        user.area_serves = data.get("area_serves")
        user.whatsapp_number = data.get("whatsapp_number")
        user.category = data.get("category")

        # Handle Files
        if 'profile_image_path' in request.FILES:
            user.profile_image_path = request.FILES['profile_image_path']
        if 'company_logo_path' in request.FILES:
            user.company_logo_path = request.FILES['company_logo_path']
        
        m_cat = data.get("marketer_category")
        if m_cat:
            try:
                # If it's a JSON string from JS
                parsed_cat = json.loads(m_cat)
                if isinstance(parsed_cat, list):
                    user.marketer_category = ",".join(parsed_cat)
                else:
                    user.marketer_category = str(parsed_cat)
            except:
                user.marketer_category = m_cat
            
        if user.role == "MARKETER":
            plan = data.get("plan_type")
            if plan:
                user.plan_type = plan
            
        try:
            user.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

@login_required
@csrf_exempt
def register_subscribe(request):
    if request.method == "POST":
        plan_type = None
        if request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
                plan_type = data.get("plan_type")
            except:
                pass
        else:
            plan_type = request.POST.get("plan_type")

        if plan_type:
            user = request.user
            user.plan_type = plan_type
            user.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({"success": True})
            
            return redirect("prop:home")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({"success": False, "message": "Invalid request"})
        
    return redirect("prop:home")

def register_choice(request):
    return render(request, 'register_choice.html')    
 

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Get user by username/email
            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                user_obj = None

            # 🔥 BLOCK normal login if Google-only user
            if user_obj and not user_obj.has_usable_password():
                messages.error(request, "Please login using Google.")
                return redirect("account_login")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}.")
                return redirect("prop:home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request, "login.html", {"login_form": form})



@login_required
def leads_page(req):
    user = req.user
    
    lead_user = ProfileLeadsModel.objects.filter(leadTo=user)

    luser_list = []
    for item in lead_user:
        luser_list.append({
            "username": item.leadFrom.username,
            "phone": item.leadFrom.phone,
        })

    return render(req, "leads_page.html", {
        "luser_list": luser_list
    })
    
@login_required
def property_leads_page(request, id):
    u = request.user

    try:
        pro = AddPropertyModel.objects.get(id=id)
    except AddPropertyModel.DoesNotExist:
        return HttpResponse("Property not found")

    leads_qs = PropertyLeadsModel.objects.filter(property=pro).order_by('-created_at')

    unique_users = {}

    for l in leads_qs:
        if l.leadFrom:
            unique_users[l.leadFrom.id] = {
                "id": l.leadFrom.id,
                "username": l.leadFrom.username,
                "phone": getattr(l.leadFrom, "phone", "") or getattr(l.leadFrom, "contact_number", ""),
                "created_at": l.created_at,
            }

    # final list (no duplicates)
    luser_list = list(unique_users.values())

    return render(request, "property_leads_page.html", {
        "property": pro,
        "luser_list": luser_list,
        "user": u
    })
from .models import User, ProfileLeadsModel

@login_required
def company_leads_page(request, user_id):
    # Company profile user
    profile_user = get_object_or_404(User, id=user_id)

    # Owner check
    is_owner = request.user.id == profile_user.id

    # Order by latest first
    leads_qs = ProfileLeadsModel.objects.filter(
        leadTo=profile_user
    ).select_related("leadFrom").order_by('-created_at')

    # Remove duplicates (keep latest)
    unique_users = {}

    for lead in leads_qs:
        if lead.leadFrom and lead.leadFrom.id not in unique_users:
            unique_users[lead.leadFrom.id] = lead

    # Final list
    lead_list = list(unique_users.values())

    context = {
        "profile_user": profile_user,
        "lead_list": lead_list,
        "is_owner": is_owner,
    }

    return render(request, "company_leads_page.html", context)
#=================
# property adding
#=================




from django.contrib import messages
import time

@login_required
def add_property(request):
    if request.user.role in ["PROFESSIONAL", "FRANCHISE", "REGISTER", "COMPANY"]:
        messages.error(request, "You are not authorized to post properties.")
        return redirect('prop:home')
    
    if request.method == "POST":
        # Debug: see what nearby_locations value is coming in
        print("NEARBY RAW:", request.POST.get("nearby_locations"))

        form = AddPropertyForm(request.POST, request.FILES)

        if form.is_valid():
            start = time.time()

            form.save(user=request.user)

            print("TIME:", time.time() - start)

            messages.success(request, "🎉 Property posted successfully!")
            return redirect('prop:home')

        else:
            print(form.errors.as_json())

    else:
        form = AddPropertyForm()

    return render(request, 'add_property.html', {'form': form})
from django.contrib.auth import get_user_model

from django.shortcuts import render
from .models import AddProject, User, Role, PlanType

from datetime import date

User = get_user_model()

def home(request):
    today = date.today()
    
    desktop_slides = SlideImage.objects.filter(
        slide_type="desktop"
    ).order_by("-created_at")[:3]

    mobile_slides = SlideImage.objects.filter(
        slide_type="mobile"
    ).order_by("-created_at")[:3] 
    marketing_experts = User.objects.filter(
        role=Role.MARKETER,
        plan_type=PlanType.MARKETER_EXPORT,
    ).order_by('-id')

    marketing_experts_pro = User.objects.filter(
        role=Role.MARKETER,
        plan_type=PlanType.MARKETER_EXPORT_PRO,
    ).order_by('-id')

    marketing_experts_premium = User.objects.filter(
        role=Role.MARKETER,
        plan_type=PlanType.MARKETER_EXPORT_PREMIUM,
    ).order_by('-id')

    # Fallback: if experts are empty, show any marketers
    if not marketing_experts.exists() and not marketing_experts_pro.exists() and not marketing_experts_premium.exists():
        marketing_experts = User.objects.filter(role=Role.MARKETER).order_by('-id')
# ============================
# COMPANIES
# ============================

    featured_companies = User.objects.filter(
        role=Role.COMPANY,
    ).exclude(
        plan_type__in=[PlanType.COMPANY_PRO, PlanType.COMPANY_PREMIUM]
    ).order_by('-id')

    featured_companies_pro = User.objects.filter(
        role=Role.COMPANY,
        plan_type=PlanType.COMPANY_PRO
    ).order_by('-id')

    featured_companies_premium = User.objects.filter(
        role=Role.COMPANY,
        plan_type=PlanType.COMPANY_PREMIUM
    ).order_by('-id')

    # ============================
    # PROFESSIONALS
    # ============================
    professionals = User.objects.filter(
        role=Role.PROFESSIONAL
    ).order_by('-id')

    # ============================
    # OWNERS
    # ============================
    owners = User.objects.filter(
        role=Role.OWNER
    ).order_by('-id')

    # ============================
    # REELS
    # ============================
    reels = Reels.objects.exclude(reel='').exclude(reel__isnull=True).order_by('-id')[:10]

    # Exclude current user from all user lists if logged in
    if request.user.is_authenticated:
        marketing_experts = marketing_experts.exclude(id=request.user.id)
        marketing_experts_pro = marketing_experts_pro.exclude(id=request.user.id)
        marketing_experts_premium = marketing_experts_premium.exclude(id=request.user.id)
        featured_companies = featured_companies.exclude(id=request.user.id)
        featured_companies_pro = featured_companies_pro.exclude(id=request.user.id)
        featured_companies_premium = featured_companies_premium.exclude(id=request.user.id)
        professionals = professionals.exclude(id=request.user.id)
        owners = owners.exclude(id=request.user.id)

    # Limit results after exclusion
    marketing_experts = marketing_experts[:40]
    marketing_experts_pro = marketing_experts_pro[:40]
    marketing_experts_premium = marketing_experts_premium[:40]
    featured_companies = featured_companies[:40]
    featured_companies_pro = featured_companies_pro[:40]
    featured_companies_premium = featured_companies_premium[:40]
    professionals = professionals[:40]
    owners = owners[:40]

    # ============================
    # ============================
    # PROJECTS (ORDERED BY PLAN)
    # ============================
    premium_projects = AddProject.objects.filter(plan_type=PlanType.COMPANY_PREMIUM).order_by('-id')[:40]
    pro_projects = AddProject.objects.filter(plan_type=PlanType.COMPANY_PRO).order_by('-id')[:40]
    normal_projects = AddProject.objects.filter(plan_type=PlanType.COMPANY_NORMAL).order_by('-id')[:40]

    # Fallback for Featured Projects section
    if not pro_projects.exists():
        pro_projects = AddProject.objects.exclude(plan_type=PlanType.COMPANY_PREMIUM).order_by('-id')[:40]
    
    # Fallback for Premium Projects section
    if not premium_projects.exists():
        premium_projects = AddProject.objects.all().order_by('-id')[:40]

    all_properties = AddPropertyModel.objects.exclude(user__role='OWNER', is_verified=False).order_by('-id')[:40]
    feed_posts = NewsPost.objects.all().order_by('-created_at')[:40]
    reels = Reels.objects.exclude(reel='').exclude(reel__isnull=True).order_by('-id')[:40]

    # ============================
    # MIXED FEATURED DATA (PROPERTIES + FEED)
    # ============================
    mixed_featured_data = []
    prop_list = list(all_properties)
    feed_list = list(feed_posts)
    
    # Interleave 1 property and 1 feed item at a time (strictly alternating)
    for p, f in zip(prop_list, feed_list):
        mixed_featured_data.append({'wrap_type': 'property', 'item': p})
        mixed_featured_data.append({'wrap_type': 'feed', 'item': f})
    
    # If one list is longer, add the remaining items (optional, but keeps consistency)
    remaining_props = prop_list[len(feed_list):]
    remaining_feeds = feed_list[len(prop_list):]
    mixed_featured_data.extend([{'wrap_type': 'property', 'item': p} for p in remaining_props])
    mixed_featured_data.extend([{'wrap_type': 'feed', 'item': f} for f in remaining_feeds])
    
    fp_batches = [mixed_featured_data[k:k+10] for k in range(0, 80, 10)]

    other_sections = [
        ('premium_projects', list(premium_projects)),
        ('premium_builders', list(featured_companies_premium)),
        ('premium_agents', list(marketing_experts_premium)),
        ('professionals', list(professionals)),
        ('prop_bytes', list(reels)),
        ('featured_projects', list(pro_projects)),
        ('featured_builders', list(featured_companies_pro)),
        ('featured_agents', list(marketing_experts_pro)),
        ('recommended_agents', list(marketing_experts)),
        ('recommended_builders', list(featured_companies)),
        ('recommended_projects', list(normal_projects)),
    ]

    # ============================
    # LOOPING LOGIC
    # ============================
    homepage_loops = []
    fp_index = 0
    
    # Create up to 4 loops
    for i in range(0, 40, 10):
        current_loop = []
        for k, (s_type, s_data) in enumerate(other_sections):
            batch = s_data[i:i+10]
            if batch:
                current_loop.append({'type': s_type, 'data': batch})
            
            # After every 2 sections, insert a mixed featured section
            if (k + 1) % 2 == 0 and fp_index < len(fp_batches):
                current_loop.append({'type': 'featured_properties', 'data': fp_batches[fp_index]})
                fp_index += 1
        
        if current_loop:
            homepage_loops.append(current_loop)

    # ============================
    # STORIES (ImagePost last 24h)
    # ============================
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    
    # 1. Automatic Cleanup: Delete posts older than 24h from DB (Run once per hour)
    if not cache.get('stories_cleaned'):
        ImagePost.objects.filter(created_at__lt=twenty_four_hours_ago).delete()
        cache.set('stories_cleaned', True, 3600) # Expire in 1 hour
    
    # 2. Optimized Fetch: Only active posts
    active_news = ImagePost.objects.filter(
        created_at__gte=twenty_four_hours_ago
    ).select_related('user').only(
        'id', 'image', 'heading', 'news_content', 'created_at',
        'user__username', 'user__company_name', 'user__company_logo_path', 'user__profile_image_path'
    ).order_by('-created_at') # Most recent users first
    
    # Group news posts by user
    stories_data = {}
    for post in active_news:
        if post.user:
            user_id = post.user.id
            if user_id not in stories_data:
                if len(stories_data) >= 20: break 
                stories_data[user_id] = {
                    'user': {
                        'id': post.user.id,
                        'username': post.user.username,
                        'company_name': post.user.company_name,
                        'company_logo_path': post.user.company_logo_path.url if post.user.company_logo_path else None,
                        'profile_image_path': post.user.profile_image_path.url if post.user.profile_image_path else None,
                    },
                    'posts': []
                }
            # Add to posts list
            stories_data[user_id]['posts'].append({
                'id': post.id,
                'user_id': post.user.id,
                'media_type': post.media_type,
                'image_url': post.image.url if post.image else None,
                'video_url': post.video.url if post.video else None,
                'content': post.news_content,
                'created_at': post.created_at.strftime("%H:%M")
            })

    # Reverse the posts for each user so they play Oldest -> Newest
    for user_id in stories_data:
        stories_data[user_id]['posts'].reverse()
    
    # 3. Seen/Unseen Logic (Sort stories_data)
    if request.user.is_authenticated:
        seen_post_ids = set(StorySeen.objects.filter(user=request.user).values_list('post_id', flat=True))
        
        # Determine if each user's story group is "all seen"
        for user_id, group in stories_data.items():
            all_seen = True
            for post in group['posts']:
                if post['id'] not in seen_post_ids:
                    all_seen = False
                    break
            group['all_seen'] = all_seen
            
        # Sort: Unseen first, then Seen. Within each group, it's already sorted by recency of the latest post.
        sorted_stories = sorted(
            stories_data.values(),
            key=lambda x: (x.get('all_seen', False))
        )
        stories_list = sorted_stories
    else:
        stories_list = list(stories_data.values())

    # Separate current user's stories for special "Your Story" handling
    user_stories = stories_data.pop(request.user.id, None) if request.user.is_authenticated else None
    
    import json
    stories_json = json.dumps(stories_list)
    user_stories_json = json.dumps(user_stories) if user_stories else "null"

    return render(request, "home.html", {
        "desktop_slides": desktop_slides,
        "mobile_slides": mobile_slides, 
        "stories_list": list(stories_data.values()),
        "stories_json": stories_json,
        "user_stories": user_stories,
        "user_stories_json": user_stories_json,
        "current_user_id": request.user.id if request.user.is_authenticated else None,
        "homepage_loops": homepage_loops,
    })






def all_projects(request):
    category = request.GET.get("category")
    name = request.GET.get("name", "")
    location = request.GET.get("location", "")
    type_of_project = request.GET.get("type_of_project", "")
    facing = request.GET.get("facing", "")
    min_price = request.GET.get("minpricing")
    max_price = request.GET.get("maxpricing")
    cname = request.GET.get("cname")
    position = request.GET.get("position")
    city = request.GET.get("city")
    extent = request.GET.get("extent")
    approval = request.GET.get("approval")

    qs = AddProject.objects.all()

    if name:
        qs = qs.filter(project_name__icontains=name)
    if position:
        qs = qs.filter(position=position)
    if cname:
        qs = qs.filter(user_id=cname)
    if location:
        qs = qs.filter(Q(project_address__icontains=location) | Q(project_name__icontains=location))
    if city:
        qs = qs.filter(project_address__icontains=city)
    if type_of_project:
        qs = qs.filter(type_of_project__icontains=type_of_project)
    if facing:
        qs = qs.filter(available_facing__icontains=facing)
    if extent:
        qs = qs.filter(total_project_area__icontains=extent)
    if approval:
        qs = qs.filter(type_of_approval__icontains=approval)
    if min_price:
        qs = qs.filter(pricing__gte=min_price)
    if max_price:
        qs = qs.filter(pricing__lte=max_price)

    if category == "premium":
        qs = qs.filter(plan_type=PlanType.COMPANY_PREMIUM)
    elif category == "pro":
        qs = qs.filter(plan_type=PlanType.COMPANY_PRO)
    elif category == "normal":
        qs = qs.filter(plan_type=PlanType.COMPANY_NORMAL)
        
    qs = qs.order_by('-id')
    
    return render(request, "all_projects.html", {
        "projects": qs,
        "category": category,
        "name": name,
        "location": location,
        "type_of_project": type_of_project,
        "facing": facing,
        "min_price": min_price,
        "max_price": max_price,
        "cname": cname,
        "position": position,
    })

 
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Increase profile views only for visitors
    if request.user != user:
        user.click = (user.click or 0) + 1
        user.save()

    reels = Reels.objects.filter(user=user).exclude(reel='').exclude(reel__isnull=True)
    qs = AddPropertyModel.objects.filter(user=user)
    projects = []
    if user.role == 'COMPANY':
        from .models import AddProject
        projects = AddProject.objects.filter(user=user)
    
    from .models import Poll, NewsPost
    polls = Poll.objects.filter(user=user).order_by('-created_at')
    feed_posts = NewsPost.objects.filter(user=user).order_by('-created_at')

    # Filter owner properties to only show verified ones to visitors
    if user.role == 'OWNER' and request.user != user:
        qs = qs.filter(is_verified=True)

    total_count = qs.count()
    sold_count = qs.filter(is_notSold=True).count()
    pending_count = qs.filter(is_notSold=False).count()

    return render(request, "user_detail.html", {
        "u": user,
        "sold": sold_count,
        "pending": pending_count,
        "total": total_count,
        "reels": reels,
        "properties": qs,
        "projects": projects,
        "polls": polls,
        "feed_posts": feed_posts,
    })

from django.utils import timezone
from django.db.models import Q



from django.shortcuts import render
from django.utils import timezone
from django.core.files.storage import default_storage
from .models import User, Role, PlanType
def all_users(request):
    today = timezone.now().date()
    category = request.GET.get("category", "company")  # default tab

    # ===== CATEGORY CHOICES =====
    PROFESSIONAL_CATEGORY_CHOICES = [
        ('Plumber', 'Plumber'),
        ('Painter', 'Painter'),
        ('Electrician', 'Electrician'),
        ('Constructor', 'Constructor'),
        ('Centring', 'Centring'),
        ('Interior designer', 'Interior designer'),
        ('Architecture', 'Architecture'),
        ('Civil engineer', 'Civil engineer'),
        ('Tiles works', 'Tiles works'),
        ('Marble works', 'Marble works'),
        ('Grinate works', 'Grinate works'),
        ('Wood works', 'Wood works'),
        ('Glass works', 'Glass works'),
        ('Steel railing works', 'Steel railing works'),
        ('Carpenter', 'Carpenter'),
        ('Doozer works', 'Doozer works'),
        ('JCB works', 'JCB works'),
        ('Borewells', 'Borewells'),
        ('Material supplier', 'Material supplier'),
    ]

    COMPANY_CATEGORY_CHOICES = [
       ('Open Flat', 'Open Flat'),
    ('Villa', 'Villa'),
    ('Appartment', 'Appartment'),
    ('Farm Flats', 'Farm Flats'),
     ('Commercial Lands', 'Commercial Lands'),
    ]

    MARKETER_CATEGORY_CHOICES = [
       ('Plot', 'Plot'),
        ('House', 'House'),
        ('Flat', 'Flat'),
        ('Villa', 'Villa'),
        ('Farm', 'Farm'),
        ('Lands', 'Lands'),
        ('Developmentlands', 'Developmentlands')
       
    ]

    # ===== INITIAL QUERYSETS =====
    marketer_export = marketer_export_pro = marketer_export_premium = company_normal = company_pro = company_premium = professional_users = None

    # ===== MARKETER USERS =====
    if category in ["marketer", "marketer_pro", "marketer_premium"]:
        marketer_export_premium = User.objects.filter(
            role=Role.MARKETER,
            plan_type=PlanType.MARKETER_EXPORT_PREMIUM,
        )
        marketer_export_pro = User.objects.filter(
            role=Role.MARKETER,
            plan_type=PlanType.MARKETER_EXPORT_PRO,
        )
        marketer_export = User.objects.filter(
            role=Role.MARKETER
        ).exclude(
            plan_type__in=[PlanType.MARKETER_EXPORT_PRO, PlanType.MARKETER_EXPORT_PREMIUM]
        )

    # ===== COMPANY USERS ===== 
    elif category in ["company", "company_pro", "company_premium"]:


        company_premium = User.objects.filter(
            role=Role.COMPANY,
            plan_type=PlanType.COMPANY_PREMIUM,
        )

        company_pro = User.objects.filter(
            role=Role.COMPANY,
            plan_type=PlanType.COMPANY_PRO,
        )

        company_normal = User.objects.filter(
            role=Role.COMPANY
        ).exclude(
            plan_type__in=[PlanType.COMPANY_PRO, PlanType.COMPANY_PREMIUM]
        )

    # ===== PROFESSIONAL USERS =====
    elif category == "professional":
        professional_users = User.objects.filter(
            role=Role.PROFESSIONAL,
        )

    # ===== FILTERS =====
    name = request.GET.get("name", "")
    user_category = request.GET.get("user_category", "")
    experience = request.GET.get("experience", "")
    location = request.GET.get("location", "")
    city = request.GET.get("city", "")
    plan_type = request.GET.get("plan_type", "")

    # ❤️ CATEGORY FIELD FIX (IMPORTANT)
    def apply_filters(queryset):
        if queryset is None:
            return None

        if name:
            queryset = queryset.filter(Q(username__icontains=name) | Q(company_name__icontains=name))

        if user_category:
            if category.startswith("company"):
                queryset = queryset.filter(category__icontains=user_category)
            elif category.startswith("marketer"):
                queryset = queryset.filter(marketer_category__icontains=user_category)
            elif category == "professional":
                queryset = queryset.filter(category__icontains=user_category)

        if experience:
            queryset = queryset.filter(experience__gte=experience)

        if location:
            queryset = queryset.filter(location__icontains=location)
            
        if city:
            queryset = queryset.filter(location__icontains=city)
            
        if plan_type:
            queryset = queryset.filter(plan_type=plan_type)
        if request.user.is_authenticated:
            queryset = queryset.exclude(id=request.user.id)

        return queryset.order_by('-id')

    marketer_export = apply_filters(marketer_export)
    marketer_export_pro = apply_filters(marketer_export_pro)
    marketer_export_premium = apply_filters(marketer_export_premium)
    company_normal = apply_filters(company_normal)
    company_pro = apply_filters(company_pro)
    company_premium = apply_filters(company_premium)
    professional_users = apply_filters(professional_users)

    # ===== RENDER =====
    return render(request, "all_users.html", {
        "category": category,

        "PROFESSIONAL_CATEGORY_CHOICES": PROFESSIONAL_CATEGORY_CHOICES,
        "COMPANY_CATEGORY_CHOICES": COMPANY_CATEGORY_CHOICES,
        "MARKETER_CATEGORY_CHOICES": MARKETER_CATEGORY_CHOICES,

        "filters": {
            "name": name,
            "user_category": user_category,
            "experience": experience,
            "location": location,
        },

        "marketer_export": marketer_export,
        "marketer_export_pro": marketer_export_pro,
        "marketer_export_premium": marketer_export_premium,
        "company_normal": company_normal,
        "company_pro": company_pro,
        "company_premium": company_premium,
        "professional_users": professional_users,
    })
# franchise in home

from .forms import FranchiseApplicationForm
def franchise(request):
    if request.method == "POST":
        form = FranchiseApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Form submitted successfully!")
            return render(request, "franchise.html", {"form": FranchiseApplicationForm(), "success": True})
    else:
        form = FranchiseApplicationForm()
        fran=User.objects.filter(role='FRANCHISE')

    return render(request, "franchise.html", {"form": form,  "data": fran, })


# my requrement form
def requirement_form(request):
    if request.method == 'POST':
        form = FutureRequirementForm(request.POST)
        if form.is_valid():
            form.save()
            if request.user.is_authenticated:
                PropertyInteraction.objects.create(
                    user=request.user,
                    interaction_type='enquiry'
                )
            messages.success(request, 'Your requirement has been submitted successfully!')
            return redirect('prop:require')  # URL name defined in urls.py
        else:
            print("Form errors:", form.errors)  # Debugging help in terminal
    else:
        form = FutureRequirementForm()
    return render(request, 'require.html', {'form': form})


from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required
def marketing_renew_plans(request):
    user = request.user

    if request.method == "POST":

        role = request.POST.get("role")

        if not role:
            messages.error(request, "Invalid role.")
            return redirect("prop:marketing_renew_plan")

        user.role = role

        # ---------------- GET PLAN & DURATION ----------------
        if role == "MARKETER":
            plan_type = request.POST.get("plan_type")
            duration = request.POST.get("duration")

        elif role == "PROFESSIONAL":
            plan_type = request.POST.get("professional_plan_type")
            duration = request.POST.get("professional_duration")

        elif role == "OWNER":
            plan_type = request.POST.get("owner_plan_type")
            duration = request.POST.get("owner_duration")

        else:
            messages.error(request, "Invalid role selected.")
            return redirect("prop:marketing_renew_plan")

        if not plan_type or not duration:
            messages.error(request, "Please select a plan and duration.")
            return redirect("prop:marketing_renew_plan")

        try:
            duration = int(duration)
        except ValueError:
            messages.error(request, "Invalid duration.")
            return redirect("prop:marketing_renew_plan")

        # ---------------- PRICE TABLE ----------------
        plan_prices = {
            "EXPORT": 9999,
            "EXPORT_PRO": 14999,
            "EXPORT_PREMIUM":24999,
            "OWNER":9999,
            "PROFESSIONAL_SINGLE": 4999,
        }

        total_amount = plan_prices.get(plan_type, 0) * duration
        today = timezone.now().date()

        # ================= MARKETER =================
        if role == "MARKETER":

            if user.marketer_subscription_end_date and user.marketer_subscription_end_date > today:
                base_date = user.marketer_subscription_end_date
            else:
                base_date = today

            user.marketing_plan = plan_type
            user.marketer_subscription_end_date = base_date + timedelta(days=30 * duration)

        # ================= PROFESSIONAL =================
        elif role == "PROFESSIONAL":

            if user.professionals_subscription_end_date and user.professionals_subscription_end_date > today:
                base_date = user.professionals_subscription_end_date
            else:
                base_date = today

            user.professionals_subscription_type = plan_type
            user.professionals_subscription_end_date = base_date + timedelta(days=30 * duration)
            
        elif role == "OWNER":

            if user.owner_subscription_end_date and user.owner_subscription_end_date > today:
                base_date = user.owner_subscription_end_date
            else:
                base_date = today

            user.owner_subscription_type = plan_type
            user.owner_subscription_end_date = base_date + timedelta(days=30 * duration)
            
        user.save()

        messages.success(
            request,
            f"Your {plan_type} plan activated for {duration} month(s). Total ₹{total_amount}"
        )

        return redirect("prop:profile")

    return render(request, "company_renew_plan.html", {"user": user}) 
    
    
# ===================== USER PROFILE VIEW =====================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import AddPropertyModel, ProfileLeadsModel

@login_required
def profile(request):
    user = request.user

    # ===== Upload Count =====
    properties = AddPropertyModel.objects.filter(user=user)
    upload_count = properties.count()
    sold_count = properties.filter(status="Sold Out").count()
    pending_count = properties.filter(is_verified=False).count()

    # Display status is now a @property in the model, so we don't need to manually set it here.

    # ===== Leads aggregation =====
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    from datetime import date, timedelta
    import json
    
    today_date = date.today()
    last_7_days = [(today_date - timedelta(days=i)).strftime("%d %b") for i in range(6, -1, -1)]

    leads = ProfileLeadsModel.objects.filter(leadTo=user)
    lcount = leads.count()
    leads_labels = last_7_days[:]
    leads_counts = [0] * 7
    leads_by_date = leads.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    for item in leads_by_date:
        d_str = item['date'].strftime("%d %b")
        if d_str in leads_labels:
            leads_counts[leads_labels.index(d_str)] = item['count']

    # Referrals aggregation
    referrals_labels = last_7_days[:]
    referrals_counts = [0] * 7
    if user.user_referral_code:
        referrals_qs = User.objects.filter(referred_by_code=user.user_referral_code)
        referrals_by_date = referrals_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        for item in referrals_by_date:
            d_str = item['date'].strftime("%d %b")
            if d_str in referrals_labels:
                referrals_counts[referrals_labels.index(d_str)] = item['count']

    # Activity Pie Data
    reels_count = Reels.objects.filter(user=user).count()
    props_count = properties.count()
    activity_labels = ["Reels", "Properties"]
    activity_counts = [reels_count, props_count]

    # ===== Subscription Logic =====
    today = timezone.now().date()
    is_expired = False
    show_expiry_warning = False
    days_left = None
    expiry_message = ""
    plan_name = None

    # Determine expiry date based on role
    if user.role == "PROFESSIONAL":
        expiry_date = user.professionals_subscription_end_date
        plan_name = "Professional Plan"
    elif user.role == "MARKETER":
        expiry_date = user.marketer_subscription_end_date
        plan_name = "Marketing Plan"
    elif user.role == "OWNER":
        expiry_date = user.owner_subscription_end_date
        plan_name = "Owner Plan"
        
    else:
        expiry_date = None

    # Check subscription status
    if expiry_date:
        days_left = (expiry_date - today).days
        if days_left < 0:
            is_expired = True
            expiry_message = f"Your {plan_name} expired on {expiry_date.strftime('%d-%m-%Y')}."
        elif days_left <= 7:
            show_expiry_warning = True
            expiry_message = f"Your {plan_name} will expire on {expiry_date.strftime('%d-%m-%Y')}."
        else:
            expiry_message = f"Your {plan_name} is active until {expiry_date.strftime('%d-%m-%Y')}."
    else:
        if user.role in ["PROFESSIONAL", "MARKETER"]:
            is_expired = True
            expiry_message = "You do not have an active subscription."

    context = {
        "data": user,
        "properties": properties,
        "upload_count": upload_count,
        "sold_count": sold_count,
        "pending_count": pending_count,
        "lcount": lcount,
        "leads_qs": leads,
        "is_expired": is_expired,
        "expiry_message": expiry_message,
        "show_expiry_warning": show_expiry_warning,
        "days_left": days_left,
        "leads_labels": json.dumps(leads_labels),
        "leads_counts": json.dumps(leads_counts),
        "referrals_labels": json.dumps(referrals_labels),
        "referrals_counts": json.dumps(referrals_counts),
        "activity_labels": json.dumps(activity_labels),
        "activity_counts": json.dumps(activity_counts),
    }

    if user.role == "OWNER":
        return render(request, "owner_profile.html", context)
    elif user.role == "PROFESSIONAL":
        return redirect("prop:professional_profile")
    elif user.role == "MARKETER":
        return redirect("prop:marketer_profile")
    elif user.role == "COMPANY":
        return redirect("prop:company_profile")
    elif user.role == "FRANCHISE":
        return redirect("prop:franchise_profile")
    
    return render(request, "owner_profile.html", context) # Fallback

def professional_profile_view(request, user_id=None):
    if not user_id and not request.user.is_authenticated:
        return redirect('prop:login')
        
    user = request.user
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = user

    is_owner = (user.id == profile_user.id)

    # If not the owner, show the public visitor view (user_detail)
    if not is_owner:
        return redirect('prop:user_detail', user_id=profile_user.id)

    # Properties/Stats
    properties = AddPropertyModel.objects.filter(user=profile_user).order_by('-id')
    upload_count = properties.count()
    sold_count = properties.filter(status="Sold Out").count()
    pending_count = properties.filter(is_verified=False).count()
    # display_status is now a @property

    # Increase profile views only for visitors
    if request.user != profile_user:
        profile_user.click = (profile_user.click or 0) + 1
        profile_user.save()

    # Chart Data Setup
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    from datetime import date, timedelta
    import json
    
    today_date = date.today()
    last_7_days = [(today_date - timedelta(days=i)).strftime("%d %b") for i in range(6, -1, -1)]

    # Leads aggregation
    leads_qs = ProfileLeadsModel.objects.filter(leadTo=profile_user)
    lcount = leads_qs.count()
    leads_labels = last_7_days[:]
    leads_counts = [0] * 7
    leads_by_date = leads_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    for item in leads_by_date:
        d_str = item['date'].strftime("%d %b")
        if d_str in leads_labels:
            leads_counts[leads_labels.index(d_str)] = item['count']

    # Referrals aggregation
    referrals_labels = last_7_days[:]
    referrals_counts = [0] * 7
    if profile_user.user_referral_code:
        referrals_qs = User.objects.filter(referred_by_code=profile_user.user_referral_code)
        referrals_by_date = referrals_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        for item in referrals_by_date:
            d_str = item['date'].strftime("%d %b")
            if d_str in referrals_labels:
                referrals_counts[referrals_labels.index(d_str)] = item['count']

    # Activity Pie Data
    reels_count = Reels.objects.filter(user=profile_user).count()
    props_count = properties.count()
    projects_count = AddProject.objects.filter(user=profile_user).count()
    
    activity_labels = ["Reels", "Properties", "Projects"]
    activity_counts = [reels_count, props_count, projects_count]

    # Area Serves tags
    area_tags = []
    if profile_user.area_serves:
        area_tags = [tag.strip() for tag in profile_user.area_serves.split(",") if tag.strip()]

    # Subscription
    today = timezone.now().date()
    is_expired = False
    show_expiry_warning = False
    days_left = None
    expiry_date = profile_user.professionals_subscription_end_date
    news_posts = NewsPost.objects.filter(user=profile_user).order_by('-created_at')
    
    if expiry_date:
        days_left = (expiry_date - today).days
        if days_left < 0:
            is_expired = True
        elif days_left <= 7:
            show_expiry_warning = True

    reels = Reels.objects.filter(user=profile_user).order_by('-id')
    feed_posts = NewsPost.objects.filter(user=profile_user).order_by('-created_at')

    # Handle inline feed post (owner only)
    if request.method == 'POST' and is_owner:
        post_type = request.POST.get('post_type', '')

        if post_type == 'feed':
            heading = request.POST.get('heading', '').strip()
            news_content = request.POST.get('news_content', '').strip()
            media_file = request.FILES.get('media_file')
            if heading or news_content:
                post = NewsPost(user=request.user, heading=heading, news_content=news_content)
                if media_file:
                    if media_file.content_type.startswith('image'):
                        post.media_type = 'image'
                        post.image = media_file
                    elif media_file.content_type.startswith('video'):
                        post.media_type = 'video'
                        post.video = media_file
                else:
                    post.media_type = 'text'
                post.save()
                messages.success(request, 'Feed posted successfully!')
            return redirect(request.path + '?tab=feed')

        elif post_type == 'reel':
            reel_file = request.FILES.get('reel')
            description = request.POST.get('description', '').strip()
            if reel_file:
                reel = Reels(user=request.user, reel=reel_file, description=description or 'Reel')
                reel.save()
                messages.success(request, 'Reel uploaded successfully!')
            return redirect(request.path + '?tab=bytes')

    active_tab = request.GET.get('tab', 'dashboard')

    context = {
        "data": profile_user,
        "is_owner": is_owner,
        "news_posts": news_posts,
        "feed_posts": feed_posts,
        "reels": reels,
        "polls": Poll.objects.filter(user=profile_user).order_by("-created_at"),
        "properties": properties,
        "upload_count": upload_count,
        "sold_count": sold_count,
        "pending_count": pending_count,
        "lcount": lcount,
        "area_tags": area_tags,
        "is_expired": is_expired,
        "show_expiry_warning": show_expiry_warning,
        "days_left": days_left,
        "rating": 4.5,
        "rating_count": 200,
        "active_tab": active_tab,
        "leads_labels": json.dumps(leads_labels),
        "leads_counts": json.dumps(leads_counts),
        "referrals_labels": json.dumps(referrals_labels),
        "referrals_counts": json.dumps(referrals_counts),
        "activity_labels": json.dumps(activity_labels),
        "activity_counts": json.dumps(activity_counts),
        "leads_qs": leads_qs,
    }

    return render(request, "professional_profile.html", context)

def marketer_profile_view(request, user_id=None):
    if not user_id and not request.user.is_authenticated:
        return redirect('prop:login')
        
    user = request.user
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = user

    is_owner = (user.id == profile_user.id)

    # If not the owner, show the public visitor view (user_detail)
    if not is_owner:
        return redirect('prop:user_detail', user_id=profile_user.id)

    # Properties/Stats
    properties = AddPropertyModel.objects.filter(user=profile_user).order_by('-id')
    upload_count = properties.count()
    sold_count = properties.filter(status="Sold Out").count()
    pending_count = properties.filter(is_verified=False).count()
    # display_status is now a @property

    # Increase profile views only for visitors
    if request.user != profile_user:
        profile_user.click = (profile_user.click or 0) + 1
        profile_user.save()

    # Chart Data Setup
    from datetime import date, timedelta
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    import json
    
    leads_qs = ProfileLeadsModel.objects.filter(leadTo=profile_user)
    lcount = leads_qs.count()
    
    today_date = date.today()
    last_7_days = [(today_date - timedelta(days=i)).strftime("%d %b") for i in range(6, -1, -1)]

    # Leads aggregation
    leads_labels = last_7_days[:]
    leads_counts = [0] * 7
    leads_by_date = leads_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    for item in leads_by_date:
        d_str = item['date'].strftime("%d %b")
        if d_str in leads_labels:
            leads_counts[leads_labels.index(d_str)] = item['count']

    # Referrals aggregation
    referrals_labels = last_7_days[:]
    referrals_counts = [0] * 7
    if profile_user.user_referral_code:
        referrals_qs = User.objects.filter(referred_by_code=profile_user.user_referral_code)
        referrals_by_date = referrals_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        for item in referrals_by_date:
            d_str = item['date'].strftime("%d %b")
            if d_str in referrals_labels:
                referrals_counts[referrals_labels.index(d_str)] = item['count']

    # Activity Pie Data
    reels_count = Reels.objects.filter(user=profile_user).count()
    props_count = properties.count()
    projects_count = AddProject.objects.filter(user=profile_user).count()
    
    activity_labels = ["Reels", "Properties", "Projects"]
    activity_counts = [reels_count, props_count, projects_count]

    # Area Serves tags
    area_tags = []
    if profile_user.area_serves:
        area_tags = [tag.strip() for tag in profile_user.area_serves.split(",") if tag.strip()]

    # Subscription
    today = timezone.now().date()
    is_expired = False
    show_expiry_warning = False
    days_left = None
    expiry_date = profile_user.marketer_subscription_end_date
    reels = Reels.objects.filter(user=profile_user).order_by('-id')
    feed_posts = NewsPost.objects.filter(user=profile_user).order_by('-created_at')
    active_tab = request.GET.get('tab', 'dashboard')

    context = {
        "data": profile_user,
        "is_owner": is_owner,
        "feed_posts": feed_posts,
        "reels": reels,
        "active_tab": active_tab,
        "polls": Poll.objects.filter(user=profile_user).order_by("-created_at"),
        "properties": properties,
        "upload_count": upload_count,
        "sold_count": sold_count,
        "pending_count": pending_count,
        "lcount": lcount,
        "area_tags": area_tags,
        "is_expired": is_expired,
        "show_expiry_warning": show_expiry_warning,
        "days_left": days_left,
        
        "rating": 4.8,
        "rating_count": 150,

        "leads_labels": json.dumps(leads_labels),
        "leads_counts": json.dumps(leads_counts),
        "referrals_labels": json.dumps(referrals_labels),
        "referrals_counts": json.dumps(referrals_counts),
        "activity_labels": json.dumps(activity_labels),
        "activity_counts": json.dumps(activity_counts),
        "leads_qs": leads_qs,
    }

    return render(request, "marketer_profile.html", context)
    
  
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required
def update_plans(request):
    user = request.user

    if request.method == "POST":
        role = request.POST.get("role")

        if not role:
            messages.error(request, "Please select a role.")
            return redirect("prop:update_plans")

        today = timezone.now().date()
        user.role = role

        # ==================================================
        # 🔥 CLEAR EVERYTHING FIRST (VERY IMPORTANT FIX)
        # ==================================================
        user.plan_type = None   # 🔥 Fix for wrong plan_type column
        user.category = None
        user.marketer_category = None

        # Professional
        user.professionals_subscription_type = None
        user.professionals_subscription_start_date = None
        user.professionals_subscription_end_date = None

        # Owner
        user.owner_subscription_type = None
        user.owner_subscription_start_date = None
        user.owner_subscription_end_date = None

        # Marketer
        user.marketing_subscription_type = None
        user.marketing_plan_duration = None
        user.marketer_subscription_start_date = None
        user.marketer_subscription_end_date = None

        # ==================================================
        # PROFESSIONAL
        # ==================================================
        if role == "PROFESSIONAL":

            category = request.POST.get("category")
            plan_type = request.POST.get("professional_plan_type")
            duration = request.POST.get("professional_duration")

            user.category = category

            if plan_type and duration:
                duration = int(duration)

                user.professionals_subscription_type = plan_type
                user.professionals_subscription_start_date = today
                user.professionals_subscription_end_date = (
                    today + timedelta(days=30 * duration)
                )

                # Optional: keep main plan_type column synced
                user.plan_type = plan_type

                messages.success(
                    request,
                    f"Professional plan activated for {duration} month(s)."
                )
            else:
                messages.success(
                    request,
                    "Profile updated to Professional (No plan activated)."
                )

        # ==================================================
        # OWNER
        # ==================================================
        elif role == "OWNER":

            plan_type = request.POST.get("owner_plan_type")
            duration = request.POST.get("owner_duration")

            if plan_type and duration:
                duration = int(duration)

                user.owner_subscription_type = plan_type
                user.owner_subscription_start_date = today
                user.owner_subscription_end_date = (
                    today + timedelta(days=30 * duration)
                )

                # Optional: sync
                user.plan_type = plan_type

                messages.success(
                    request,
                    f"Owner plan activated for {duration} month(s)."
                )
            else:
                messages.success(
                    request,
                    "Profile updated to Owner (No plan activated)."
                )

        # ==================================================
        # MARKETER
        # ==================================================
        elif role == "MARKETER":

            marketer_cats = request.POST.getlist("marketer_category")
            user.marketer_category = (
                ",".join(marketer_cats) if marketer_cats else None
            )

            plan_type = request.POST.get("plan_type")
            duration = request.POST.get("duration")

            if plan_type and duration:
                duration = int(duration)

                user.marketing_subscription_type = plan_type
                user.marketing_plan_duration = duration
                user.marketer_subscription_start_date = today
                user.marketer_subscription_end_date = (
                    today + timedelta(days=30 * duration)
                )

                # Optional: sync
                user.plan_type = plan_type

                messages.success(
                    request,
                    f"Marketing plan activated: {plan_type} for {duration} month(s)."
                )
            else:
                messages.success(
                    request,
                    "Profile updated to Marketer (No plan activated)."
                )

        # ==================================================
        user.save()
        return redirect("prop:profile")

    return render(request, "company_renew_plan.html", {"user": user})
# propertry list

from django.http import HttpResponse
def get_Property(req,prop):
    a=AddPropertyModel.objects.filter(selectProperty=prop)
    print(a)
    
    return HttpResponse(a)
    
    


def property_list(request, prop):
    if prop == "All":
        properties = AddPropertyModel.objects.all().exclude(is_notSold=True).exclude(user__role='OWNER', is_verified=False)
    else:
        properties = AddPropertyModel.objects.filter(selectProperty=prop).exclude(is_notSold=True).exclude(user__role='OWNER', is_verified=False)

    name = request.GET.get("name")
    location = request.GET.get("location")
    is_verified = request.GET.get("verified")
    city = request.GET.get("city")

    # Accept both old (min_price/max_price) and new navbar form names (minpricing/maxpricing)
    min_price = request.GET.get("min_price") or request.GET.get("minpricing")
    max_price = request.GET.get("max_price") or request.GET.get("maxpricing")

    # Accept both old (road) and new navbar form name (facing)
    road_facing = request.GET.get("road") or request.GET.get("facing")

    look = request.GET.get("look")
    position = request.GET.get("position")
    approval = request.GET.get("approval")

    if location:
        properties = properties.filter(address__icontains=location)
    if city:
        properties = properties.filter(address__icontains=city)
    if name:
        properties = properties.filter(projectName__icontains=name)
    if is_verified in ['1', '0']:
        properties = properties.filter(is_verified=(is_verified == '1'))
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if road_facing:
        properties = properties.filter(facing=road_facing)
    if look in ['Buy', 'Rent']:
        properties = properties.filter(look=look)
    if position in ['READY', 'UNDER']:
        properties = properties.filter(position=position)
    if approval:
        properties = properties.filter(type_of_approval__icontains=approval)

    properties = properties.order_by('-id')
    return render(request, "property_list.html", {"data": properties, "prop": prop})


def property_detail(request, id):
    data = get_object_or_404(AddPropertyModel, id=id)
    
    # Restrict unverified owner properties from public view
    if data.user.role == 'OWNER' and not data.is_verified:
        if not request.user.is_authenticated or (request.user != data.user and not request.user.is_staff):
            from django.http import Http404
            raise Http404("Property is pending verification.")

    if request.user.is_authenticated:
        PropertyInteraction.objects.get_or_create(
            user=request.user,
            property=data,
            interaction_type='view'
        )

    return render(request, "property_detail.html", {"item": data})

def filterbox(request):
    # Use PROPERTY_CHOICES from the model for dropdown
    all_properties = AddPropertyModel.PROPERTY_CHOICES
    return render(request, "filterbox.html", {"all_properties": all_properties})




# edit----------


from .forms import UserProfileForm


@login_required
def edit_profile(request):
    user = request.user  # currently logged-in user
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()  # <-- updates the database
            return redirect('prop:profile')  # redirect back to profile page
    form = UserProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def user_uploades(req):
    p= req.user
    D = AddPropertyModel.objects.filter(user = p)
    # D= User.objects.filter(AddPropertyModel = upload)

    return render(req, "user_uploades.html",{"D":D})

def property_leads_get(req, id):
    pro = AddPropertyModel.objects.get(id=id)
    try:
        pro = AddPropertyModel.objects.get(id=id)
    except AddPropertyModel.DoesNotExist:
        return JsonResponse({"error": "Property not found"}, status=404)
    leads_qs = PropertyLeadsModel.objects.filter(property=pro)
    
    leads_qss = PropertyLeadsModel.objects.filter(property=pro).count()
    print(leads_qss)

    leads = []
    for l in leads_qs:
        leads.append({
           
            "leadFrom_name": l.leadFrom.username,
            "leadFrom_phone": getattr(l.leadFrom, "phone", ""),  # if phone exists

           
            "leadTo_name": l.leadTo.username,
            "leadTo_phone": getattr(l.leadTo, "phone", ""),

            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return JsonResponse({"leads": leads,"count":leads_qss})






@login_required
def referral(req):
    user = req.user
    referral_code = user.user_referral_code

    referrals = User.objects.filter(referred_by_code=referral_code)

    referral_list = []
    total_amount = 0
    percentage = 5  # 5% referral

    for r in referrals:
        plan_price = r.plan_price or 0
        amount = (plan_price * percentage) / 100
        total_amount += amount  # sum up total

        referral_list.append({
            "username": r.username,
            "phone": r.phone,
            "email": r.email,
            "plan_price": plan_price,
            "percentage": percentage,
            "amount": amount
        })

    return render(req, "referral.html", {"s": referral_list, "total_amount": total_amount})



# move form************
from .forms import MoveRequestForm


def move_form(request):
    if request.method == "POST":
        form = MoveRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "move_form.html", {
                "form": MoveRequestForm(),
                "success": True
            })
    else:
        form = MoveRequestForm()

    return render(request, "move_form.html", {"form": form})


from django.shortcuts import render
from .models import ContactForm
def contact_form_view(request):
    success = False
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        number = request.POST.get("number")
        alternate_number = request.POST.get("alternate_number")
        renovation_type = request.POST.get("renovation_type")
        location = request.POST.get("location")
        additional_info = request.POST.get("additional_info")

        ContactForm.objects.create(
            customer_name=customer_name,
            number=number,
            alternate_number=alternate_number,
            renovation_type=renovation_type,
            location=location,
            additional_info=additional_info,
        )
        success = True

    return render(request, "contact_form.html", {"success": success})

    # loan form*************


def loan_form(request):
    if request.method == 'POST':
        data = LoanApplication(
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            dob=request.POST.get('dob'),
            street_address=request.POST.get('street_address'),
            unit=request.POST.get('unit'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zip_code=request.POST.get('zip_code'),
            loan_amount=request.POST.get('loan_amount'),
            loan_purpose=request.POST.get('loan_purpose'),
            application_date=request.POST.get('application_date'),
            employment_status=request.POST.get('employment_status'),
            realtor=request.POST.get('realtor'),
            credit_score=request.POST.get('credit_score'),
            agree=('agree' in request.POST)
        )
        data.save()
        messages.success(request, "✅ Loan Application submitted successfully!")
        return redirect('prop:loan_form')
    return render(request, 'loan_form.html')


from datetime import date, timedelta
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CompanyRegisterForm
from .models import User, PlanType


def company_register(request):
    # Companies are considered registered if they have a company name
    if request.user.is_authenticated and (request.user.role == "COMPANY" or request.user.company_name):
        return redirect("prop:home")
    
    if request.method == "POST":
        form = CompanyRegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = "COMPANY"

            # ===============================
            # PLAN MAPPING
            # ===============================
            plan = form.cleaned_data.get("plan")
            duration = form.cleaned_data.get("duration")

            plan_mapping = {
                "NORMAL": PlanType.COMPANY_NORMAL,
                "PRO": PlanType.COMPANY_PRO,
                "PREMIUM": PlanType.COMPANY_PREMIUM,
            }

            selected_plan = plan_mapping.get(plan, PlanType.COMPANY_NORMAL)

            user.plan_type = selected_plan
            user.selected_duration = duration

            # ===============================
            # ACTIVATE SUBSCRIPTION
            # ===============================
            user.company_subscription_type = plan
            user.company_subscription_start_date = date.today()
            user.company_subscription_end_date = date.today() + timedelta(days=30 * duration)

            user.save()

            # ===============================
            # LOGIN USER
            # ===============================
            authenticated_user = authenticate(
                request,
                username=user.username,
                password=form.cleaned_data.get("password1")
            )

            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, "Company registered successfully!")
                return redirect("prop:home")

        else:
            print("FORM ERRORS:", form.errors)

    else:
        form = CompanyRegisterForm()

    return render(request, "company_register.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.files.storage import default_storage
from .models import User,ContactMessage
from .forms import CompanyRegisterForm

def company_profile_view(request, user_id=None):
    if not user_id and not request.user.is_authenticated:
        return redirect('prop:login')

    # Get profile user
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user

    # Handle owner updates
    if request.method == "POST" and request.user == profile_user:
        profile_user.company_name = request.POST.get("company_name")
        profile_user.email = request.POST.get("email")
        profile_user.address = request.POST.get("address")
        profile_user.contact_number = request.POST.get("contact_number")
        profile_user.experience = request.POST.get("experience")
        profile_user.total_projects = request.POST.get("total_projects")
        profile_user.ongoing_projects = request.POST.get("ongoing_projects")
        profile_user.completed_projects = request.POST.get("completed_projects")
        profile_user.description = request.POST.get("description")

        if request.FILES.get("company_logo_path"):
            logo_file = request.FILES["company_logo_path"]
            logo_path = default_storage.save(f"company_logo/{logo_file.name}", logo_file)
            profile_user.company_logo_path = logo_path

        if request.FILES.get("company_wallpaper_path"):
            wall_file = request.FILES["company_wallpaper_path"]
            wallpaper_path = default_storage.save(f"company_wallpaper/{wall_file.name}", wall_file)
            profile_user.company_wallpaper_path = wallpaper_path

        profile_user.save()
        messages.success(request, "Profile Updated Successfully!")
        return redirect("prop:company_profile")

    # Increase profile views only for visitors
    if request.user != profile_user:
        profile_user.click = (profile_user.click or 0) + 1
        profile_user.save()

    # Owner check
    is_owner = (request.user == profile_user)

    # If not the owner, show the public visitor view (user_detail)
    if not is_owner:
        return redirect('prop:user_detail', user_id=profile_user.id)

    # Contact count
    contact_count = ContactMessage.objects.filter(cid=str(profile_user.id)).count()

    # Projects/Stats
    projects = AddProject.objects.filter(user=profile_user).order_by('-id')
    upload_count = projects.count()
    # Assuming 'Sold' projects are marked somehow, otherwise 0 for now or use completed_projects
    sold_count = profile_user.completed_projects or 0
    # Assuming 'Pending' are ongoing
    pending_count = profile_user.ongoing_projects or 0

    # Chart Data Setup
    today_date = date.today()
    last_7_days = [(today_date - timedelta(days=i)).strftime("%d %b") for i in range(6, -1, -1)]

    # Leads aggregation
    leads_qs = ProfileLeadsModel.objects.filter(leadTo=profile_user)
    lcount = leads_qs.count()
    leads_labels = last_7_days[:]
    leads_counts = [0] * 7
    leads_by_date = leads_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    for item in leads_by_date:
        d_str = item['date'].strftime("%d %b")
        if d_str in leads_labels:
            leads_counts[leads_labels.index(d_str)] = item['count']

    # Referrals aggregation
    referrals_labels = last_7_days[:]
    referrals_counts = [0] * 7
    if profile_user.user_referral_code:
        referrals_qs = User.objects.filter(referred_by_code=profile_user.user_referral_code)
        referrals_by_date = referrals_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
        for item in referrals_by_date:
            d_str = item['date'].strftime("%d %b")
            if d_str in referrals_labels:
                referrals_counts[referrals_labels.index(d_str)] = item['count']

    # Activity Data (Example: Projects, Leads, etc.)
    activity_labels = ['Projects', 'Leads', 'Referrals']
    total_referrals = sum(referrals_counts)
    activity_counts = [upload_count, lcount, total_referrals]

    show_expiry_warning = False
    is_expired = False
    days_left = None

    if profile_user.company_subscription_end_date:
        today = timezone.now().date()
        expiry_date = profile_user.company_subscription_end_date
        days_left = (expiry_date - today).days

        if days_left < 0:
            is_expired = True
        elif days_left <= 7:
            show_expiry_warning = True

    reels = Reels.objects.filter(user=profile_user).order_by('-id')
    feed_posts = NewsPost.objects.filter(user=profile_user).order_by('-created_at')
    active_tab = request.GET.get('tab', 'dashboard')

    return render(request, "company_profile.html", {
        "profile_user": profile_user,
        "projects": projects,
        "is_owner": is_owner,
        "upload_count": upload_count,
        "sold_count": sold_count,
        "pending_count": pending_count,
        "lcount": lcount,
        "feed_posts": feed_posts,
        "reels": reels,
        "active_tab": active_tab,
        "leads_labels": json.dumps(leads_labels),
        "leads_counts": json.dumps(leads_counts),
        "referrals_labels": json.dumps(referrals_labels),
        "referrals_counts": json.dumps(referrals_counts),
        "activity_labels": json.dumps(activity_labels),
        "activity_counts": json.dumps(activity_counts),
        "days_left": days_left,
        "is_expired": is_expired,
        "show_expiry_warning": show_expiry_warning,
        "leads_qs": leads_qs,
    })
# project_edit----------------------------

def edit_project(request, id):
    project = AddProject.objects.get(id=id)
    if request.method == "POST":

        project.project_name = request.POST.get("project_name")
        project.type_of_project = request.POST.get("type_of_project")
        project.project_address = request.POST.get("project_address")
        project.location_url = request.POST.get("location_url")
        project.number_of_units = request.POST.get("number_of_units")
        project.available_units = request.POST.get("available_units")
        project.available_facing = request.POST.get("available_facing")
        project.available_sizes = request.POST.get("available_sizes")
        project.rera_approved = bool(request.POST.get("rera_approved"))
        project.select_amenities = request.POST.get("select_amenities")
        project.highlights = request.POST.get("highlights")
        project.type_of_approval = request.POST.get("type_of_approval")
        project.total_project_area = request.POST.get("total_project_area")
        project.contact_info = request.POST.get("contact_info")
        project.pricing = request.POST.get("pricing")
         # Nearby locations (LIST)
        nearby_list = request.POST.getlist("nearby_locations[]")
 
        nearby_list = [i.strip() for i in nearby_list if i.strip()]

        project.nearby_locations = nearby_list

        # image update
        if request.FILES.get("image"):
            project.image = request.FILES.get("image")

        # video update
        if request.FILES.get("video"):
            project.video = request.FILES.get("video")

        # document update
        if request.FILES.get("document"):
            project.document = request.FILES.get("document")

        project.save()

        return redirect("prop:company_profile")  # redirect back to list

    return render(request, "edit_project.html", {"project": project})


def projects_views_list(request, user_id=None):
    is_owner = True

    if user_id:
        # Visitor: viewing other user's projects
        user = User.objects.get(id=user_id)
        is_owner = False
    else:
        user = request.user
        is_owner = True

    projects = AddProject.objects.filter(user=user)

    final_projects = []
    for p in projects:
        # Get all leads for this project
        leads = ProjectLeadsModel.objects.filter(project=p).select_related('leadFrom')

        # Keep only one lead per unique user
        unique_leads = {}
        for l in leads:
            if l.leadFrom and l.leadFrom.id not in unique_leads:
                unique_leads[l.leadFrom.id] = l

        lead_list = []
        for l in unique_leads.values():
            lead_list.append({
                "username": l.leadFrom.username,
                "phone": l.leadFrom.phone,
            })

        final_projects.append({
            "project": p,
            "leads": lead_list,
            "lead_count": len(lead_list),  # now unique count
        })

    return render(request, "projects_all_list.html", {
        "projects": final_projects,
        "is_owner": is_owner,
        "profile_user": user,
    })
@login_required
def delete_project(request, id):
    project = AddProject.objects.get(id=id, user=request.user)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect("prop:company_profile")

@login_required
def mark_sold(request, id):
    project = AddProject.objects.get(id=id, user=request.user)
    project.status = "Sold"
    project.save()
    messages.success(request, "Project marked as sold!")
    return redirect("prop:company_profile")

@login_required
def delete_reel(request, id):
    reel = get_object_or_404(Reels, id=id, user=request.user)
    reel.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True})
    messages.success(request, "Reel deleted successfully!")
    return redirect("prop:profile")

 
# Contact Form Submit
def contact_submit(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=request.POST.get("contact_name"),
            email=request.POST.get("email"),
            requirement=request.POST.get("requirement"),
            message=request.POST.get("message"),
            cid=request.POST.get("contact_id"),
        )
        if request.user.is_authenticated:
            PropertyInteraction.objects.create(
                user=request.user,
                interaction_type='enquiry'
            )
        messages.success(request, "Message Sent Successfully!")
        return redirect(request.META.get("HTTP_REFERER", "company_profile"))

    return redirect(request.META.get("HTTP_REFERER", "company_profile"))


# franchise register**********************
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
@staff_member_required
def franchise_register(request):
    if request.method == "POST":
        form = FranchiseForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)

            user.phone = form.cleaned_data["phone"]
            user.location = form.cleaned_data["location"]
            user.experience = form.cleaned_data["experience"]
            user.role = "FRANCHISE"

            if form.cleaned_data.get("profile_image"):
                user.profile_image_path = form.cleaned_data["profile_image"]

            try:
                user.save()  # <-- Catch error here

                messages.success(request, "Franchise registered successfully! Please login.")
                return redirect("prop:login")

            except IntegrityError:
                # Add error on the phone field
                form.add_error("phone", "This phone number is already registered.")
                messages.error(request, "Please correct the errors below.")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = FranchiseForm()

    return render(request, "franchise_register.html", {"form": form})
 
# =============================
# FRANCHISE PROFILE & EDIT
# =============================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import FranchiseProperty, AddPropertyModel

@login_required
def franchise_profile(request):
    if request.user.role != "FRANCHISE":
        return redirect("prop:home")

    # Get properties explicitly assigned to this franchise
    assigned_tasks = FranchiseProperty.objects.filter(
        franchise=request.user
    ).select_related('property')

    # Pending tasks (property not verified)
    pending_tasks = [task for task in assigned_tasks if not task.property.is_verified]
    
    # Verified tasks (property verified)
    verified_tasks = [task for task in assigned_tasks if task.property.is_verified]

    # Fetch referred users
    referred_users = []
    if request.user.user_referral_code:
        referred_users = User.objects.filter(referred_by_code=request.user.user_referral_code)

    return render(request, "franchise_profile.html", {
        "profile": request.user,
        "news_posts": NewsPost.objects.filter(user=request.user).order_by('-created_at'),
        "polls": Poll.objects.filter(user=request.user).order_by("-created_at"),

        "assigned": assigned_tasks.count(),
        "pending": len(pending_tasks),
        "verified": len(verified_tasks),

        "assigned_tasks": assigned_tasks,
        "verified_tasks": verified_tasks,
        "pending_tasks": pending_tasks,
        "referred_users": referred_users,
    })


@login_required
def franchise_edit(request):
    user = request.user

    if request.method == "POST":
        errors = {}
        form_data = request.POST.copy()

        email = request.POST.get("email", "").strip()
        phone = request.POST.get("contact_number", "").strip()
        location = request.POST.get("location", "").strip()
        radius = request.POST.get("radius", "").strip()
        experience = request.POST.get("experience", "").strip()
        description = request.POST.get("description", "").strip()

        # ===== REQUIRED VALIDATION =====
        if not email:
            errors["email"] = "Email is required."
        if not phone:
            errors["phone"] = "Contact number is required."
        if not location:
            errors["location"] = "Location is required."
        if not radius:
            errors["radius"] = "Radius is required."
        if not experience:
            errors["experience"] = "Experience is required."
        if not description:
            errors["description"] = "Description is required."

        # If ANY errors ➝ return modal with errors
        if errors:
            return render(request, "franchise_profile.html", {
                "profile": user,
                "errors": errors,
                "form_data": form_data,
                "assigned": user.total_projects,
                "pending": user.ongoing_projects,
                "verified": user.completed_projects,
                "show_modal": True,   
            })

        # ===== SAVE VALID DATA =====
        user.email = email
        user.phone = phone
        user.location = location
        user.radius = int(radius)
        user.experience = int(experience)
        user.description = description

        if request.FILES.get("profile_image"):
            user.profile_image_path = request.FILES["profile_image"]

        user.save()

        return redirect("prop:franchise_profile")

    return redirect("prop:franchise_profile")

@login_required
def verify_property(request):
    if request.method == "POST":

        property_id = request.POST.get("property_id")
        reviews = request.POST.get("reviews")
        amount = request.POST.get("amount")
        verified_location = request.POST.get("verified_location")
        video_file = request.FILES.get("video_file")

        try:
            prop = AddPropertyModel.objects.get(id=property_id)
        except AddPropertyModel.DoesNotExist:
            return redirect("prop:franchise_profile")

        # Create record in FranchiseProperty table
        FranchiseProperty.objects.create(
            property=prop,
            property_id_number=prop.id,      # <-- here we store ID
            franchise=request.user,
            reviews=reviews,
            amount=amount,
            verified_location=verified_location,
            video_file=video_file,
        )

        # Mark property verified
        prop.is_verified = True
        prop.save()

        return redirect("prop:franchise_profile")







# addproject-------
def add_project(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to add a project.")
        return redirect("prop:login")
        
    if request.user.role != "COMPANY":
        messages.error(request, f"Access denied. Only Builders (Company roles) can add projects. Your current role is: {request.user.role}")
        return redirect("prop:home")

    if request.method == "POST":
        project_name = request.POST.get("project_name")
        type_of_project = request.POST.get("type_of_project")
        project_address = request.POST.get("project_address")
        location_url = request.POST.get("location_url")
        number_of_units = request.POST.get("number_of_units")
        available_units = request.POST.get("available_units")
        available_facing = request.POST.get("available_facing")
        available_sizes = request.POST.get("available_sizes")
        position = request.POST.get("position")
        construction_time = request.POST.get("construction_time")
        estbalis_year = request.POST.get("estbalis_year")

        # ✅ FIXED nearby
        nearby_locations = request.POST.getlist("nearby_locations[]")

        # ✅ FIXED rera
        rera_approved = request.POST.get("rera_approved") == "True"

        amenities_list = request.POST.getlist("select_amenities")
        amenities = ",".join(amenities_list)

        highlights = request.POST.get("highlights")
        type_of_approval = request.POST.get("type_of_approval")
        total_project_area = request.POST.get("total_project_area")
        contact_info = request.POST.get("contact_info")
        pricing = request.POST.get("pricing")
        
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Get main image and other files
        images = request.FILES.getlist("image")
        video = request.FILES.get("video")
        documents = request.FILES.getlist("document")

        try:
            project = AddProject.objects.create(
                user=request.user,
                plan_type=request.user.plan_type,
                project_name=project_name,
                type_of_project=type_of_project,
                project_address=project_address,
                location_url=location_url,
                latitude=float(latitude) if latitude and latitude.strip() else None,
                longitude=float(longitude) if longitude and longitude.strip() else None,
                number_of_units=number_of_units,
                available_units=available_units,
                nearby_locations=nearby_locations,
                available_facing=available_facing,
                available_sizes=available_sizes,
                estbalis_year=int(estbalis_year) if estbalis_year and estbalis_year.strip() else None,
                rera_approved=rera_approved,
                select_amenities=amenities,
                highlights=highlights,
                type_of_approval=type_of_approval,
                total_project_area=total_project_area,
                contact_info=int(contact_info) if contact_info and contact_info.strip() else 0,
                pricing=int(pricing) if pricing and pricing.strip() else 0,
                position=position,
                construction_time=construction_time,
                image=images[0] if images else None,
                video=video,
                document=documents[0] if documents else None,
            )

            # ✅ Handle Extra Images
            if len(images) > 1:
                for img in images[1:]:
                    ProjectImage.objects.create(project=project, image=img)

            # ✅ Handle Legal Documents
            legal_doc_names = request.POST.getlist("legal_doc_name[]")
            legal_doc_files = request.FILES.getlist("legal_doc_file[]")
            
            for i in range(min(len(legal_doc_names), len(legal_doc_files))):
                ProjectLegalDocument.objects.create(
                    project=project,
                    name=legal_doc_names[i],
                    file=legal_doc_files[i]
                )

            messages.success(request, f"Project '{project.project_name}' added successfully!")
            return redirect("prop:project_detail", id=project.id)
        except Exception as e:
            messages.error(request, f"Error adding project: {str(e)}")
            return redirect("prop:add_project")

    return render(request, "add_project.html")
    
def project_detail(request, id):
    project = AddProject.objects.get(id=id)

    if request.user.is_authenticated:
        PropertyInteraction.objects.get_or_create(
            user=request.user,
            project=project,
            interaction_type='view'
        )

    images = []

    # main image
    if project.image:
        images.append(project.image.url)

    # extra images
    extra = project.extra_images.all()
    for img in extra:
        images.append(img.image.url)

    return render(request, "project_detail.html", {"project": project, "images": images})





from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import AddPropertyModel, SavedProperty


from .models import SavedProperty, SavedProject

@login_required
def saved_properties(request):
    saved_properties = SavedProperty.objects.filter(user=request.user).exclude(
        property__user__role='OWNER', property__is_verified=False
    )
    saved_projects = SavedProject.objects.filter(user=request.user)

    return render(request, "saved_properties.html", {
        "saved_properties": saved_properties,
        "saved_projects": saved_projects
    })

def save_property(request, property_id):
    property_obj = AddPropertyModel.objects.get(id=property_id)

    saved, created = SavedProperty.objects.get_or_create(
        user=request.user,
        property=property_obj
    )

    if not created:
        saved.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "saved"})

from .models import AddProject, SavedProject
 
def save_project(request, project_id):
    project = AddProject.objects.get(id=project_id)

    saved, created = SavedProject.objects.get_or_create(
        user=request.user,
        project=project
    )

    if not created:
        saved.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "saved"})



#otp
import time
import random
import urllib.parse
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

API_KEY = "bGxMnkR7nUa3DpPDGdqhUg"
SENDER_ID = "WDPROP"
TEMPLATE_ID = "1007692442675920680"
PE_ID = "1001053976927196733"
SMS_URL = "https://cloud.smsindiahub.in/api/mt/SendSMS"

otp_storage = {}  # temporary

@csrf_exempt
def send_otp(request):
    phone = request.GET.get("phone")

    if not phone:
        return JsonResponse({"error": "Phone number required"}, status=400)

    otp = "%06d" % random.randint(0, 999999)
    otp_storage[phone] = {"otp": otp, "timestamp": time.time()}

    # MUST MATCH EXACT DLT TEMPLATE
    message = (
        f"Your OTP for verification with Weekdays Properties is {otp}. "
        "Please do not share this code with anyone. It is valid for 10 minutes."
    )

    params = {
        "APIKey": API_KEY,
        "senderid": SENDER_ID,
        "channel": "Trans",
        "DCS": 0,
        "flashsms": 0,
        "number": "91" + phone,
        "text": message,   # RAW MESSAGE (NO URL ENCODE)
        "DLTTemplateId": TEMPLATE_ID,
        "route": "0",
        "PEId": PE_ID
    }

    response = requests.get(SMS_URL, params=params)

    print("SMSIndiaHub Response:", response.text)

    return JsonResponse({
        "status": response.status_code,
        "response": response.text,
        "otp": otp
    })


@csrf_exempt
def verify_otp(request):
    phone = request.GET.get("phone")
    otp = request.GET.get("otp")

    if not phone or not otp:
        return JsonResponse({"error": "Phone and OTP required"}, status=400)

    data = otp_storage.get(phone)

    if not data:
        return JsonResponse({"error": "OTP expired or not sent"}, status=400)

    if time.time() - data["timestamp"] > 600:
        otp_storage.pop(phone)
        return JsonResponse({"error": "OTP expired"}, status=400)

    if otp != data["otp"]:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    otp_storage.pop(phone)
    
    # Save phone to user profile if logged in
    if request.user.is_authenticated:
        user = request.user
        
        # Check if phone is already taken by another user
        if User.objects.filter(phone=phone).exclude(pk=user.pk).exists():
            return JsonResponse({"error": "This phone number is already registered with another account."}, status=400)
            
        try:
            user.phone = phone
            user.save()
        except Exception as e:
            return JsonResponse({"error": f"Failed to save phone number: {str(e)}"}, status=500)

    return JsonResponse({"message": "OTP Verified"})

 
    

from django.http import JsonResponse
from django.forms.models import model_to_dict

from django.http import JsonResponse

def get_property_details(request, id):
    try:
        prop = AddPropertyModel.objects.get(id=id)

        data = {
            "id": prop.id,
            "look": prop.look,
            "selectProperty": prop.selectProperty,
            "projectName": prop.projectName,
            "extent": prop.extent,
            "facing": prop.facing,
            "roadSize": prop.roadSize,
            "units": prop.units,
            "dimensions": prop.dimensions,
            "numberOfFloors": prop.numberOfFloors,
            "numberOfBHK": prop.numberOfBHK,
            "builtUpArea": prop.builtUpArea,
            "openArea": prop.openArea,
            "rentalIncome": prop.rentalIncome,
            "floorNo": prop.floorNo,
            "communityType": prop.communityType,
            "carpetArea": prop.carpetArea,
            "landType": prop.landType,
            "soilType": prop.soilType,
            "roadFacing": prop.roadFacing,
            "waterSource": prop.waterSource,
            "unitType": prop.unitType,
            "zone": prop.zone,
            "developmentType": prop.developmentType,
            "expectedAdvance": prop.expectedAdvance,
            "ratio": prop.ratio,
            "disputeDetails": prop.disputeDetails,
            "lookingToSell": prop.lookingToSell,
            "problemDetails": prop.problemDetails,
            "actualPrice": prop.actualPrice,
            "salePrice": prop.salePrice,
            "price": prop.price,
            "status": prop.status,
            "reraApproved": prop.reraApproved,
            "approvalType": prop.approvalType,
            "amenities": prop.amenities,
            "highlights": prop.highlights,
            "propertyId": prop.propertyId,
            "is_notSold": prop.is_notSold,
            "is_verified": prop.is_verified,
            "is_legal_verified": prop.is_legal_verified,
            "location": prop.address,
            "locationUrl": prop.locationUrl,
            "nearby_places": prop.nearby_places or [],
            "is_verifiedproperty": prop.is_verifiedproperty,

            # FILES
            "image": prop.image.url if prop.image else "",
            "image1": prop.image1.url if prop.image1 else "",
            "image2": prop.image2.url if prop.image2 else "",
            "image3": prop.image3.url if prop.image3 else "",
            "image4": prop.image4.url if prop.image4 else "",
            "video": prop.video.url if prop.video else "",
            "document": prop.document.url if prop.document else "",
        }

        return JsonResponse({"status": "success", "data": data})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

import json

def edit_property(request, id):
    prop = AddPropertyModel.objects.get(id=id)

    if request.method == "POST":

        def to_number(value):
            return float(value) if value not in ["", None] else None

        # TEXT FIELDS
        prop.look = request.POST.get("look") or prop.look
        prop.selectProperty = request.POST.get("selectProperty") or prop.selectProperty
        prop.projectName = request.POST.get("projectName") or prop.projectName
        prop.facing = request.POST.get("facing") or None
        prop.roadSize = request.POST.get("roadSize") or None
        prop.units = request.POST.get("units") or None
        prop.dimensions = request.POST.get("dimensions") or None
        prop.address = request.POST.get("location") or None

        # NUMERIC
        prop.extent = to_number(request.POST.get("extent"))
        prop.numberOfFloors = to_number(request.POST.get("numberOfFloors"))
        prop.numberOfBHK = to_number(request.POST.get("numberOfBHK"))
        prop.builtUpArea = to_number(request.POST.get("builtUpArea"))
        prop.openArea = to_number(request.POST.get("openArea"))

        price_val = request.POST.get("price")
        if price_val not in ["", None]:
            prop.price = float(price_val)

        # BOOLEAN
        prop.reraApproved = request.POST.get("reraApproved") == "on"

        # ✅ NEARBY PLACES (ADD THIS)
        nearby_places = request.POST.get("nearby_places")

        if nearby_places:
            try:
                prop.nearby_places = json.loads(nearby_places)
            except:
                prop.nearby_places = []
        else:
            prop.nearby_places = []

        # FILE
        if request.FILES.get("image"):
            prop.image = request.FILES["image"]

        prop.save()

        return JsonResponse({"status": "success"})

    
from .models import AddProject, ProjectLeadsModel

def project_leads_page(request, project_id):
    project = get_object_or_404(AddProject, id=project_id)

    # Latest leads first
    leads_qs = ProjectLeadsModel.objects.filter(
        project=project
    ).select_related('leadFrom').order_by('-created_at')

    # Remove duplicates (keep latest per user)
    unique_users = {}

    for lead in leads_qs:
        if lead.leadFrom and lead.leadFrom.id not in unique_users:
            unique_users[lead.leadFrom.id] = lead

    # Final list
    leads = list(unique_users.values())

    return render(request, "project_leads.html", {
        "project": project,
        "leads": leads,
    })


from .forms import ReelsForm
from .models import AddPropertyModel
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def reels_upload(request):
    if request.user.role in ["OWNER", "FRANCHISE", "REGISTER"]:
        messages.error(request, "You are not authorized to post reels.")
        return redirect('prop:home')
        
    user = request.user

    # ✅ ONLY LOGGED-IN USER PROPERTIES
    properties = AddPropertyModel.objects.filter(user=user)

    if request.method == "POST":
        form = ReelsForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.user = user

            # ✅ Get selected property
            property_id = request.POST.get("propertyId")

            if property_id:
                reel.linked_property_id = property_id

            reel.save()
            return redirect("prop:home")
    else:
        form = ReelsForm()

    return render(request, "reels_upload.html", {
        "f": form,
        "properties": properties
    })

import random 
def get_reel(req):
    clicked_id = req.GET.get("reel")
    # Exclude reels with no uploaded file to avoid ValueError on .url access
    reels = list(Reels.objects.exclude(reel='').exclude(reel__isnull=True))
    random.shuffle(reels) 
    # If user clicked a specific reel, move that reel to the first position
    if clicked_id:
        clicked_id = int(clicked_id)
        reels.sort(key=lambda r: 0 if r.id == clicked_id else 1)
  
    return render(req,'reelViewer.html',{'data':reels})
    
def like_reel(req, id):
    reel = Reels.objects.get(id=id)

    # Get liked reels list from session
    liked_reels = req.session.get("liked_reels", [])

    if id in liked_reels:
        # UNLIKE
        reel.likeCount -= 1
        liked_reels.remove(id)
        liked = False
    else:
        # LIKE
        reel.likeCount += 1
        liked_reels.append(id)
        liked = True

    # Save back to session
    req.session["liked_reels"] = liked_reels

    reel.save()

    return JsonResponse({
        "status": "success",
        "liked": liked,
        "likes": reel.likeCount
    })

 
from .models import Reels, Comment

@login_required
def comment_reel(req, id, comment):
    reel = Reels.objects.get(id=id)
    # Create the comment
    new_comment = Comment.objects.create(
        user=req.user,
        reel=reel,
        comment=comment
    )
    
    # Get updated comment count
    comment_count = reel.comment_set.count()
    
    # Prepare comments JSON for frontend
    def __str__(self):
        return f"{self.user.username} - {self.title}"

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications.html", {"notifications": notifications})
    comments_data = [
        {"user": c.user.username, "text": c.comment}
        for c in reel.comment_set.all()
    ]
    
    return JsonResponse({
        "status": "success",
        "commentCount": comment_count,
        "comments": comments_data
    })
def getAllComments(request, id):
    try:
        reel = Reels.objects.get(id=id)
        # Select only the fields needed and convert to list
        comments = Comment.objects.filter(reel=reel).values(
            'id', 'comment', 'user__username', 'created_at'
        )
        comments_list = list(comments)  # ✅ Convert QuerySet to list
        return JsonResponse({"status": "success", "comments": comments_list}, safe=False)
    except Reels.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Reel not found"}, status=404)




# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Reels
import json

@login_required
def reel_viewer(request):
    user = request.user
    # Get reels for this user, excluding empty ones
    reels_qs = Reels.objects.filter(user=user).exclude(reel='').exclude(reel__isnull=True).order_by('-id').prefetch_related('comment_set')

    # Prepare reels with comments as JSON
    reels = []
    for r in reels_qs:
        comments_data = [
            {"user": c.user.username, "text": c.comment}
            for c in r.comment_set.all()
        ]
        reels.append({
            "id": r.id,
            "reel_url": r.reel.url,
            "description": r.description or "",
            "link": r.link or "",
            "likeCount": r.likeCount,
            "view_count": r.view_count or 0, 
            "commentCount": r.comment_set.count(),
            "comments_json": json.dumps(comments_data)   
        })

    # Render template
    return render(request, "all_reels.html", {"reel": reels})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Reels
from .forms import ReelsForm

@login_required
def edit_reel(request, id):
    reel = get_object_or_404(Reels, id=id, user=request.user)
    if request.method == "POST":
        form = ReelsForm(request.POST, request.FILES, instance=reel)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True})
            return redirect('all_reels')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = ReelsForm(instance=reel)
    return render(request, 'edit_reel.html', {'form': form, 'reel': reel})


# Unified delete_reel above

from django.views.decorators.http import require_POST
@login_required
@require_POST
def register_reel_view(request, reel_id):
    try:
        reel = Reels.objects.get(id=reel_id)
        if request.user not in reel.viewers.all():
            reel.viewers.add(request.user)
            reel.view_count = reel.viewers.count()  # or reel.view_count += 1
            reel.save()
        return JsonResponse({'status': 'success', 'view_count': reel.view_count})
    except Reels.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Reel not found'}, status=404)
        
from django.urls import reverse
from urllib.parse import urlencode

def search(req):
    # If it's a GET request → show the search box page
    if req.method == "GET":
        return render(req, "search_box.html")

    # If it's POST → process search
    cat = req.POST.get('search-cat') or "All"
    btn = (req.POST.get('search-input') or "").strip()
    
    query = {}
    if btn:
        query['location'] = btn

    prop = cat if cat else "All"

    url = reverse('prop:property_list', args=[prop])
    if query:
        url = f"{url}?{urlencode(query)}"

    return redirect(url)




def terms_and_conditions(request):
    return render(request, "terms.html")



from django.contrib.auth import get_user_model



def forget_password(request):
    return render(request, "forget_password.html")
    
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def reset_password(request):
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "reset_password.html")

        # Get user ID stored after OTP verification
        user_id = request.session.get("reset_user_id")

        if not user_id:
            messages.error(request, "Session expired. Please try again.")
            return redirect("forgetPass")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("forgetPass")

        # Update password
        user.password = make_password(password1)
        user.save()

        # Clear session key
        if "reset_user_id" in request.session:
            del request.session["reset_user_id"]

        messages.success(request, "Password updated successfully. Please login.")
        return redirect("prop:login")  # Update with your login route name

    return render(request, "reset_password.html")




User = get_user_model()
otp_pass_storage = {}

@csrf_exempt
def send_otp_pass(request):
    value = request.GET.get("value")  # phone/email/username

    if not value:
        return JsonResponse({"error": "Input required"}, status=400)

    user = None

    if value.isdigit():
        user = User.objects.filter(phone=value).first()

    if not user:
        user = User.objects.filter(email=value).first()

    if not user:
        user = User.objects.filter(username=value).first()

    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    phone = user.phone
    if not phone:
        return JsonResponse({"error": "User has no phone number"}, status=400)

    otp = "%06d" % random.randint(0, 999999)

    otp_pass_storage[phone] = {
        "otp": otp,
        "timestamp": time.time(),
        "user_id": user.id
    }

    # 🔥 USE SAME APPROVED TEMPLATE MESSAGE
    message = (
        f"Your OTP for verification with Weekdays Properties is {otp}. "
        "Please do not share this code with anyone. It is valid for 10 minutes."
    )

    params = {
        "APIKey": API_KEY,
        "senderid": SENDER_ID,
        "channel": "Trans",
        "DCS": 0,
        "flashsms": 0,
        "number": "91" + phone,
        "text": message,
        "DLTTemplateId": TEMPLATE_ID,  # same template ID
        "route": "0",
        "PEId": PE_ID
    }

    response = requests.get(SMS_URL, params=params)

    print("Password Reset OTP SEND RESPONSE:", response.text)

    return JsonResponse({
        "message": "OTP Sent",
        "phone": phone,
        "status": response.status_code
    })

@csrf_exempt
def verify_otp_pass(request):
    phone = request.GET.get("phone")
    otp = request.GET.get("otp")

    if not phone or not otp:
        return JsonResponse({"error": "Phone and OTP required"}, status=400)

    data = otp_pass_storage.get(phone)

    if not data:
        return JsonResponse({"error": "OTP expired or not sent"}, status=400)

    if time.time() - data["timestamp"] > 600:
        otp_pass_storage.pop(phone)
        return JsonResponse({"error": "OTP expired"}, status=400)

    if otp != data["otp"]:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    request.session["reset_user_id"] = data["user_id"]

    otp_pass_storage.pop(phone)

    return JsonResponse({"message": "OTP Verified"})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import AddPropertyModel  # change to your model name

 
def delete_property(request, id):
    if request.method == "POST":
        obj = get_object_or_404(AddPropertyModel, id=id)
        obj.delete()
        return JsonResponse({"status": "success"})  
    return JsonResponse({"status": "error"}, status=400)




def make_sold(request, id):
    if request.method == "POST":
        obj = get_object_or_404(AddPropertyModel, id=id)

        if obj.is_notSold:
            return JsonResponse({"message": "Property already sold"})

        obj.is_notSold = True
        obj.save()
        return JsonResponse({"message": "Property marked as SOLD"})

    return JsonResponse({"message": "Invalid request"}, status=400)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def profilelead_view(req,id):
    leadFrom=req.user
    leadTo=User.objects.get(id=id)
    ProfileLeadsModel.objects.create(
        leadFrom=leadFrom,
        leadTo=leadTo
        
    )
    return JsonResponse({"message":"lead Added"})
@csrf_exempt
def propertlead_view(req,id,propId):
    leadFrom=req.user
    leadTo=User.objects.get(id=id)
    property=AddPropertyModel.objects.get(id=propId)
    PropertyLeadsModel.objects.create(
        leadFrom=leadFrom,
        leadTo=leadTo,
        property=property
    )
    
    return JsonResponse({"msg":"Lead Added"})
@csrf_exempt
def projectlead_view(req,id,proId):
    leadFrom=req.user
    leadTo=User.objects.get(id=id)
    project=AddProject.objects.get(id=proId)
    ProjectLeadsModel.objects.create(
        leadFrom=leadFrom,
        leadTo=leadTo,
        project=project
    )
    
    return JsonResponse({"msg":"Lead Added"})



from django.db.models import Q, Max
from .models import ChatRoom, ChatMessage

User = get_user_model()

def get_chat_users_data(current_user):
    # Get all other users
    all_users = User.objects.exclude(id=current_user.id)
    users_data = []

    for user in all_users:
        # Only normal chats (property=None)
        chat_room = ChatRoom.objects.filter(
            (Q(user1=current_user) & Q(user2=user)) |
            (Q(user1=user) & Q(user2=current_user)),
            property=None
        ).first()

        if chat_room:
            unread_count = chat_room.messages.filter(
                sender=user,
                is_read=False
            ).count()
            last_message_time = chat_room.messages.aggregate(
                last=Max('created_at')
            )['last']
        else:
            unread_count = 0
            last_message_time = None

        users_data.append({
            'user': user,
            'unread_count': unread_count,
            'last_message_time': last_message_time,
            'plan_type': getattr(user, 'plan_type', 'all'),
        })

    # Sort: unread first, then last message time
    return sorted(
        users_data,
        key=lambda x: (
            -x['unread_count'],
            -(x['last_message_time'].timestamp() if x['last_message_time'] else 0)
        )
    )

@login_required
def all_users_to_chat(request):
    """
    Show all chat users (normal chats only), 
    exclude property chats.
    """
    users_sorted = get_chat_users_data(request.user)
    return render(request, "chat/all_chat_users.html", {
        "users_sorted": users_sorted
    })

from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def start_chat_with_user(request, user_id):

    # Prevent self chat
    if user_id == request.user.id:
        return redirect("prop:all_users_to_chat")

    other_user = get_object_or_404(User, id=user_id)

    # Always sort users (important for unique_together)
    user1, user2 = sorted([request.user, other_user], key=lambda u: u.id)

    # ✅ ALWAYS DEFINE chat
    chat = ChatRoom.objects.filter(
        user1=user1,
        user2=user2,
        property=None   # important (since you also use property chats)
    ).first()

    # If chat doesn't exist → create
    if chat is None:
        chat = ChatRoom.objects.create(user1=user1, user2=user2)

    # ✅ Mark messages as read when opening
    ChatMessage.objects.filter(
        chat=chat,
        sender=other_user,
        is_read=False
    ).update(is_read=True)

    # Handle pre message
    pre_message = request.GET.get("pre_message", "")

    if pre_message:
        url = f"{reverse('prop:chat_room', kwargs={'chat_id': chat.id})}?pre_message={pre_message}"
        return redirect(url)

    return redirect("prop:chat_room", chat_id=chat.id)
@login_required
def delete_message(request, msg_id):
    msg = get_object_or_404(ChatMessage, id=msg_id, sender=request.user)
    msg.is_deleted = True
    msg.save()
    return redirect("prop:chat_room", chat_id=msg.chat.id)

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def chat_room(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)

    if request.user not in [chat.user1, chat.user2]:
        return redirect("prop:all_users_to_chat")

    other_user = chat.user2 if request.user == chat.user1 else chat.user1
    property_obj = chat.property if hasattr(chat, 'property') else None

    # Mark messages as delivered
    ChatMessage.objects.filter(
        chat=chat,
        sender=other_user,
        is_delivered=False
    ).update(is_delivered=True)

    # Mark messages as read
    ChatMessage.objects.filter(
        chat=chat,
        sender=other_user,
        is_read=False
    ).update(is_read=True)

    # ✅ SEND MESSAGE USING AJAX
    if request.method == "POST":
        message_text = request.POST.get("message")
        if message_text:
            msg = ChatMessage.objects.create(
                chat=chat,
                sender=request.user,
                message=message_text
            )

            # Return JSON instead of redirect
            return JsonResponse({
                "message": msg.message,
                "time": msg.created_at.strftime("%I:%M %p"),
                "status": "sent"
            })

    pre_message = request.GET.get("pre_message", "")
    
    messages = chat.messages.order_by("created_at")

    # Get users list for the left sidebar
    users_sorted = get_chat_users_data(request.user)

    return render(request, "chat/chat_room.html", {
        "chat": chat,
        "messages": messages,
        "other_user": other_user,
        "property": property_obj,
        "pre_message": pre_message,
        "users_sorted": users_sorted,
    })
# Optional AJAX for notifications
@login_required
def new_messages_count(request):
    unread_count = ChatMessage.objects.filter(
        is_read=False
    ).filter(
        Q(chat__user1=request.user) | Q(chat__user2=request.user)
    ).exclude(sender=request.user).count()

    return JsonResponse({"unread_count": unread_count})



from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AddPropertyModel, ChatRoom

@login_required
def start_property_chat(request, property_id):
    prop = get_object_or_404(AddPropertyModel, id=property_id)

    # Block chat if property owner is OWNER
    if prop.user.role == "OWNER":
        messages.error(request, "Chat is disabled for this property.")
        return redirect(request.META.get("HTTP_REFERER", "prop:property_list"))

    # Buyer cannot chat on own property
    if prop.user == request.user:
        messages.error(request, "You cannot chat on your own property.")
        return redirect(request.META.get("HTTP_REFERER", "prop:property_list"))

    buyer, owner = sorted([request.user, prop.user], key=lambda u: u.id)

    chat = ChatRoom.objects.filter(
        user1=buyer,
        user2=owner,
        property=prop
    ).first()

    if not chat:
        chat = ChatRoom.objects.create(
            user1=buyer,
            user2=owner,
            property=prop
        )

    # Get pre_message from GET params
    pre_message = request.GET.get("pre_message", "")

    if pre_message:
        url = f"{reverse('prop:chat_room', kwargs={'chat_id': chat.id})}?pre_message={pre_message}"
        return redirect(url)

    return redirect("prop:chat_room", chat_id=chat.id)
    
@login_required
def owner_property_chats(request):
    chats = ChatRoom.objects.filter(
        user2=request.user  # OWNER
    ).select_related("property", "user1").order_by("-created_at")

    return render(request, "chat/owner_property_chats.html", {
        "chats": chats
    })


from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

@login_required
def select_plan(request):

    if request.method == "POST":

        user = request.user
        plan_type = request.POST.get("plan_type")
        duration = int(request.POST.get("duration", 0))

        # Plan prices (per month)
        plan_prices = {
            "COMPANY_NORMAL": 14999,
            "COMPANY_PRO": 19999,
            "PROFESSIONAL_SINGLE": 4999,
        }

        # ✅ Get monthly price
        base_price = plan_prices.get(plan_type, 0)

        # ✅ Multiply by duration
        total_price = base_price * duration

        today = timezone.now().date()

        if not user.company_subscription_end_date or user.company_subscription_end_date < today:
            start_date = today
        else:
            start_date = user.company_subscription_end_date

        expiry_date = start_date + timedelta(days=30 * duration)

        # SAVE DATA
        user.plan_type = plan_type
        user.selected_duration = duration
        user.subscription_amount = total_price   # ✅ IMPORTANT LINE
        user.company_subscription_start_date = start_date
        user.company_subscription_end_date = expiry_date

        user.save()

        return redirect("prop:company_profile")

    return redirect("prop:renew_plan")


@login_required
def renew_plan(request):

    if request.method == "POST":
        # save plan
        return redirect("prop:company_profile")

    return render(request, "renew_plan.html")
  
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render as django_render

def is_admin(user):
    return user.is_staff  # Only staff users
 

@login_required
@user_passes_test(is_admin)
def property_stats(request):

    total_properties = AddPropertyModel.objects.count()
    total_projects = AddProject.objects.count()
    total_professionals = User.objects.filter(role="PROFESSIONAL").count()
    total_contacts = User.objects.filter(is_superuser=False).count()

    total_company_normal = User.objects.filter(plan_type="COMPANY_NORMAL").count()
    total_company_pro = User.objects.filter(plan_type="COMPANY_PRO").count()
    total_company_premium = User.objects.filter(plan_type="COMPANY_PREMIUM").count()
    total_marketer_export = User.objects.filter(plan_type="MARKETER_EXPORT").count()
    total_marketer_export_pro = User.objects.filter(plan_type="MARKETER_EXPORT_PRO").count()
    total_marketer_export_premium = User.objects.filter(plan_type="MARKETER_EXPORT_PREMIUM").count()
    total_professional_single = User.objects.filter(plan_type="PROFESSIONAL_SINGLE").count() 

    total_property_leads = PropertyLeadsModel.objects.count()

    context = {
        "total_properties": total_properties,
        "total_projects": total_projects,
        "total_professionals": total_professionals,
        "total_contacts": total_contacts,
        "total_company_normal": total_company_normal,
        "total_company_pro": total_company_pro,
        "total_marketer_export": total_marketer_export,
        "total_marketer_export_pro": total_marketer_export_pro,
        "total_professional_single": total_professional_single,
        "total_property_leads": total_property_leads,
        "progress_percent": 60,
    }

    return django_render(request, "property_stats.html", context)

    # admin views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import AddProject

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import (
    AddProject,
    AddPropertyModel,
    MoveRequest,
    ContactForm,
    LoanApplication,
    FutureRequirement,
    FranchiseApplication
)

User = get_user_model()


# ===============================
# ALL PROJECTS (Admin Only)
# ===============================
@staff_member_required
def all_project(request):
    projects = AddProject.objects.all().order_by("-id")
    return render(request, "all_project.html", {"projects": projects})


# ===============================
# ALL CONTACTS (Admin Only)
# ===============================
@staff_member_required
def all_contacts(request):
    plan_type = request.GET.get('plan_type', None)

    if plan_type:
        contacts = User.objects.filter(plan_type=plan_type)
        selected_plan = plan_type.replace("_", " ").title()
    else:
        contacts = User.objects.all()
        selected_plan = None

    return render(request, "all_contacts.html", {
        "contacts": contacts,
        "selected_plan": selected_plan
    })


# ===============================
# ADMIN PROPERTIES
# ===============================
@staff_member_required
def admin_properties(request):
    properties = AddPropertyModel.objects.all().order_by("-id")

    selected_type = request.GET.get("type")
    if selected_type:
        properties = properties.filter(selectProperty=selected_type)

    property_types = AddPropertyModel.objects.values_list(
        "selectProperty", flat=True
    ).distinct()

    return render(request, "admin_properties.html", {
        "properties": properties,
        "property_types": property_types,
        "selected_type": selected_type,
    })


# ===============================
# TOGGLE VERIFY PROPERTY
# ===============================
@staff_member_required
def toggle_verify_property(request, pk):
    property_obj = get_object_or_404(AddPropertyModel, pk=pk)

    if request.method == "POST":
        property_obj.is_verified = "is_verified" in request.POST
        property_obj.verifiedBy = request.user
        property_obj.save()

    return redirect("prop:admin_properties")


# ===============================
# TOGGLE ILLEGAL PROPERTY
# ===============================
@staff_member_required
def toggle_illegal_property(request, pk):
    property = get_object_or_404(AddPropertyModel, pk=pk)

    property.is_legal_verified = not property.is_legal_verified
    property.save()

    return redirect('prop:admin_properties')


# ===============================
# ALL REQUESTS
# ===============================
@staff_member_required
def all_requests(request):
    move_requests = MoveRequest.objects.all().order_by('-created_at')
    contact_forms = ContactForm.objects.all().order_by('-submitted_at')
    loan_applications = LoanApplication.objects.all().order_by('-submitted_on')

    return render(request, "all_requests.html", {
        "move_requests": move_requests,
        "contact_forms": contact_forms,
        "loan_applications": loan_applications,
    })


# ===============================
# PROPERTY VERIFICATION LIST
# ===============================
@staff_member_required
def property_verification_list(request):

    verified_properties = AddPropertyModel.objects.filter(is_verified=True)
    not_verified_properties = AddPropertyModel.objects.filter(is_verified=False)
    illegal_properties = AddPropertyModel.objects.filter(is_legal_verified=True)

    return render(request, 'property_verification_list.html', {
        'verified_properties': verified_properties,
        'not_verified_properties': not_verified_properties,
        'illegal_properties': illegal_properties,
    })


# ===============================
# FUTURE REQUIREMENTS
# ===============================
@staff_member_required
def FutureRequire(request):
    future = FutureRequirement.objects.all()
    return render(request, "futureRequirement_list.html", {"future": future})


# ===============================
# FRANCHISE LIST
# ===============================
@staff_member_required
def franchies_list(request):
    franch = FranchiseApplication.objects.all()
    return render(request, "franchisecontact_list.html", {"franch": franch})
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect



#===============payment======================
import razorpay
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import Payment

User = get_user_model()

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)




@csrf_exempt
def create_order(request):

    if request.method == "POST":

        data = json.loads(request.body)
        plan = data.get("plan")

        PLAN_PRICES = {
            "PROFESSIONAL": 4999,
            "MARKETER_EXPERT": 4999,
            "MARKETER_EXPERT_PRO": 5999,
            "COMPANY_SILVER": 4999,
            "COMPANY_PLATINUM": 6999,
            "COMPANY_GOLD": 7999,
        }

        amount = PLAN_PRICES.get(plan)

        if not amount:
            return JsonResponse({"error": "Invalid Plan"})

        order = client.order.create({
            "amount": amount * 100,
            "currency": "INR",
            "payment_capture": 1
        })

        return JsonResponse({
            "order_id": order["id"],
            "amount": amount,
            "key": settings.RAZORPAY_KEY_ID
        })
        
        
        
        
@csrf_exempt
def verify_payment(request):

    if request.method == "POST":

        data = json.loads(request.body)

        plan = data["plan"]
        email = data["email"]

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"],
            })

            # Create user
            user = User.objects.create_user(
                username=data["username"],
                email=email,
                password=data["password"]
            )

            # Save payment
            Payment.objects.create(
                user=user,
                plan_type=plan,
                amount=data["amount"],
                razorpay_order_id=data["razorpay_order_id"],
                razorpay_payment_id=data["razorpay_payment_id"],
                razorpay_signature=data["razorpay_signature"],
                is_paid=True
            )

            return JsonResponse({"status": "success"})

        except:
            return JsonResponse({"status": "failed"})
            
def payment_success(request):
    return render(request, "payment_success.html")
    
from .models import SlideImage

 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SlideImage
@staff_member_required
def manage_slides(request):

    if request.method == "POST":

        slide_type = request.POST.get("slide_type")
        image = request.FILES.get("image")

        if slide_type and image:

            if slide_type in ["desktop", "mobile"]:
                SlideImage.objects.create(
                    image=image,
                    slide_type=slide_type
                )
                messages.success(request, "Slide uploaded successfully")
            else:
                messages.error(request, "Invalid slide type")

        else:
            messages.error(request, "Image and slide type required")

        return redirect("prop:manage_slides")



    desktop_slides = SlideImage.objects.filter(
        slide_type="desktop"
    ).order_by("-created_at")

    mobile_slides = SlideImage.objects.filter(
        slide_type="mobile"
    ).order_by("-created_at")

    context = {
        "desktop_slides": desktop_slides,
        "mobile_slides": mobile_slides
    }

    return render(request, "change_slides.html", context)
from django.shortcuts import get_object_or_404

@staff_member_required
def delete_slide(request, id):

    slide = get_object_or_404(SlideImage, id=id)

    if slide.image:
        slide.image.delete(save=False)

    slide.delete()

    return redirect("prop:manage_slides")
    
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import AddPropertyModel


@staff_member_required
def owner_properties(request):

    properties = AddPropertyModel.objects.filter(
        user__role="OWNER"   # must match exactly what is stored
    ).order_by("-id")

    return render(request, "admin_owner_properties.html", {
        "properties": properties
    }) 
    
@staff_member_required
def toggle_rera_property(request, pk):
    property = get_object_or_404(AddPropertyModel, pk=pk)
    property.reraApproved = not property.reraApproved 
    property.save()
    return redirect('prop:admin_properties')   # safer than HTTP_REFERER
    
    
    
    
from django.shortcuts import render


def careers(request):
    return render(request, 'prop:careers.html')


def about_us(request):
    return render(request, 'about.html')



def terms(request):
    return render(request, 'terms.html')

def help_view(request):
    return render(request, 'help.html')

def refund_policy(request):
    return render(request, 'refund_policy.html')

def disclaimer(request):
    return render(request, 'disclaimer.html')


def privacy_policy(request):
    return render(request, 'privacy-policy.html')


def contact(request):
    return render(request, 'contact.html')


def unsubscribe(request):
    return render(request, 'unsubscribe.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PostFeed, ImagePost
from .forms import PostFeedForm, ImagePostForm


# =========================
# IMAGE STORIES (CRUD)
# =========================

@login_required
def news_list(request):
    posts = ImagePost.objects.all().order_by('-created_at')
    return render(request, 'news_list.html', {'posts': posts})


@login_required
def news_create(request):
    if request.user.role in ["FRANCHISE", "REGISTER"]:
        messages.error(request, "You are not authorized to post news.")
        return redirect('prop:home')
        
    if request.method == 'POST':
        heading = request.POST.get('heading', '').strip()
        news_content = request.POST.get('news_content', '').strip()
        media_file = request.FILES.get('media_file')

        if heading or news_content or media_file:
            post = ImagePost(user=request.user, heading=heading, news_content=news_content)

            if media_file:
                content_type = media_file.content_type
                if content_type.startswith('image'):
                    post.media_type = 'image'
                    post.image = media_file
                elif content_type.startswith('video'):
                    post.media_type = 'video'
                    post.video = media_file
            else:
                # ImagePost model only has 'image' and 'video' types, 
                # but we can default to 'image' for text-only if needed,
                # though usually stories are visual.
                post.media_type = 'image' 

            post.save()
            messages.success(request, 'Update posted successfully!')
            return redirect('prop:home')
        else:
            messages.error(request, 'Please add a heading or description.')

    return render(request, 'news_form.html', {})


@login_required
def news_edit(request, pk):
    post = get_object_or_404(ImagePost, pk=pk)
    if post.user and post.user != request.user:
        return redirect('prop:home')

    if request.method == 'POST':
        form = ImagePostForm(request.POST, instance=post)
        media_file = request.FILES.get('media_file')
        
        if form.is_valid():
            edited_post = form.save(commit=False)
            if media_file:
                content_type = media_file.content_type
                if content_type.startswith('image'):
                    edited_post.media_type = 'image'
                    edited_post.image = media_file
                    edited_post.video = None
                elif content_type.startswith('video'):
                    edited_post.media_type = 'video'
                    edited_post.video = media_file
                    edited_post.image = None
            edited_post.save()
            return redirect('prop:home')
    else:
        form = ImagePostForm(instance=post)
    return render(request, 'news_form.html', {'form': form})


@login_required
def news_delete(request, pk):
    post = get_object_or_404(ImagePost, pk=pk)

    if post.user == request.user:
        post.delete()

    return redirect('prop:home')


@login_required
def news_detail(request, pk):
    post = get_object_or_404(ImagePost, pk=pk)
    return render(request, 'news_detail.html', {'post': post})


# =========================
# FEED POST
# =========================

@login_required
def feed_list_old(request):
    feeds = PostFeed.objects.all().order_by('-created_at')
    return render(request, 'feed_list_old.html', {'feeds': feeds})

@login_required
def feed_create_old(request):
    form = PostFeedForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        feed = form.save(commit=False)
        feed.user = request.user
        feed.save()
        return redirect('prop:feed_list_old')
    return render(request, 'feed_form_old.html', {'form': form})


@login_required
def feed_edit(request, pk):
    feed = get_object_or_404(PostFeed, pk=pk)

    if feed.user and feed.user != request.user:
        return redirect('prop:feed_list')

    form = PostFeedForm(request.POST or None, request.FILES or None, instance=feed)

    if form.is_valid():
        form.save()
        return redirect('prop:feed_list')

    return render(request, 'feed_form.html', {'form': form})


@login_required
def feed_delete(request, pk):
    feed = get_object_or_404(PostFeed, pk=pk)

    if feed.user == request.user:
        feed.delete()

    return redirect('prop:feed_list')




# =========================
# PROFILE PAGE
# =========================

@login_required
def profile_pagess(request):
    return render(request, 'profile_menu.html')

# =========================
# NEWSPOS FEED
# =========================

@login_required
def feed_list(request):
    posts = NewsPost.objects.all().order_by('-created_at')
    return render(request, 'feed_list.html', {'posts': posts})

@login_required
def feed_create(request):
    if request.user.role in ["FRANCHISE", "REGISTER"]:
        messages.error(request, "You are not authorized to post feeds.")
        return redirect('prop:home')
        
    if request.method == 'POST':
        form = NewsPostForm(request.POST)
        media_file = request.FILES.get('media_file')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            
            # Optional Keyword Validation - Disabled to ensure 'working' state
            # news_content = post.news_content.lower()
            # allowed_keywords = NewsKeyword.objects.values_list('keyword', flat=True)
            # allowed_keywords = [k.lower() for k in allowed_keywords]
            # match_found = False
            # for kw in allowed_keywords:
            #     if kw in news_content:
            #         match_found = True
            #         break
            # if not match_found:
            #     messages.error(request, "Your post does not contain any allowed keywords.")
            #     keywords = NewsKeyword.objects.all()
            #     return render(request, 'feed_form.html', {'form': form, 'keywords': keywords})

            if media_file:
                content_type = media_file.content_type
                if content_type.startswith('image'):
                    post.media_type = 'image'
                    post.image = media_file
                elif content_type.startswith('video'):
                    post.media_type = 'video'
                    post.video = media_file
            else:
                post.media_type = 'text'
            
            post.save()
            messages.success(request, "News posted successfully!")
            return redirect('prop:feed_list')
    else:
        form = NewsPostForm()
    
    keywords = NewsKeyword.objects.all()
    return render(request, 'feed_form.html', {'form': form, 'keywords': keywords})

@login_required
def feed_detail(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    return render(request, 'feed_detail.html', {'post': post})

@login_required
def feed_edit(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('prop:feed_list')

    if request.method == 'POST':
        form = NewsPostForm(request.POST, instance=post)
        media_file = request.FILES.get('media_file')
        if form.is_valid():
            updated_post = form.save(commit=False)
            
            # Keyword Validation
            news_content = updated_post.news_content.lower()
            allowed_keywords = NewsKeyword.objects.values_list('keyword', flat=True)
            allowed_keywords = [k.lower() for k in allowed_keywords]
            
            match_found = False
            for kw in allowed_keywords:
                if kw in news_content:
                    match_found = True
                    break
            
            if not match_found:
                messages.error(request, "Update rejected: Your content does not contain any allowed keywords.")
                keywords = NewsKeyword.objects.all()
                return render(request, 'feed_form.html', {'form': form, 'post': post, 'keywords': keywords})

            if media_file:
                content_type = media_file.content_type
                if content_type.startswith('image'):
                    updated_post.media_type = 'image'
                    updated_post.image = media_file
                elif content_type.startswith('video'):
                    updated_post.media_type = 'video'
                    updated_post.video = media_file
            
            updated_post.save()
            messages.success(request, "News updated successfully!")
            return redirect('prop:feed_list')
    else:
        form = NewsPostForm(instance=post)
    
    keywords = NewsKeyword.objects.all()
    return render(request, 'feed_form.html', {'form': form, 'post': post, 'keywords': keywords})

@login_required
def feed_delete(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    if post.user == request.user:
        post.delete()
        messages.success(request, "News post deleted.")
    else:
        messages.error(request, "Not authorized.")
    return redirect('prop:feed_list')
@login_required
def poll_create(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        if question:
            poll = Poll.objects.create(user=request.user, question=question)
            for i in range(1, 6):
                option_text = request.POST.get('option_' + str(i))
                if option_text:
                    PollOption.objects.create(poll=poll, option_text=option_text)
            messages.success(request, 'Poll created successfully!')
    return redirect(request.META.get('HTTP_REFERER', 'prop:profile'))


@login_required
def poll_vote(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    if request.method == 'POST':
        option_id = request.POST.get('option')
        if option_id:
            option = get_object_or_404(PollOption, pk=option_id, poll=poll)
            if PollVote.objects.filter(user=request.user, poll=poll).exists():
                messages.warning(request, 'You have already voted on this poll.')
            else:
                PollVote.objects.create(user=request.user, poll=poll, option=option)
                messages.success(request, 'Your vote has been recorded.')
        else:
            messages.error(request, 'Please select an option.')
    return redirect(request.META.get('HTTP_REFERER', 'prop:profile'))

@login_required
def poll_delete(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    if poll.user == request.user:
        poll.delete()
        messages.success(request, 'Poll deleted.')
    else:
        messages.error(request, 'Not authorized.')
    return redirect(request.META.get('HTTP_REFERER', 'prop:profile'))


@login_required
def check_property_details(request, property_id):
    prop = get_object_or_404(AddPropertyModel, id=property_id, user=request.user)
    
    # Get the verification data from franchise
    verification = FranchiseProperty.objects.filter(property=prop).order_by('-created_at').first()
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "confirm":
            prop.is_verifiedproperty = True
            prop.is_verified = True
            prop.save()
            messages.success(request, f"Property '{prop.projectName}' has been successfully verified!")
            return redirect('prop:profile')
            
        elif action == "reverify":
            reason = request.POST.get('reason')
            if verification:
                verification.owner_feedback = reason
                verification.save()
            
            # Reset verification status so it goes back to "Not Verified" / "Needs Verification"
            prop.is_verified = False
            prop.is_verifiedproperty = False
            prop.save()
            
            messages.info(request, "Re-verification request submitted successfully.")
            return redirect('prop:profile')

    return render(request, 'property_check_details.html', {
        'prop': prop,
        'verification': verification
    })

@login_required
def settings_view(request):
    user = request.user
    return render(request, 'settings.html', {'profile': user})

@login_required
def notifications_list(request):
    notifications_qs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    # Store in a list so we can render them before they are marked as read
    notifications = list(notifications_qs)
    notifications_qs.update(is_read=True)
    return render(request, "notifications.html", {"notifications": notifications})

@login_required
@csrf_exempt
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@csrf_exempt
@login_required
def mark_story_seen(request, post_id):
    if request.method == "POST":
        try:
            post = ImagePost.objects.get(id=post_id)
            StorySeen.objects.get_or_create(user=request.user, post=post)
            return JsonResponse({"success": True})
        except ImagePost.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)
