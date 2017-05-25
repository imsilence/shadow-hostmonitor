#encoding: utf-8

import os
import json
from datetime import datetime
from pytz import timezone
import time

from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone as dtimezone

from hostmonitor.settings import TIME_ZONE
from hostmonitor.settings import BASE_DIR
from utils.files import list_dir, get_file_stat, copy_file
from utils.crypt import get_file_md5, get_str_md5

class BaseFile(models.Model):

    cid = models.CharField(max_length=128, null=False, default='')
    fid = models.CharField(max_length=128, null=False)
    path = models.TextField(null=False)
    ftype = models.IntegerField(null=False)
    inode = models.IntegerField(null=False, default=0)
    links = models.IntegerField(null=False, default=0)

    check_sum = models.CharField(max_length=1024, null=False)

    uid = models.IntegerField(null=False, default=0)
    user = models.CharField(max_length=64, null=False, default='')
    gid = models.IntegerField(null=False, default=0)
    group = models.CharField(max_length=64, null=False, default='')
    size = models.IntegerField(null=False, default=0)
    mode = models.IntegerField(null=False, default=0)

    ctime = models.DateTimeField(null=False)
    atime = models.DateTimeField(null=False)
    mtime = models.DateTimeField(null=False)

    class Meta:
        abstract = True
        unique_together = ['cid', 'fid']

    def __str__(self):
        return self.path


    @classmethod
    def saveOrReplace(cls, path, cid=''):
        zone = timezone(TIME_ZONE)
        fid = get_str_md5(path)
        stat = get_file_stat(path)
        md5 = get_file_md5(path)
        is_created, _obj = True, None
        try:
            _obj = cls.objects.get(fid=fid, cid=cid)
            is_created = False
        except ObjectDoesNotExist as e:
            _obj = cls()

        _obj.cid = cid
        _obj.fid = fid
        _obj.path = path
        _obj.ftype = 1
        _obj.inode = stat.st_ino
        _obj.links = stat.st_nlink
        _obj.check_sum = md5
        _obj.uid = stat.st_uid
        _obj.gid = stat.st_gid
        _obj.size = stat.st_size
        _obj.mode = stat.st_mode
        _obj.ctime = datetime.fromtimestamp(stat.st_ctime).replace(tzinfo=zone)
        _obj.atime = datetime.fromtimestamp(stat.st_atime).replace(tzinfo=zone)
        _obj.mtime = datetime.fromtimestamp(stat.st_mtime).replace(tzinfo=zone)
        _obj.save()

        return is_created, _obj


    @classmethod
    def build(cls, paths):
        for path in paths:
            fpaths = list_dir(path.get('dir'), path.get('suffix'), path.get('except_suffixs'), path.get('except_dirs'))
            for fpath in fpaths:
                cls.saveOrReplace(fpath)


class BaseLineFile(BaseFile):

    btime = models.DateTimeField(auto_now=True)

    @classmethod
    def build(cls, paths):
        now = dtimezone.now()
        suffix = '{dt:s}_{suffix:d}'.format(dt=now.strftime('%Y%m%d_%H%M%S'), suffix=int(now.timestamp()))
        data_dir = os.path.join(BASE_DIR, 'datas', suffix)
        last_dir = os.path.join(BASE_DIR, 'datas', 'last')
        tmp_dir = os.path.join(BASE_DIR, 'datas', 'tmp_%s' % suffix)
        BaseLineFile.objects.raw('CREATE TABLE filemonitor_baseline_{suffix:s} AS SELECT * from filemonitor_baseline'.format(suffix=suffix));
        os.makedirs(tmp_dir, exist_ok=True)
        for path in paths:
            fpaths = list_dir(path.get('dir'), path.get('suffix'), path.get('except_suffixs'), path.get('except_dirs'))
            for fpath in fpaths:
                _, obj = cls.saveOrReplace(fpath)
                # 备份文件
                copy_file(obj.path, os.path.join(tmp_dir, obj.fid))

        if os.path.exists(last_dir):
            os.rename(last_dir, data_dir)

        time.sleep(3)
        os.rename(tmp_dir, last_dir)

        BaseLineFile.objects.filter(btime__lt=now).delete()


