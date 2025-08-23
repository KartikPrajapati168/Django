from django import forms
from .models import TableBooking
from .models import Restaurant, RestaurantOwnerProfile
from .models import MenuItem,MenuCategory

class TableBookingForm(forms.ModelForm):
    class Meta:
        model  = TableBooking
        fields = [
            'name', 'email', 'phone',
            'date', 'time', 'no_of_guests',
            'meal_type', 'message',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class RestaurantForm(forms.ModelForm):
    #forms.ModelForm ka matlab hai: Ye form model ke fields se automatic banega.
    class Meta:
        model = Restaurant
        fields = [
            'name', 'logo', 'description', 'address',
            'timings', 'dining_out_available',
        ]
        

class OwnerProfileForm(forms.ModelForm):
    class Meta:
        model  = RestaurantOwnerProfile
        fields = ['gst_number']          # आगे owner_phone, kyc वग़ैरह भी जोड़ सकते हैं
        widgets = {
            'gst_number': forms.TextInput(attrs={'placeholder': 'GSTIN'}),
        }
        # user field को form से बाहर कर दो
        # exclude = ["user", "restaurant"]


class MenuCategoryCreateForm(forms.ModelForm):
    predefined_category = forms.ModelChoiceField(
        queryset=MenuCategory.objects.filter(is_global=True),
        required=False,
        label="Choose Predefined Category"
    )

    class Meta:
        model = MenuCategory
        fields = ['name', 'image','is_global']
        
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant

    def save(self, commit=True):
        predefined = self.cleaned_data.get('predefined_category')
        if predefined:
            # Clone the global category
            new_category = MenuCategory(
                name=predefined.name,
                image=predefined.image,
                restaurant=self.restaurant,
                is_global=False
            )
        else:
            new_category = super().save(commit=False)
            new_category.restaurant = self.restaurant
            new_category.is_global = False

        if commit:
            new_category.save()
        return new_category
    
    
    
class MenuItemCreateForm(forms.ModelForm):
    predefined_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.none(),  # override in init
        required=False,
        label="Choose Predefined Item (optional)"
    )

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image', 'is_available']

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)

        self.restaurant = restaurant
        self.category = category

        self.fields['predefined_item'].queryset = MenuItem.objects.filter(
            restaurant__isnull=True,
            category__name=category.name
        )

    def save(self, commit=True):
        predefined = self.cleaned_data.get('predefined_item')
        if predefined:
            new_item = MenuItem(
                name=predefined.name,
                description=predefined.description,
                price=predefined.price,
                image=predefined.image,
                restaurant=self.restaurant,
                category=self.category,
                is_available=True
            )
        else:
            new_item = super().save(commit=False)
            new_item.restaurant = self.restaurant
            new_item.category = self.category

        if commit:
            new_item.save()
        return new_item
    
    