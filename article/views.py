from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from article.models import Article
from datetime import datetime
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    posts = Article.objects.all()
    paginator = Paginator(posts, 2)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'home.html', {'post_list':post_list})

def logi(request):
    goto = request.GET.get('next')
    if not goto:
        goto = '/'
    if 'error' in request.GET:
        return render(request, 'login.html', {'error':True, 'target':goto})
    else:
        return render(request, 'login.html', {'target':goto})

@login_required
def logo(request):
    logout(request)
    return redirect('/login')

def success(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None and user.is_active:
            login(request, user)
            return redirect(request.GET.get('target'))
    return redirect('/login?error=1')

@login_required
def detail(request, idx):
    try:
        post = Article.objects.get(id=str(idx))
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'post.html', {'post':post})

@login_required
def archives(request):
    try:
        post_list = Article.objects.all()
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'archives.html', {'post_list':post_list, 'error':False})

def about_me(request):
    return render(request, 'aboutme.html')

@login_required
def search_tag(request, tag):
    try:
        post_list = Article.objects.filter(category__iexact=tag)
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'tag.html', {'post_list':post_list})

@login_required
def blog_search(request):
    if 's' in request.GET:
        s = request.GET['s']
        if not s:
            return render(request, 'home.html')
        else:
            post_list = Article.objects.filter(title__icontains=s)
            if len(post_list) == 0:
                return render(request, 'archives.html', {'post_list':post_list, 'error':True})
            else:
                return render(request, 'archives.html', {'post_list':post_list, 'error':False})
    return redirect('/')

class RSSFeed(Feed):
    title = "RSS feed - article"
    link = "feeds/posts/"
    description = "RSS feed - blog posts"
    def items(self):
        return Article.objects.order_by('-date_time')
    def item_title(self, item):
        return item.title
    def item_pubdate(self, item):
        return item.date_time
    def item_description(self, item):
        return item.content
    def item_link(self, item):
        return reverse('detail', args=[item.id])