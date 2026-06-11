from django import forms
from django.conf import settings


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Your name", "class": "contact-input", "required": True}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Your email", "class": "contact-input", "required": True}),
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Subject", "class": "contact-input", "required": True}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Your message", "class": "contact-textarea", "required": True, "rows": 5}),
    )

    def send_email(self):
        name = self.cleaned_data["name"]
        email = self.cleaned_data["email"]
        subject = self.cleaned_data["subject"]
        message = self.cleaned_data["message"]
        full_message = f"From: {name} <{email}>\n\n{message}"
        from django.core.mail import EmailMessage
        msg = EmailMessage(
            subject=f"[Chhohreivung Contact] {subject}",
            body=full_message,
            from_email=email,
            to=[settings.CONTACT_EMAIL],
            reply_to=[email],
        )
        msg.send(fail_silently=False)


from ckeditor.widgets import CKEditorWidget


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        from .models import Article
        model = Article
        fields = [
            "title", "slug", "excerpt", "content", "featured_image",
            "category", "tags", "status", "featured", "published_at",
            "meta_title", "meta_description", "meta_keywords",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "writer-title-input", "placeholder": "Enter article title..."}),
            "excerpt": forms.Textarea(attrs={"class": "writer-excerpt-input", "placeholder": "Write a compelling excerpt...", "rows": 2}),
            "slug": forms.HiddenInput(),
            "category": forms.Select(attrs={"class": "writer-input"}),
            "tags": forms.CheckboxSelectMultiple(attrs={"class": "writer-tag-checkbox"}),
            "featured_image": forms.FileInput(attrs={"class": "writer-hidden-field"}),
            "featured": forms.CheckboxInput(attrs={"class": "writer-hidden-field"}),
            "meta_title": forms.TextInput(attrs={"class": "writer-input", "placeholder": "SEO title"}),
            "meta_description": forms.Textarea(attrs={"class": "writer-textarea", "placeholder": "SEO description", "rows": 2}),
            "meta_keywords": forms.TextInput(attrs={"class": "writer-input", "placeholder": "keyword1, keyword2"}),
            "status": forms.HiddenInput(),
        }


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search articles...",
                "class": "search-input",
                "aria-label": "Search",
            }
        ),
    )
