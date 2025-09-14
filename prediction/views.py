from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CustomUser, Article, PreventionTip
from prediction.ml_model import MODEL, MODEL_FEATURES, prepare_user_input, predict, get_risk_label
from django.utils import timezone
from django.http import HttpRequest, HttpResponse, JsonResponse, Http404
import traceback
from .forms import ArticleForm, PreventionTipForm
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from datetime import timedelta,date
import json
from django.forms.models import model_to_dict


def is_doctor(user):
    return user.is_authenticated and user.is_staff

def is_superuser_check(user): 
    return user.is_authenticated and user.is_superuser

def get_assessment_details(prediction_code, probability_value):
    risk_level = get_risk_label(probability_value) 

    predicted_condition = "Yes" if prediction_code == 1 else "No"

    return {
        "predicted_condition_code": prediction_code, 
        "predicted_condition_text": predicted_condition,
        "probability_percent": f"{probability_value * 100:.2f}%",
        "risk_level": risk_level, 
        "advice": f"Based on the model, your predicted risk of heart disease is {risk_level.lower()} ({predicted_condition}, probability: {probability_value * 100:.2f}%). Please consult a healthcare professional for medical advice."
    }

def home(request: HttpRequest) -> HttpResponse:
    context = {}
    last_result_details = None

    if request.user.is_authenticated:
        if request.user.last_assessment_timestamp is not None:
            try:
                prediction = request.user.last_assessment_prediction
                probability = request.user.last_assessment_probability
                if prediction is not None and probability is not None:
                    last_result_details = get_assessment_details(prediction, probability)
                    last_result_details['timestamp'] = request.user.last_assessment_timestamp
                else:
                    print(f"Warning: User {request.user.email} has timestamp but missing prediction/probability.")
            except Exception as e:
                print(f"Error retrieving last assessment details for {request.user.email}: {e}")

    latest_articles = Article.objects.filter(is_published=True).order_by('-created_at')[:3]
    random_tips = PreventionTip.objects.filter(is_published=True).order_by('?')[:3]

    context['last_result_details'] = last_result_details
    context['latest_articles'] = latest_articles
    context['random_tips'] = random_tips

    return render(request, 'prediction/index.html', context)

def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'prediction/about.html')

def prevention(request: HttpRequest) -> HttpResponse:
    context = {
        'title': 'Heart Disease Prevention - HeartGuard'
    }
    return render(request, 'prediction/prevention.html', context)

def risk(request: HttpRequest) -> HttpResponse:
    return render(request, 'prediction/risk.html')

def articles_public_list(request: HttpRequest) -> HttpResponse:
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    context = {'articles': articles}
    return render(request, 'prediction/articles_public_list.html', context)

def article_detail(request: HttpRequest, pk: int) -> HttpResponse:
    article = get_object_or_404(Article, pk=pk, is_published=True)
    context = {'article': article}
    return render(request, 'prediction/article_detail.html', context)



