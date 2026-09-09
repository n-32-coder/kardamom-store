from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    slug = forms.SlugField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    is_featured = forms.BooleanField(required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'category', 'description', 'price',
            'stock', 'pack_size', 'sku', 'image',
            'is_active', 'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'slug': 'Leave blank to auto-generate from the name.',
        }