class ActualFile(BaseFile):

    CK_OK = 0
    CK_CREATE = 1
    CK_MODIFY = 2
    CK_DELETE = 3

    DL_NO = 0
    DL_IGNORE = 1
    DL_RECOVER = 2

    adtime = models.DateTimeField(null=False, auto_now_add=True)
    cktime = models.DateTimeField(null=False, auto_now=True)
    # 0 => ok, 1 => create, 2 => modify, 3 => delete
    ckstatus = models.IntegerField(null=False, default=0)
    # 0 => no, 1 => ignore, 2 => recover
    dlstatus = models.IntegerField(null=False, default=0)
    remark = models.TextField(null=False, default='')


    def status_text(self):
        ck_texts = {self.CK_OK : '正常', self.CK_CREATE : '创建', self.CK_DELETE : '删除', self.CK_MODIFY : '修改', }
        dl_texts = {self.DL_NO : '未处理', self.DL_IGNORE : '已忽略', self.DL_RECOVER : '已恢复',}
        return '%s/%s' % (ck_texts.get(self.ckstatus), dl_texts.get(self.dlstatus))


    @classmethod
    def build(cls, paths):
        now = dtimezone.now()
        sql = 'CREATE TABLE filemonitor_actualfile_{dt:s}_{suffix:d} AS SELECT * from filemonitor_actualfile;'.format(dt=now.strftime('%Y%m%d_%H%M%S'), suffix=int(now.timestamp()))
        ActualFile.objects.raw(sql);
        #attrs = ['inode', 'check_sum', 'uid', 'gid', 'size', 'mode', 'ctime', 'atime', 'mtime']
        attrs = ['check_sum', 'uid', 'gid', 'size', 'mode', 'atime', 'mtime']
        for path in paths:
            fpaths = list_dir(path.get('dir'), path.get('suffix'), path.get('except_suffixs'), path.get('except_dirs'))
            for fpath in fpaths:
                is_created, obj = cls.saveOrReplace(fpath)
                try:
                    bobj = BaseLineFile.objects.get(cid=obj.cid, fid=obj.fid)
                    for attr in attrs:
                        bvalue = getattr(bobj, attr, '')
                        avalue = getattr(obj, attr, '')
                        if bvalue != avalue:
                            if obj.ckstatus != cls.CK_MODIFY:
                                obj.dlstatus = cls.DL_NO
                                Event(content="文件[{path}]属性[{attr}]被修改, 基准值:[{bvalue}], 现实:[{avalue}]".format(path=obj.path, attr=attr, bvalue=bvalue, avalue=avalue)).save()
                            obj.ckstatus = cls.CK_MODIFY
                            break
                    else:
                        obj.ckstatus = cls.CK_OK
                        obj.dlstatus = cls.DL_NO
                except ObjectDoesNotExist as e:
                    if obj.ckstatus != cls.CK_CREATE:
                        obj.dlstatus = cls.DL_NO
                        Event(content="文件[{path}]被创建".format(path=obj.path)).save()
                    obj.ckstatus = cls.CK_CREATE

                obj.save()


        ActualFile.objects.filter(cktime__lt=now, ckstatus=cls.CK_CREATE).delete()
        objs = ActualFile.objects.filter(Q(cktime__lt=now) & ~Q(ckstatus=cls.CK_DELETE)).all()
        for obj in objs:
            obj.ckstatus = cls.CK_DELETE
            obj.dlstatus = cls.DL_NO
            obj.save()
            Event(content="文件[{path}]被删除".format(path=obj.path)).save()


    @classmethod
    def list_doing(cls):
        return ActualFile.objects.filter(~Q(ckstatus=cls.CK_OK)).order_by('dlstatus')


    @classmethod
    def ignore(cls, pk):
        try:
            afile = cls.objects.get(pk=pk)
            afile.dlstatus = cls.DL_IGNORE
            afile.save()
        except ObjectDoesNotExist as e:
            pass


    @classmethod
    def recover(cls, pk):
        try:
            afile = cls.objects.get(pk=pk)

            now = dtimezone.now()
            suffix = '{dt:s}_{suffix:d}'.format(dt=now.strftime('%Y%m%d_%H%M%S'), suffix=int(now.timestamp()))
            data_dir = os.path.join(BASE_DIR, 'datas', 'backup', suffix)
            last_dir = os.path.join(BASE_DIR, 'datas', 'last')
            os.makedirs(data_dir, exist_ok=True)
            if afile.ckstatus != cls.CK_DELETE:
                copy_file(afile.path, data_dir)
            if afile.ckstatus == cls.CK_CREATE:
                os.unlink(afile.path)
            elif afile.ckstatus in [cls.CK_MODIFY, cls.CK_DELETE]:
                copy_file(os.path.join(last_dir, afile.fid), afile.path)
                _, afile = cls.saveOrReplace(afile.path)
            afile.dlstatus = cls.DL_RECOVER
            afile.save()
        except ObjectDoesNotExist as e:
            pass


class Event(models.Model):

    ST_DOING = 0
    ST_DONE = 1

    cid = models.CharField(max_length=128, null=False, default='')
    content = models.TextField(null=False, default='')
    adtime = models.DateTimeField(null=False, auto_now_add=True)
    dltime = models.DateTimeField(null=False, auto_now=True)
    status = models.IntegerField(null=False, default=0)
    remark = models.TextField(null=False, default='')

    @classmethod
    def list_doing(cls, limit=200):
        return Event.objects.filter(status=cls.ST_DOING).order_by('-adtime')[:limit]

    @classmethod
    def deal(cls, pk):
        try:
            event = cls.objects.get(pk=pk)
            event.status = cls.ST_DONE
            event.save()
        except OjbectsDoesNotExist as e:
            pass


class Config(models.Model):

    cid = models.CharField(max_length=128, null=False, default='')
    category = models.CharField(max_length=256, default='')
    content = models.TextField(null=False, default='{}')
    adtime = models.DateTimeField(null=False, auto_now_add=True)

    __default_cached = {}

    @classmethod
    def get_config(cls, category='', cid=''):
        _rt_json = {}
        try:
            config = cls.objects.get(cid=cid, category=category)
            _rt_json = json.loads(config.content)
        except ObjectDoesNotExist as e:
            _rt_json = cls.__get_default(category, cid)

        return _rt_json

    @classmethod
    def __get_default(cls, category, cid):
        rt_default = cls.__default_cached.get(category)
        if rt_default is None:
            rt_default = {}
            path = os.path.join(BASE_DIR, 'etc', '{0}.default.json'.format(category))
            if os.path.exists(path):
                with open(path, 'rt') as fhandler:
                    rt_default = json.loads(fhandler.read())

        return rt_default

    @classmethod
    def set_config(cls, jconfig, category='', cid=''):
        config = None
        try:
            config = cls.objects.get(cid=cid, category=category)
        except ObjectDoesNotExist as e:
            config = cls(cid=cid, category=category)

        config.content = json.dumps(jconfig)
        config.save()
