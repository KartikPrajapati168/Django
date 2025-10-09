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



from django import forms
from .models import MenuCategory, MenuItem  # Adjust if models are elsewhere

class MenuCategoryCreateForm(forms.ModelForm):
    predefined_category = forms.ModelChoiceField(
        queryset=MenuCategory.objects.filter(is_global=True),
        required=False,
        label="Choose Predefined Category"
    )

    class Meta:
        model = MenuCategory
        fields = ['name', 'image']
        
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

class MenuCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['name', 'image']  # No predefined

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        category = super().save(commit=False)
        if commit:
            category.save()
        return category

class MenuItemCreateForm(forms.ModelForm):
    predefined_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.none(),  # override in init
        required=False,
        label="Choose Predefined Item (optional)"
    )

    class Meta:
        model = MenuItem
        fields = ['category','name', 'description', 'price', 'image','is_available']

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        category_for_queryset = kwargs.pop('category', None)  # Renamed to avoid confusion
        super().__init__(*args, **kwargs)

        self.restaurant = restaurant

        if category_for_queryset is not None:
            self.fields['predefined_item'].queryset = MenuItem.objects.filter(
                restaurant__isnull=True,
                category__name=category_for_queryset.name
            )
        else:
            self.fields['predefined_item'].queryset = MenuItem.objects.none()

    def save(self, commit=True):
        predefined = self.cleaned_data.get('predefined_item')
        if predefined:
            new_item = MenuItem(
                name=predefined.name,
                description=predefined.description,
                price=predefined.price,
                image=predefined.image,
                restaurant=self.restaurant,
                category=predefined.category,  # Use the predefined's category, or self.cleaned_data['category'] if you want to override
                is_available=True
            )
        else:
            new_item = super().save(commit=False)
            new_item.restaurant = self.restaurant
            # Removed: new_item.category = self.category  # This was overwriting with None

        if commit:
            new_item.save()
        return new_item
    
# class MenuCategoryCreateForm(forms.ModelForm):
#     predefined_category = forms.ModelChoiceField(
#         queryset=MenuCategory.objects.filter(is_global=True),
#         required=False,
#         label="Choose Predefined Category"
#     )

#     class Meta:
#         model = MenuCategory
#         fields = ['name', 'description','image']
        
#     def __init__(self, *args, **kwargs):
#         restaurant = kwargs.pop('restaurant', None)
#         super().__init__(*args, **kwargs)
#         self.restaurant = restaurant

#     def save(self, commit=True):
#         predefined = self.cleaned_data.get('predefined_category')
#         if predefined:
#             # Clone the global category
#             new_category = MenuCategory(
#                 name=predefined.name,
#                 image=predefined.image,
#                 restaurant=self.restaurant,
#                 is_global=False
#             )
#         else:
#             new_category = super().save(commit=False)
#             new_category.restaurant = self.restaurant
#             new_category.is_global = False

#         if commit:
#             new_category.save()
#         return new_category
    
    
    
# class MenuItemCreateForm(forms.ModelForm):
#     predefined_item = forms.ModelChoiceField(
#         queryset=MenuItem.objects.none(),  # override in init
#         required=False,
#         label="Choose Predefined Item (optional)"
#     )

#     class Meta:
#         model = MenuItem
#         fields = ['category','name', 'description', 'price', 'image','is_available']

#     def __init__(self, *args, **kwargs):
#         restaurant = kwargs.pop('restaurant', None)
#         category = kwargs.pop('category', None)
#         super().__init__(*args, **kwargs)

#         self.restaurant = restaurant
#         self.category = category

#         # self.fields['predefined_item'].queryset = MenuItem.objects.filter(
#         #     restaurant__isnull=True,
#         #     category__name=category.name
#         # )
#          # ✅ Safe check
#         if category is not None:
#             self.fields['predefined_item'].queryset = MenuItem.objects.filter(
#                 restaurant__isnull=True,
#                 category__name=category.name
#             )
#         else:
#             self.fields['predefined_item'].queryset = MenuItem.objects.none()

#     def save(self, commit=True):
#         predefined = self.cleaned_data.get('predefined_item')
#         if predefined:
#             new_item = MenuItem(
#                 name=predefined.name,
#                 description=predefined.description,
#                 price=predefined.price,
#                 image=predefined.image,
#                 restaurant=self.restaurant,
#                 category=self.category,
#                 is_available=True
#             )
#         else:
#             new_item = super().save(commit=False)
#             new_item.restaurant = self.restaurant
#             new_item.category = self.category

#         if commit:
#             new_item.save()
#         return new_item


# class MenuCategoryCreateForm(forms.ModelForm):
#     predefined_category = forms.ModelChoiceField(
#         queryset=MenuCategory.objects.filter(is_global=True),
#         required=False,
#         label="Choose Predefined Category"
#     )

#     class Meta:
#         model = MenuCategory
#         fields = ['name','image']
        
#     def __init__(self, *args, **kwargs):
#         restaurant = kwargs.pop('restaurant', None)
#         super().__init__(*args, **kwargs)
#         self.restaurant = restaurant

#     def save(self, commit=True):
#         predefined = self.cleaned_data.get('predefined_category')
#         if predefined:
#             # Clone the global category
#             new_category = MenuCategory(
#                 name=predefined.name,
#                 image=predefined.image,
#                 restaurant=self.restaurant,
#                 is_global=False
#             )
#         else:
#             new_category = super().save(commit=False)
#             new_category.restaurant = self.restaurant
#             new_category.is_global = False

