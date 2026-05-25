from django import forms
from .models import ServiceOrder


class ServiceOrderForm(forms.ModelForm):
   
   

    class Meta:
        model  = ServiceOrder
        fields = [
            'customer_name',
            'phone_number',
            'address',
            'service_type',
            'grass_option',
            'note',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Nguyễn Văn A',
            }),
            'phone_number': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': '09xx xxx xxx',
            }),
            'address': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Số nhà, đường, phường, quận...',
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-control',
                'id':    'id_service_type',   # JS dựa vào id này
            }),
            'grass_option': forms.Select(attrs={
                'class': 'form-control',
                'id':    'id_grass_option',
            }),
            'note': forms.Textarea(attrs={
                'class':       'form-control',
                'placeholder': 'Mô tả thêm về yêu cầu của bạn...',
                'rows':        4,
            }),
        }
        labels = {
            'customer_name': 'Họ và Tên *',
            'phone_number':  'Số Điện Thoại *',
            'address':       'Địa Chỉ *',
            'service_type':  'Loại Dịch Vụ *',
            'grass_option':  'Loại Cỏ',
            'note':          'Ghi Chú',
        }

    def clean(self):
        cleaned = super().clean()
        service = cleaned.get('service_type')
        grass   = cleaned.get('grass_option')

        # Bắt buộc chọn loại cỏ khi dịch vụ là Lợp thảm cỏ
        if service == 'lop_tham_co' and not grass:
            self.add_error(
                'grass_option',
                'Vui lòng chọn loại cỏ cho dịch vụ Lợp thảm cỏ.'
            )

        # Nếu không phải lợp thảm cỏ, xóa grass_option để không lưu rác
        if service != 'lop_tham_co':
            cleaned['grass_option'] = None

        return cleaned