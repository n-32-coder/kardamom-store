from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Product, ProductCategory, ProductReview, WishlistItem


def home(request):
    featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
    recent = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    categories = ProductCategory.objects.filter(is_active=True)
    return render(request, 'home.html', {
        'featured_products': featured,
        'recent_products': recent,
        'categories': categories,
    })


def product_list(request):
    categories = ProductCategory.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).select_related('category')

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    pack_size = request.GET.get('pack_size')
    if pack_size:
        products = products.filter(pack_size=pack_size)

    min_price = request.GET.get('min_price')
    if min_price:
        try:
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    max_price = request.GET.get('max_price')
    if max_price:
        try:
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(sku__icontains=query)
        )

    sort_by = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')
    prefix = '-' if order == 'desc' else ''
    if sort_by in ('price', 'name', 'created_at'):
        products = products.order_by(f'{prefix}{sort_by}')
    else:
        products = products.order_by('name')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'current_pack_size': pack_size,
        'current_query': query,
        'current_sort': sort_by,
        'current_order': order,
    })


def product_detail(request, product_id, slug):
    product = get_object_or_404(Product, id=product_id, slug=slug, is_active=True)
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(id=product.id)[:4]
    )
    return render(request, 'products/detail.html', {
        'product': product,
        'images': product.images.all(),
        'reviews': product.reviews.all()[:6],
        'related': related,
    })


def api_product_search(request):
    from django.http import JsonResponse

    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True,
    )[:10]
    return JsonResponse({'results': [
        {'id': p.id, 'name': p.name, 'price': str(p.price),
         'pack_size': p.get_pack_size_display()}
        for p in products
    ]})


@login_required
def wishlist_list(request):
    items = WishlistItem.objects.filter(customer=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'items': items})


@login_required
def wishlist_toggle(request, product_id):
    from django.contrib import messages
    from django.shortcuts import redirect

    product = get_object_or_404(Product, id=product_id, is_active=True)
    item = WishlistItem.objects.filter(customer=request.user, product=product).first()
    if item:
        item.delete()
        messages.info(request, f'{product.name} removed from wishlist.')
    else:
        WishlistItem.objects.create(customer=request.user, product=product)
        messages.success(request, f'{product.name} saved to wishlist.')
    return redirect('product_detail', product_id=product.id, slug=product.slug)


@login_required
def review_add(request, product_id):
    from django.contrib import messages
    from django.shortcuts import redirect

    from orders.models import OrderItem

    product = get_object_or_404(Product, id=product_id, is_active=True)
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
        except ValueError:
            rating = 0
        comment = request.POST.get('comment', '').strip()
        if rating not in (1, 2, 3, 4, 5) or not comment:
            messages.error(request, 'Give a 1–5 rating and a comment.')
        else:
            verified = OrderItem.objects.filter(
                order__customer=request.user, product=product
            ).exists()
            ProductReview.objects.update_or_create(
                product=product, customer=request.user,
                defaults={'rating': rating, 'comment': comment,
                          'verified_purchase': verified},
            )
            messages.success(request, 'Thanks for your review!')
    return redirect('product_detail', product_id=product.id, slug=product.slug)


def healthz(request):
    """Kubernetes liveness/readiness/startup probe endpoint."""
    from django.http import JsonResponse

    return JsonResponse({'status': 'ok', 'app': 'kardamom'})


@staff_member_required
def product_manage_list(request):
    from django.contrib import messages
    from django.db.models import Q
    from django.shortcuts import redirect

    if request.method == 'POST' and request.POST.get('action') == 'stock':
        product = get_object_or_404(Product, pk=request.POST.get('product_id'))
        try:
            delta = int(request.POST.get('delta', 0))
        except ValueError:
            delta = 0
        if delta and product.stock + delta >= 0:
            product.stock += delta
            product.save(update_fields=['stock'])
            messages.success(request, f'{product.name} stock → {product.stock}.')
        return redirect('product_manage_list')

    items = Product.objects.select_related('category').order_by('name')
    query = request.GET.get('q', '').strip()
    if query:
        items = items.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
            | Q(grade__icontains=query)
        )
    return render(request, 'products/manage_list.html', {'items': items, 'query': query})


@staff_member_required
def product_manage_edit(request, pk=None):
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.utils.text import slugify

    from .forms import ProductForm

    product = get_object_or_404(Product, pk=pk) if pk else None
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                obj.slug = slugify(obj.name)
            obj.save()
            messages.success(request, f'{obj.name} saved.')
            return redirect('product_manage_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/manage_form.html', {'form': form, 'product': product})


@staff_member_required
def product_manage_delete(request, pk):
    from django.contrib import messages
    from django.shortcuts import redirect

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'{name} deleted.')
        return redirect('product_manage_list')
    return render(request, 'products/manage_confirm_delete.html', {'product': product})


@staff_member_required
def category_manage_list(request):
    items = ProductCategory.objects.order_by('name')
    return render(request, 'products/category_list.html', {'items': items})


@staff_member_required
def category_manage_edit(request, pk=None):
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.utils.text import slugify

    from .forms import CategoryForm

    category = get_object_or_404(ProductCategory, pk=pk) if pk else None
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                obj.slug = slugify(obj.name)
            obj.save()
            messages.success(request, f'Category {obj.name} saved.')
            return redirect('category_manage_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'products/category_form.html', {'form': form, 'category': category})


@staff_member_required
def category_manage_delete(request, pk):
    from django.contrib import messages
    from django.shortcuts import redirect

    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category {name} deleted.')
        return redirect('category_manage_list')
    return render(request, 'products/category_confirm_delete.html', {'category': category})


@staff_member_required
def customer_manage_list(request):
    from customers.models import Customer

    customers = Customer.objects.order_by('-date_joined')
    return render(request, 'customers/manage_list.html', {'customers': customers})


@staff_member_required
def review_manage_list(request):
    reviews = ProductReview.objects.select_related('product', 'customer').order_by('-created_at')
    return render(request, 'products/review_list.html', {'reviews': reviews})


@staff_member_required
def review_manage_delete(request, pk):
    from django.contrib import messages
    from django.shortcuts import redirect

    review = get_object_or_404(ProductReview, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review removed.')
        return redirect('review_manage_list')
    return render(request, 'products/review_confirm_delete.html', {'review': review})
