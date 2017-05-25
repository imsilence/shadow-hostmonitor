#encoding: utf-8

from django.shortcuts import render, redirect

from django.urls import reverse

from .models import Event, ActualFile, Config
from .forms import SettingForm

def list_event(request):
    return render(request, 'filemonitor/event_list.html', {'events' : Event.list_doing()})


def deal_event(request, pk):
    Event.deal(pk)
    return redirect(reverse("filemonitor:list_event"))


def list_file(request):
    files = ActualFile.list_doing()
    return render(request, 'filemonitor/file_list.html', {'files' : files})


def recover_file(request, pk):
    ActualFile.recover(pk)
    return redirect(reverse("filemonitor:list_file"))


def ignore_file(request, pk):
    ActualFile.ignore(pk)
    return redirect(reverse("filemonitor:list_file"))


def setting(request):
    form = None
    if request.method == 'POST':
        form = SettingForm(request.POST)


        if form.is_valid():
            interval = form.cleaned_data.get('interval')
            fdir = form.cleaned_data.get('fdir')
            suffix = form.cleaned_data.get('suffix')
            except_dirs = form.cleaned_data.get('except_dirs')
            except_suffixs = form.cleaned_data.get('except_suffixs')
            config = {
                'interval' : interval,
                'paths' : [
                    {
                        'dir' : fdir,
                        'suffix' : suffix,
                        'except_dirs' : [node for node in except_dirs.split(';') if node.strip()],
                        'except_suffixs' : [node for node in except_suffixs.split(';') if node.strip()]
                    }
                ]
            }

            Config.set_config(config, 'filemonitor')

    else:
        config = Config.get_config('filemonitor', '')
        paths = config.get('paths')
        if paths:
            obj = {}
            obj['interval'] = config.get('interval')
            obj['fdir'] = paths[0].get('dir')
            obj['suffix'] = paths[0].get('suffix')
            obj['except_dirs'] = '; '.join(paths[0].get('except_dirs'))
            obj['except_suffixs'] = '; '.join(paths[0].get('except_suffixs'))
            form = SettingForm(obj)

    return render(request, 'filemonitor/setting.html', {'form': form})