def loginview(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
         if request.user.is_superuser: 
             return redirect('prediction:admin_dashboard')
         elif request.user.is_staff:
            return redirect('prediction:doctor_dashboard')
         else:
            return redirect('prediction:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'prediction/login.html', {'email': email})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.name or user.email}!")

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                elif user.is_superuser: # Redirect superuser to admin_dashboard
                    return redirect('prediction:admin_dashboard')
                elif user.is_staff:
                    return redirect('prediction:doctor_dashboard')
                else:
                    return redirect('prediction:home')
            else:
                messages.error(request, 'This account is inactive. Please contact support.')
                return render(request, 'prediction/login.html', {'email': email})
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
            return render(request, 'prediction/login.html', {'email': email})

    return render(request, 'prediction/login.html')


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated: # Prevent authenticated users from accessing signup
        return redirect('prediction:home')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm-password', '')
        role = request.POST.get('role') # 'user' or 'doctor'

        errors = {}
        if not name: errors['name'] = 'Name is required.'
        if not email: errors['email'] = 'Email is required.'
        elif '@' not in email or '.' not in email.split('@')[-1]: errors['email'] = 'Enter a valid email address.'
        elif CustomUser.objects.filter(email=email).exists(): errors['email'] = 'An account with this email already exists.'
        if not password: errors['password'] = 'Password is required.'
        elif len(password) < 8: errors['password'] = 'Password must be at least 8 characters long.'
        elif password != confirm: errors['confirm-password'] = 'Passwords do not match.'
        if not role: errors['role'] = 'Please select a role.'
        elif role not in ['user', 'doctor']: errors['role'] = 'Invalid role selected.'

        context = { 'errors': errors, 'name': name, 'email': email, 'selected_role': role, }

        if errors:
            for field, msg in errors.items():
                messages.error(request, msg)
            return render(request, 'prediction/signup.html', context)

        try:
            is_staff = (role == 'doctor')
            user = CustomUser.objects.create_user(
                email=email,
                name=name,
                password=password,
                is_staff=is_staff,
                is_superuser=False 
            )
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('prediction:login')

        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            traceback.print_exc()
            context['errors']['_general_'] = 'An unexpected error occurred. Please try again.'
            return render(request, 'prediction/signup.html', context)

    return render(request, 'prediction/signup.html', {})


@login_required(login_url='prediction:login')
def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        user_identifier = request.user.name or request.user.email
        logout(request)
        messages.success(request, f"You have been logged out successfully. Goodbye, {user_identifier}!")
        return redirect('prediction:home')
    else:
        messages.warning(request, "Logout should be done via the button (POST request).")
        return redirect('prediction:home')


def assessment(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return render(request, 'prediction/assessment.html', {'results': None, 'form_data': None})

    elif request.method == 'POST':
        # Check if the model loaded correctly at startup
        if MODEL is None or not MODEL_FEATURES:
            return JsonResponse({'success': False, 'error': "The prediction service is currently unavailable. Please try again later."}, status=503)

        expected_fields = [
            'BMI', 'Smoking', 'AlcoholDrinking', 'Stroke', 'PhysicalHealth',
            'MentalHealth', 'DiffWalking', 'Sex', 'AgeCategory', 'Race',
            'Diabetic', 'PhysicalActivity', 'GenHealth', 'SleepTime', 'Asthma',
            'KidneyDisease', 'SkinCancer'
        ]
        form_data = {field: request.POST.get(field) for field in expected_fields}

        try:
            missing = [f for f in expected_fields if not form_data.get(f)]
            if missing:
                return JsonResponse({'success': False, 'error': f"Missing fields: {', '.join(missing)}"}, status=400)
            
            try:
                form_data['BMI'] = float(form_data['BMI'])
                form_data['SleepTime'] = int(form_data['SleepTime'])
                form_data['PhysicalHealth'] = int(form_data['PhysicalHealth'])
                form_data['MentalHealth'] = int(form_data['MentalHealth'])
            except (TypeError, ValueError) as e:
                return JsonResponse({'success': False, 'error': f"Invalid number format: {e}"}, status=400)

            errors = []
            if not (10 <= form_data['BMI'] <= 100): errors.append("BMI value out of range (10–100).")
            if errors:
                return JsonResponse({'success': False, 'error': " ".join(errors)}, status=400)

            input_df = prepare_user_input(form_data)
            prediction_code, probability_array = predict(input_df)

            probability_of_high_risk = float(probability_array[1])
            
            risk_level_text = get_risk_label(probability_of_high_risk) 

            recommendations = []
            if probability_of_high_risk >= 0.5:
                recommendations.append({'title': 'Consult Your Doctor', 'text': 'Schedule an appointment with your doctor to discuss these results.'})
            else:
                recommendations.append({'title': 'Maintain Healthy Habits', 'text': 'Continue your healthy lifestyle choices.'})
            if form_data.get('PhysicalActivity') == 'No':
                recommendations.append({'title': 'Increase Physical Activity', 'text': 'Aim for at least 150 minutes of moderate activity per week.'})

            results_details = {
                'predicted_condition_text': risk_level_text, 
                'predicted_label': int(prediction_code),
                'probability_of_predicted_class': float(probability_array[prediction_code]),
                'probability_of_high_risk': probability_of_high_risk,
                'recommendations': recommendations
            }

            print(results_details)

            db_save_message = "Log in to save your results."
            if request.user.is_authenticated:
                user = request.user
                user.last_assessment_prediction = int(prediction_code)
                user.last_assessment_probability = probability_of_high_risk
                user.last_assessment_timestamp = timezone.now()
                user.save(update_fields=['last_assessment_prediction', 'last_assessment_probability', 'last_assessment_timestamp'])
                
                db_save_message = "Assessment saved!"

            return JsonResponse({'success': True, 'results': results_details, 'db_message': db_save_message})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f"Unexpected server error: {str(e)}"}, status=500)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)


