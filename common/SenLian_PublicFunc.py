#!/usr/bin/env python
# -*-coding:utf-8-*-
# ==========================info========================
# Autho: ShenLian
# Func:  Modle of public functions
# Data:  2017\09\15
# ======================================================

from common.SenLian_Logging import *
from common.SenLian_TimeFunc import *

import socket, subprocess, shutil
import zipfile, tarfile, gzip
import os, sys, re
import hashlib
import chardet
import urllib
from bs4 import BeautifulSoup

try:
    from win32 import win32file
except:
    import win32file

# import psutil
# import pstats

OS_NAME = os.name

PYTHON_VERSION = int(sys.version_info.major)


###################################################Create Log###################################################
# Create a log file
def create_log(log_file):
    global log
    log = LogFunc(log_file)
    return log


# Write error info
def log_error(msg):
    log.log_error()


# Write warn info
def log_warn(msg):
    log.log_warn(msg)


# Write normal info
def log_info(msg):
    log.log_info(msg)


# Write and print error info
def loger_error(msg, color=FOREGROUND_WHITE):
    log.loger_error(msg, color)


# Write and print warn info
def loger_warn(msg, color=FOREGROUND_WHITE):
    log.loger_warn(msg, color)


# Write and print normal info
def loger_info(msg, color=FOREGROUND_WHITE):
    log.loger_info(msg, color)


def log_close():
    log.log_close()


###################################################Excute Commond#############################################
def shell_cmd(cmd):
    if not cmd:
        return 0
    rst = subprocess.call(cmd, shell=True)
    return rst


###################################################Socket Ordre###############################################
# Get host name
def get_host_name():
    return socket.gethostname()


# Get host ip
def get_host_ip():
    return socket.gethostbyname(get_host_name())


def get_host_ip_ex():
    try:
        url = urllib.urlopen('https://ip.cn/')
        content = url.read()
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf8')
        return soup.find('div', attrs={'id': 'cf-error-details'}).find('div', attrs={'class': 'cf-error-footer'}).find(
                'p').findAll('span')[2].get_text().split('Your IP:')[1].replace(' ', '')
    except:
        return None


###################################################Syetem Operate#############################################
# Start server
def start_server(server_name=''):
    cmd = ''
    if OS_NAME == 'nt':
        cmd = 'net start {0}'.format(server_name)

    return shell_cmd(cmd)


# Stop server
def stop_server(server_name):
    if not server_name:
        return 0
    cmd = ''
    if OS_NAME == 'nt':
        cmd = 'net stop {0}'.format(server_name)

    return shell_cmd(cmd)


def cls():
    if OS_NAME == 'nt':
        os.system("cls")
    else:
        os.system("clear")
    time.sleep(0.5)


def pause(msg="\nPress any key to continue\n"):
    if not (isinstance(msg, unicode)):
        msg = unicode(msg, 'utf-8')
    reload(sys)
    defaultencode = (sys.getdefaultencoding())
    sys.setdefaultencoding(sys.stdin.encoding)
    if PYTHON_VERSION > 2:
        inputStr = str(input(msg).strip().strip('\n')).lower()
    else:
        inputStr = str(raw_input(msg).strip().strip('\n')).lower()
    sys.setdefaultencoding(defaultencode)
    return inputStr


###################################################ZipFile####################################################
def is_zipfile(f):
    return zipfile.is_zipfile(f)


def get_relpath(root, abspath):
    pwd = os.getcwd()
    os.chdir(root)
    _relpath = os.path.relpath(abspath, start=root)
    os.chdir(pwd)
    return _relpath


def _zip(src_path, zip_file, zip_log=False):
    zip_folder = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    abs_targets = []
    cycle_list(src_path, abs_targets)
    pwd = os.getcwd()
    os.chdir(src_path)
    for target in abs_targets:
        if isfile(target):
            dir_name = os.path.dirname(target)
            if not zip_log and (os.path.normpath(dir_name).split(os.sep)[-1].lower() in ["log", "logs"]):
                target = dir_name
            if not zip_log and (target.endswith(".log") or re.findall('.*\.log\.\d+.*\d$', target)):
                target = os.path.dirname(target)
        zip_folder.write(get_relpath(src_path, target))
    zip_folder.close()
    os.chdir(pwd)
    return zip_file


def cycle_list(src_path, abs_targets=[], add_dirs=True):
    targets = list_dir(src_path)
    if targets == [] and add_dirs:
        abs_targets.append(src_path)
        return
    for target in targets:
        abs_target = os.path.join(src_path, target)
        # 系统隐藏文件
        if get_attrib(abs_target) == 22:
            continue
        if os.path.isfile(abs_target):
            abs_targets.append(abs_target)
        else:
            cycle_list(abs_target, abs_targets)
    return abs_targets


def get_attrib(target):
    return int(win32file.GetFileAttributesW(target))


def __unzip(dst_folder, zip_file):
    zip_folder = zipfile.ZipFile(zip_file, 'r', allowZip64=True)
    for f in zip_folder.namelist():
        zip_folder.extract(f, dst_folder)


