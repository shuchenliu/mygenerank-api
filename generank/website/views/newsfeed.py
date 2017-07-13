from django.shortcuts import render, get_object_or_404
from generank.api.models import news_feed
from django.views import generic


# Create your views here.

class NewsFeedView(generic.TemplateView):
    template_name = 'roughnewsfeed.html'

    #passes multiple objects to request for use in newsfeed
    def get(self, request):
        return render(request, "roughnewsfeed.html", {
            'featured': news_feed.Item.objects.all().order_by('-created_on')[:2],
            'remaining': news_feed.Item.objects.all().order_by('-created_on')[2:10],
            'title': 'MyGeneRank | News',
        })