@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def doctor_dashboard(request: HttpRequest) -> HttpResponse:
    doctor = request.user
    articles_count = Article.objects.filter(author=doctor).count()
    tips_count = PreventionTip.objects.filter(author=doctor).count()
    last_article = Article.objects.filter(author=doctor, is_published=True).order_by('-created_at').first()
    last_article_days = None
    if last_article:
        delta = timezone.now() - last_article.created_at
        last_article_days = delta.days

    recent_articles = Article.objects.filter(author=doctor).order_by('-updated_at')[:5]
    recent_tips = PreventionTip.objects.filter(author=doctor).order_by('-updated_at')[:3]

    context = {
        'articles_count': articles_count,
        'tips_count': tips_count,
        'last_article_days': last_article_days,
        'recent_articles': recent_articles,
        'recent_tips': recent_tips,
        'total_patients': 0,
        'high_risk_patients': 0,
        'new_patients_percent': 0,
        'high_risk_percent': 0,
    }
    return render(request, 'prediction/doctor/dashboard.html', context)

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def article_list(request: HttpRequest) -> HttpResponse:
    if request.user.is_superuser:
         articles = Article.objects.all().order_by('-updated_at')
    else: 
        articles = Article.objects.filter(author=request.user).order_by('-updated_at')
    return render(request, 'prediction/doctor/article_list.html', {'articles': articles})


@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def article_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            submit_action = request.POST.get('submit_action')
            article.is_published = (submit_action == 'publish' and form.cleaned_data.get('is_published', False)) or \
                                   (submit_action != 'save_draft' and form.cleaned_data.get('is_published', False))
            if submit_action == 'save_draft':
                 article.is_published = False

            article.save()
            messages.success(request, f"Article '{article.title}' {'published' if article.is_published else 'saved as draft'}.")
            return redirect('prediction:doctor_dashboard')
        else:
            error_message = "Failed to create article. Errors: " + "; ".join([f"{f}: {e[0]}" for f, e in form.errors.items()])
            messages.error(request, error_message)
            return redirect('prediction:doctor_dashboard')
    return redirect('prediction:doctor_dashboard')