def compression_folder(src_folder, zip_file, zip_log=False):
    file_type = os.path.splitext(zip_file)[1].lower()
    if file_type == '.zip':
        return _zip(src_folder, zip_file, False)
    return None


def decompression_folder(dst_folder, zip_file):
    if is_zipfile(zip_file):
        __unzip(dst_folder, zip_file)
    pass


#################################################Folder Operate#######################################
def isdir(target):
    return os.path.isdir(target)


def makdir(target_dir):
    if not isdir(target_dir):
        os.mkdir(target_dir)


def makdirs(target_dir):
    if not isdir(target_dir):
        os.makedirs(target_dir)


def shutil_copytree(src_dir, dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(src_dir, dest_dir)


def norm_path(dirpath):
    return os.path.normpath(dirpath)


def list_dir(dir):
    if not os.path.isdir(dir):
        return []
    # return [item for item in os.listdir(dir) if item not in ['$RECYCLE.BIN', 'System Volume Information']]
    return os.listdir(dir)


def walk_dir(target_dir):
    name_list = []
    path_list = []
    dir_list = []

    if os.path.isdir(target_dir):
        for root, dirs, files in os.walk(target_dir):
            for f in files:
                name_list.append(f)
                path_list.append(os.path.join(root, f))
            for dir in dirs:
                dir_list.append(os.path.join(root, dir))
    return name_list, path_list, dir_list


#################################################File Operate#######################################
def isfile(target):
    return os.path.isfile(target)


def get_extension(target):
    return os.path.splitext(target)[1].lower()


def get_md5(target):
    obj = hashlib.md5()
    if not isfile(target):
        if not isinstance(target, bytes):
            target = target.encode("utf-8")
        obj.update(target)
    else:
        with open(target, 'rb') as f:
            obj.update(f.read())
    return obj.hexdigest()


def move_file(src_target, dest_target):
    if not isfile(src_target):
        print("Isn't file")
        return 1
    if isdir(dest_target):
        dest_target = os.path.join(dest_target, os.path.basename(src_target))
    if isfile(dest_target):
        os.remove(dest_target)
    shutil.move(src_target, dest_target)
    return 0


def copy_file(src_target, dest_target):
    if not isfile(src_target):
        print("Isn't file")
        return 1
    if isdir(dest_target):
        dest_target = os.path.join(dest_target, os.path.basename(src_target))

    if isfile(dest_target):
        os.remove(dest_target)
    shutil.copy2(src_target, dest_target)
    return 0


# Empty directory
def rmdirfile_bydate(dir, back_day=7):
    file_list = [os.path.join(dir, f) for f in list_dir(dir)]
    del_list = rmfiles(file_list, back_day)
    return del_list


# Delete old files
def rmoldfile_bydate(dir, mark="", back_day=7):
    file_list = [os.path.join(dir, f) for f in list_dir(dir) if mark in f]
    del_list = rmfiles(file_list, back_day)
    return del_list


# Delete a set of files.
def rmfiles(fileList, back_day=0):
    del_list = []
    for f in fileList:
        rst = rmfile(f, back_day)
        if rst:
            del_list.append(f)
    return del_list


# Delete single file
def rmfile(f, back_day=0):
    if not isfile(f):
        return False
    sub_day = struct_time(time_sub(time.time(), get_mtimestamp(f))).tm_yday - 1
    if back_day == -1:
        return False
    if (sub_day >= int(back_day)):
        try:
            os.remove(f)
            return True
        except Exception as e:
            print(e)
            return False


# filename
def get_basename(f):
    return os.path.basename(f)


# dirname
def get_dirname(f):
    return os.path.dirname(f)


# {filename:fileabspath}
def get_basenames_dict(files=[], key_lower=True):
    basenames = {}
    for f in files:
        key = get_basename(f)
        if key_lower:
            key = key.lower()
        basenames.update({key: f})
    return basenames


# File encoding scheme
def code_type(f):
    return chardet.detect(open(f, 'rb').read())["encoding"]


#################################################List Operate#######################################
# The item of list is converted to lowercase.
def list_lower(list):
    return [item.strip().lower() for item in list]


#################################################List Operate#######################################

#################################################Str Operate#######################################
def findChinese(text):
    res = re.findall(u"[\u4e00-\u9fa5]", text)
    # \u4e00-\u9fa5是中文常用字段
    return len(res)


def ljust_str(string, length=0, filler=" "):
    if length == 0 or length <= len(string):
        return string
    half_num = findChinese(string)
    strlen = len(string)
    addin = (length - strlen - half_num) * filler
    return string + addin


def encodeStr(itemStr):
    if not isinstance(itemStr, bytes):
        # itemStr = unicode(itemStr, 'utf-8')
        itemStr = itemStr.encode('utf-8')
    return itemStr


def decodeStr(itemStr):
    if isinstance(itemStr, bytes):
        # itemStr = unicode(itemStr, 'utf-8')
        itemStr = itemStr.decode('utf-8')
    return itemStr


#################################################Str Operate#######################################

if __name__ == '__main__':
    pass
