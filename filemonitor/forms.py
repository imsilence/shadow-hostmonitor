#encoding: utf-8

from django import forms

class SettingForm(forms.Form):
    interval = forms.IntegerField(required=True, min_value=30, max_value=24 * 30 * 60, label='检测频率')
    fdir = forms.CharField(required=True, max_length=1024, label='检测文件路径')
    except_dirs = forms.CharField(required=False, max_length=1024, label='去除文件路径', help_text='使用;分隔多个路径')
    suffix = forms.CharField(required=True, max_length=1024, label='检测文件后缀',  help_text='*表示全部文件类型')
    except_suffixs = forms.CharField(required=False, max_length=1024, label='去除文件后缀', help_text='使用;分隔多个文件后缀, 类似.doc; .py')


    def clean_interval(self):
        data = self.cleaned_data.get('interval', 30 * 60)
        return data
