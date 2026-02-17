from django.contrib import admin
from .models import Sale, SaleItem
# Register your models here.
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    min_num = 1
    readonly_fields = ['product','quantity','unit_price','subtotal']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id','customer', 'total_amount', 'created_by',  'status', 'created_at']
    inlines = [SaleItemInline]
    search_fields = ['id', 'customer__name', 'customer__phone']
    list_filter = ['created_by','status']
    readonly_fields = ['customer','total_amount','created_by','status','created_at']

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False