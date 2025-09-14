# prediction/forms.py
from django import forms
from .models import Article, PreventionTip, CustomUser

class ArticleForm(forms.ModelForm):
    # Make 'is_published' not required in the form itself,
    # as we handle draft/publish via button logic and hidden input
    is_published = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded'}))

    class Meta:
        model = Article
        fields = ['title', 'category', 'image', 'excerpt', 'content', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500', 'placeholder': 'Enter article title'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100'}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500', 'placeholder': 'Brief summary of the article (max 255 characters)', 'maxlength': '255'}),
            'content': forms.Textarea(attrs={'rows': 8, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500', 'placeholder': 'Write your article content here...'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500', 'placeholder': 'heart disease, prevention, exercise (comma separated)'}),
            # 'is_published' widget defined above
        }
        help_texts = {
            'image': 'Optional. Recommended size: 1200x800 pixels. Max size: 5MB.',
            'excerpt': 'Optional. A short summary shown in list views.',
            'content': 'You can use Markdown for formatting.',
            'tags': 'Optional. Helps categorize and find articles.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make optional fields not required by the form validation
        self.fields['image'].required = False
        self.fields['excerpt'].required = False
        self.fields['tags'].required = False


class PreventionTipForm(forms.ModelForm):
    # Make 'is_published' not required in the form itself
    is_published = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded'}))

    class Meta:
        model = PreventionTip
        fields = ['title', 'category', 'icon', 'content', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500', 'placeholder': 'Enter tip title (e.g., Reduce Salt Intake)', 'maxlength': '100'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500'}),
            'icon': forms.Select(choices=[ # Provide choices for icons directly or query dynamically
                ('', 'Select an icon (Optional)'),
                ('lightbulb', 'Lightbulb'),
                ('heartbeat', 'Heartbeat'),
                ('apple-alt', 'Apple'),
                ('person-running', 'Running'),
                ('pills', 'Pills'),
                ('bed', 'Bed (Sleep)'),
                ('ban-smoking', 'No Smoking'),
                ('glass-water', 'Water'),
                ('weight-scale', 'Scale (Weight)'),
                ('brain', 'Brain (Stress)'),
                ('calendar-check', 'Calendar (Checkup)'),
             ], attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500', 'placeholder': 'Write your concise health tip here (max 255 characters)', 'maxlength': '255'}),
            # 'is_published' widget defined above
        }
        help_texts = {
            'icon': "Select a relevant icon name (e.g., 'heartbeat').",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].required = False # Icon is optional