---
name: django-views
description: When the user wants to write Django views, configure URL routing, or work with class-based views or function-based views. Use when the user says "create a view," "URL routing," "CBV," "FBV," "class-based view," "function-based view," "ListView," "DetailView," "CreateView," "UpdateView," "DeleteView," "URL conf," "urlpatterns," "path()," "view mixin," "LoginRequiredMixin," "PermissionRequiredMixin," or "template context." For REST API views using DRF, see django-drf. For admin views, see django-admin.
metadata:
  version: 1.0.0
---

# Django Views

You are a Django views and URL routing expert. Your goal is to write clean, maintainable views using the right pattern for the task.

## Initial Assessment

**Check for project context first:**
If `.agents/django-project-context.md` exists (or `.claude/django-project-context.md`), read it to understand whether the project favors CBVs or FBVs, and what auth approach is used.

---

## FBV vs CBV Decision Guide

| Situation | Recommendation |
|-----------|---------------|
| Simple, one-off logic | FBV — less boilerplate |
| Standard CRUD (list/detail/create/update/delete) | CBV — use generic views |
| Reusable behavior across views | CBV with Mixins |
| Complex branching logic | FBV — clearer flow |
| REST API endpoints | Use DRF (see django-drf skill) |

---

## Function-Based Views

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(['GET', 'POST'])
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'articles/create.html', {'form': form})
```

### Common Shortcuts

| Function | Use For |
|----------|---------|
| `render(request, template, context)` | Render template with context |
| `redirect(viewname_or_url, *args)` | HTTP redirect |
| `get_object_or_404(Model, **kwargs)` | Get object or raise 404 |
| `get_list_or_404(Model, **kwargs)` | Get list or raise 404 |
| `HttpResponse(content)` | Raw HTTP response |
| `JsonResponse(dict)` | JSON response |

---

## Class-Based Views

### Generic Display Views

```python
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/list.html'  # default: <app>/<model>_list.html
    context_object_name = 'articles'       # default: object_list
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        # Scope to the current user
        return super().get_queryset().filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Articles'
        return context


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'articles/detail.html'
    context_object_name = 'article'
```

### Generic Edit Views

```python
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/form.html'
    success_url = reverse_lazy('articles:list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/form.html'

    def get_success_url(self):
        return reverse_lazy('articles:detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        # Only allow editing own articles
        return super().get_queryset().filter(author=self.request.user)


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'articles/confirm_delete.html'
    success_url = reverse_lazy('articles:list')
```

---

## URL Configuration

### App URLs

```python
# articles/urls.py
from django.urls import path
from . import views

app_name = 'articles'  # Always use app namespaces

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='list'),
    path('create/', views.ArticleCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='delete'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail-by-slug'),
]
```

### Root URLs

```python
# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls', namespace='articles')),
    path('api/', include('api.urls', namespace='api')),
    path('accounts/', include('django.contrib.auth.urls')),
]
```

### URL Patterns

| Pattern | Matches |
|---------|---------|
| `<int:pk>` | Integer: `42` |
| `<str:name>` | Non-empty string without `/` |
| `<slug:slug>` | Slug: `my-article-title` |
| `<uuid:id>` | UUID: `550e8400-e29b-41d4-a716-446655440000` |
| `<path:subpath>` | Any string including `/` |

---

## Mixins

### Authentication & Permission Mixins

```python
from django.contrib.auth.mixins import (
    LoginRequiredMixin,      # Redirect to login if not authenticated
    PermissionRequiredMixin, # Require specific permission
    UserPassesTestMixin,     # Custom test function
)

class AdminOnlyView(PermissionRequiredMixin, ListView):
    permission_required = 'articles.view_article'
    # Or multiple: permission_required = ['app.perm1', 'app.perm2']


class OwnerOnlyView(UserPassesTestMixin, DetailView):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
```

### Custom Mixins

```python
class OwnerQuerySetMixin:
    """Filter queryset to objects owned by the current user."""
    owner_field = 'author'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.owner_field: self.request.user})


class ArticleListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    model = Article
```

---

## Form Handling in Views

### Using Django Forms with CBVs

```python
from django import forms

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'status']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters.')
        return title
```

---

## Reverse URL Resolution

```python
# In templates:
{% url 'articles:detail' pk=article.pk %}
{% url 'articles:list' %}

# In Python:
from django.urls import reverse, reverse_lazy

reverse('articles:detail', kwargs={'pk': 1})        # Returns string
reverse_lazy('articles:list')                        # Lazy — use in class attributes
```

---

## Related Skills

- **django-drf**: For REST API views using Django REST Framework
- **django-auth**: For authentication views and custom login flows
- **django-models**: For the underlying models these views work with
- **django-tests**: For testing views with the test client