@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def article_update(request: HttpRequest, pk: int) -> HttpResponse:
    article = get_object_or_404(Article, pk=pk)
    if not request.user.is_superuser and article.author != request.user:
        messages.error(request, "Permission denied to edit this article.")
        return redirect('prediction:doctor_article_list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            updated_article = form.save()
            messages.success(request, f"Article '{updated_article.title}' updated.")
            return redirect('prediction:doctor_article_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ArticleForm(instance=article)
    return render(request, 'prediction/doctor/article_form.html', {'form': form, 'article': article, 'form_title': f"Edit Article: {article.title}"})

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def article_delete(request: HttpRequest, pk: int) -> HttpResponse:
    article = get_object_or_404(Article, pk=pk)
    if not request.user.is_superuser and article.author != request.user:
        messages.error(request, "Permission denied.")
        return redirect('prediction:doctor_article_list')
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f"Article '{title}' deleted.")
        return redirect('prediction:doctor_article_list')
    return render(request, 'prediction/doctor/article_confirm_delete.html', {'article': article})

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def tip_list(request: HttpRequest) -> HttpResponse:
    if request.user.is_superuser:
        tips = PreventionTip.objects.all().order_by('category', 'title')
    else:
        tips = PreventionTip.objects.filter(author=request.user).order_by('category', 'title')
    return render(request, 'prediction/doctor/tip_list.html', {'tips': tips})

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def tip_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PreventionTipForm(request.POST)
        if form.is_valid():
            tip = form.save(commit=False)
            tip.author = request.user
            tip.is_published = form.cleaned_data.get('is_published', True)
            tip.save()
            messages.success(request, f"Health Tip '{tip.title}' created.")
            return redirect('prediction:doctor_dashboard')
        else:
            error_message = "Failed to create tip. Errors: " + "; ".join([f"{f}: {e[0]}" for f, e in form.errors.items()])
            messages.error(request, error_message)
            return redirect('prediction:doctor_dashboard')
    return redirect('prediction:doctor_dashboard')

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def tip_update(request: HttpRequest, pk: int) -> HttpResponse:
    tip = get_object_or_404(PreventionTip, pk=pk)
    if not request.user.is_superuser and tip.author != request.user:
        messages.error(request, "Permission denied.")
        return redirect('prediction:doctor_tip_list')
    if request.method == 'POST':
        form = PreventionTipForm(request.POST, instance=tip)
        if form.is_valid():
            updated_tip = form.save()
            messages.success(request, f"Tip '{updated_tip.title}' updated.")
            return redirect('prediction:doctor_tip_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PreventionTipForm(instance=tip)
    return render(request, 'prediction/doctor/tip_form.html', {'form': form, 'tip': tip, 'form_title': f"Edit Tip: {tip.title}"})

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def tip_delete(request: HttpRequest, pk: int) -> HttpResponse:
    tip = get_object_or_404(PreventionTip, pk=pk)
    if not request.user.is_superuser and tip.author != request.user:
        messages.error(request, "Permission denied.")
        return redirect('prediction:doctor_tip_list')
    if request.method == 'POST':
        title = tip.title
        tip.delete()
        messages.success(request, f"Tip '{title}' deleted.")
        return redirect('prediction:doctor_tip_list')
    return render(request, 'prediction/doctor/tip_confirm_delete.html', {'tip': tip})

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor, login_url='prediction:home')
def model_info(request: HttpRequest) -> HttpResponse:
    model_details = {
        'name': 'Heart Disease Risk Predictor (ML)',
        'version': '1.0.0 (Hypothetical)',
        'last_trained': '2024-01-15 (Example)',
        'accuracy': 'Approx. 85% (On validation set - Example)', 
        'status': 'Active',
        'retrain_trigger_enabled': False
    }
    context = {'model_details': model_details}
    return render(request, 'prediction/doctor/model_info.html', context)

def is_doctor_check(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser

@login_required(login_url='prediction:login')
@user_passes_test(is_doctor_check, login_url='prediction:home') 
def doctor_dashboard(request: HttpRequest) -> HttpResponse:
    
    doctor = request.user
    total_patients = CustomUser.objects.filter(is_staff=False, is_superuser=False).count()
    one_month_ago = timezone.now() - timedelta(days=30)
    new_patients_count = CustomUser.objects.filter(
        is_staff=False, is_superuser=False, date_joined__gte=one_month_ago
    ).count()
    
    previous_patients_count = total_patients - new_patients_count
    new_patients_percent = 0
    if previous_patients_count > 0:
        new_patients_percent = round((new_patients_count / previous_patients_count) * 100)
    elif total_patients > 0:
        new_patients_percent = 100 

    users_with_assessment = CustomUser.objects.filter(last_assessment_timestamp__isnull=False)
    high_risk_patients = users_with_assessment.filter(last_assessment_prediction=1).count()
    total_predictions = users_with_assessment.count()

    high_risk_percent = 0
    if total_patients > 0:
        high_risk_percent = round((high_risk_patients / total_patients) * 100)

    articles_count = Article.objects.filter(author=doctor).count()
    tips_count = PreventionTip.objects.filter(author=doctor).count()
    
    last_article = Article.objects.filter(author=doctor).order_by('-updated_at').first()
    last_article_days = "N/A"
    if last_article:
        last_article_days = (timezone.now() - last_article.updated_at).days

    recent_articles = Article.objects.filter(author=doctor).order_by('-updated_at')[:5]
    recent_tips = PreventionTip.objects.filter(author=doctor).order_by('-updated_at')[:3]
    
    all_articles_by_doctor = Article.objects.filter(author=doctor).order_by('-updated_at')
    all_tips_by_doctor = PreventionTip.objects.filter(author=doctor).order_by('-updated_at')
    
    context = {
        'total_patients': total_patients,
        'new_patients_percent': new_patients_percent,
        'high_risk_patients': high_risk_patients,
        'high_risk_percent': high_risk_percent,
        'articles_count': articles_count,
        'tips_count': tips_count,
        'last_article_days': last_article_days,
        'recent_articles': recent_articles,
        'recent_tips': recent_tips,
        'all_articles_by_doctor': all_articles_by_doctor,
        'all_tips_by_doctor': all_tips_by_doctor,
    }
    
    return render(request, 'prediction/doctor/dashboard.html', context) 




@login_required(login_url='prediction:login')
@user_passes_test(is_doctor_check, login_url='prediction:home')
def download_doctor_profile_json(request: HttpRequest):
    doctor = request.user

    articles = Article.objects.filter(author=doctor)
    article_list = [
        model_to_dict(article, exclude=['author', 'image']) 
        for article in articles
    ]

    tips = PreventionTip.objects.filter(author=doctor)
    tip_list = [
        model_to_dict(tip, exclude=['author'])
        for tip in tips
    ]

    doctor_dict = model_to_dict(doctor, exclude=['password', 'email'])
    full_data = {
        'doctor_profile': doctor_dict,
        'articles': article_list,
        'prevention_tips': tip_list,
    }

    filename = f"doctor_data_{doctor.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"

    response = JsonResponse(full_data, safe=False, json_dumps_params={'indent': 2, 'default': str})
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


    filename = f"doctor_profile_{doctor.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    response = JsonResponse(doctor_dict, safe=False, json_dumps_params={'indent': 2, 'default': str})
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# def encode_email(email: str) -> str:
#     return base64.urlsafe_b64encode(email.encode()).decode()

# def decode_email(encoded_email):
#     return base64.urlsafe_b64decode(encoded_email.encode()).decode()

# def shared_result_base64(request):
#     encoded = request.GET.get('data')
#     if not encoded:
#         return JsonResponse({'error': 'Missing encoded data'}, status=400)
#     try:
#         email = decode_email(encoded)
#     except Exception:
#         return JsonResponse({'error': 'Invalid encoded data'}, status=400)


        


# @login_required(login_url='prediction:login')
# def shared_result_view(request):
#     email = request.user
#     if not email:
#         return JsonResponse({'error': 'Email is required'}, status=400)

#     try:
#         user = CustomUser.objects.get(email=email)
#         latest_result = AssessmentResult.objects.filter(user=user).latest('timestamp')

#         data = {
#             "email": user.email,
#             "prediction": latest_result.predicted_condition_text,
#             "risk": latest_result.probability_of_high_risk,
#             "timestamp": latest_result.timestamp,
#             "raw_fields": {
#                 "bmi": latest_result.bmi,
#                 "smoking": latest_result.smoking,
#                 "diabetic": latest_result.diabetic,
#                 # ...add more as needed
#             }
#         }
#         return JsonResponse(data, status=200)

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)
#     except AssessmentResult.DoesNotExist:
#         return JsonResponse({'error': 'No assessment found'}, status=404)
    