#         if commit:
#             new_category.save()
#         return new_category
    
# class MenuCategoryCreateForm(forms.ModelForm):
#     predefined_category = forms.ModelChoiceField(
#         queryset=MenuCategory.objects.filter(is_global=True),
#         required=False,
#         label="Choose Predefined Category"
#     )

#     class Meta:
#         model = MenuCategory
#         fields = ['name','image']
        
#     def __init__(self, *args, **kwargs):
#         restaurant = kwargs.pop('restaurant', None)
#         super().__init__(*args, **kwargs)
#         self.restaurant = restaurant

#     def save(self, commit=True):
#         predefined = self.cleaned_data.get('predefined_category')
#         if predefined:
#             # Clone the global category
#             new_category = MenuCategory(
#                 name=predefined.name,
#                 image=predefined.image,
#                 restaurant=self.restaurant,
#                 is_global=False
#             )
#         else:
#             new_category = super().save(commit=False)
#             new_category.restaurant = self.restaurant
#             new_category.is_global = False

#         if commit:
#             new_category.save()
#         return new_category

# class MenuCategoryUpdateForm(forms.ModelForm):
#     class Meta:
#         model = MenuCategory
#         fields = ['name', 'image']  # No predefined_category

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def save(self, commit=True):
#         category = super().save(commit=False)
#         if commit:
#             category.save()
#         return category    
    
# # class MenuItemCreateForm(forms.ModelForm):
# #     predefined_item = forms.ModelChoiceField(
# #         queryset=MenuItem.objects.none(),  # override in init
# #         required=False,
# #         label="Choose Predefined Item (optional)"
# #     )

# #     class Meta:
# #         model = MenuItem
# #         fields = ['category','name', 'description', 'price', 'image','is_available']

# #     def __init__(self, *args, **kwargs):
# #         restaurant = kwargs.pop('restaurant', None)
# #         category = kwargs.pop('category', None)
# #         super().__init__(*args, **kwargs)

# #         self.restaurant = restaurant
# #         self.category = category

# #         # self.fields['predefined_item'].queryset = MenuItem.objects.filter(
# #         #     restaurant__isnull=True,
# #         #     category__name=category.name
# #         # )
# #          # ✅ Safe check
# #         if category is not None:
# #             self.fields['predefined_item'].queryset = MenuItem.objects.filter(
# #                 restaurant__isnull=True,
# #                 category__name=category.name
# #             )
# #         else:
# #             self.fields['predefined_item'].queryset = MenuItem.objects.none()

# #     def save(self, commit=True):
# #         predefined = self.cleaned_data.get('predefined_item')
# #         if predefined:
# #             new_item = MenuItem(
# #                 name=predefined.name,
# #                 description=predefined.description,
# #                 price=predefined.price,
# #                 image=predefined.image,
# #                 restaurant=self.restaurant,
# #                 category=self.category,
# #                 is_available=True
# #             )
# #         else:
# #             new_item = super().save(commit=False)
# #             new_item.restaurant = self.restaurant
# #             new_item.category = self.category

# #         if commit:
# #             new_item.save()
# #         return new_item
    
    
#     class MenuItemCreateForm(forms.ModelForm):
#         predefined_item = forms.ModelChoiceField(
#         queryset=MenuItem.objects.none(),  # override in init
#         required=False,
#         label="Choose Predefined Item (optional)"
#         )

#     class Meta:
#         model = MenuItem
#         fields = ['category','name', 'description', 'price', 'image','is_available']

#     def __init__(self, *args, **kwargs):
#         restaurant = kwargs.pop('restaurant', None)
#         category_for_queryset = kwargs.pop('category', None)  # Renamed to avoid confusion
#         super().__init__(*args, **kwargs)

#         self.restaurant = restaurant

#         if category_for_queryset is not None:
#             self.fields['predefined_item'].queryset = MenuItem.objects.filter(
#                 restaurant__isnull=True,
#                 category__name=category_for_queryset.name
#             )
#         else:
#             self.fields['predefined_item'].queryset = MenuItem.objects.none()

#     def save(self, commit=True):
#         predefined = self.cleaned_data.get('predefined_item')
#         if predefined:
#             new_item = MenuItem(
#                 name=predefined.name,
#                 description=predefined.description,
#                 price=predefined.price,
#                 image=predefined.image,
#                 restaurant=self.restaurant,
#                 category=predefined.category,  # Use the predefined's category, or self.cleaned_data['category'] if you want to override
#                 is_available=True
#             )
#         else:
#             new_item = super().save(commit=False)
#             new_item.restaurant = self.restaurant
#             # Removed: new_item.category = self.category  # This was overwriting with None

#         if commit:
#             new_item.save()
#         return new_item
    
    # def save(self, commit=True):
    #     predefined = self.cleaned_data.get('predefined_item')

    #     if self.instance.pk:  
    #         # Editing existing item
    #         item = super().save(commit=False)
    #     elif predefined:
    #         # Creating from predefined
    #         item = MenuItem(
    #         name=predefined.name,
    #         description=predefined.description,
    #         price=predefined.price,
    #         image=predefined.image,
    #         restaurant=self.restaurant,
    #         category=self.category,
    #         is_available=True
    #     )
    #     else:
    #         # Creating new
    #         item = super().save(commit=False)
    #         item.restaurant = self.restaurant
    #         item.category = self.category

    #     if commit:
    #         item.save()
    #     return item

    
    