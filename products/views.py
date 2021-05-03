from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm


# Create your views here.
def product_detail_view(request, *args, **kwargs):
    context = {
        'product': Product.objects.get(id=kwargs['productid'])
    }
    return render(request, "products/product-page.html", context)


def product_list_view(request, *args, **kwargs):
    context = {
        'products': Product.objects.all()
    }
    return render(request, "home-page.html", context)


def product_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            pending_review = form.save(commit=False)
            pending_review.publisher = request.user.username
            pending_review.save()
        return redirect('/home/')
    else:
        form = ProductForm()
    return render(request=request, template_name="products/product_create.html", context={"form": form})


