#!/usr/bin/python3
# coding=utf-8
#
# @author Space
# @date 2020/12/31 16:45


import getopt
import os
import sys
import json


def md5sum(path) -> str:
    """
    调用系统命令md5sum 计算文件哈希值
    :param path:
    :return:
    """
    result = os.popen("md5sum " + path)
    for t in result.readlines():
        return t.split(" ")[0]


def walk(path: str) -> dict:
    """
    遍历目标路径并返回所有文件哈希值
    :param path:
    :return:
    """
    m = {}
    result = []  # 所有的文件
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise Exception("path %s not exist" % path)
    if os.path.isfile(abs_path):
        result.append(abs_path)
    else:
        for maindir, subdir, file_name_list in os.walk(path):
            for filename in file_name_list:
                apath = os.path.join(maindir, filename)  # 合并成一个完整路径
                result.append(os.path.abspath(apath))
    for f in result:
        m[f] = md5sum(f)
    return m


def usage():
    print("usage:")
    print("calculate md5sum e.g. :")
    print("python md5check.py sum -p /home/space/projects/xxx")
    print("-p --> the path to calculate md5sum\n")
    print("check md5sum e.g. :")
    print("python md5check.py sum -p /home/space/projects/xxxxxx -s /home/space/md5sum.json")
    print("-p --> the path to check md5sum")
    print("-s --> the original file md5sum value")


if __name__ == '__main__':
    arg_num = len(sys.argv)
    if arg_num < 4:
        usage()
        exit(1)
    action = sys.argv[1]
    if action not in ("sum", "check"):
        usage()
        exit(1)
    opts, args = getopt.getopt(sys.argv[2:], "-p:-s:", ["--path", "--sum-file"])
    _path = ''
    _sum_file = 'md5sum.json'
    for opn, opv in opts:
        if opn in ("-p", "--path"):
            _path = opv
        if opn in ("-s", "--sum-file"):
            _sum_file = opv
    if action == "check" and (not _sum_file or not os.path.exists(_sum_file)):
        raise Exception("sum file not found")
    # 计算目标路径所有文件哈希
    _m = walk(_path)
    if action == "sum":
        with open(_sum_file, "w", encoding="utf-8") as _sf:
            json.dump(_m, _sf)
            print("calculate path md5sum success -> %s" % os.path.abspath(_sum_file))
    else:
        with open(_sum_file, "r", encoding="utf-8") as _tsf:
            all_is_same = True
            _tm = json.load(_tsf)
            _current_file_sets = set(_m.keys())
            _ori_file_sets = set(_tm.keys())
            # 当前目录存在，原目录不存在
            _diff_files1 = _current_file_sets - _ori_file_sets
            if len(_diff_files1) > 0:
                all_is_same = False
                print("files bellow is not found in the sum file set: ")
                for _df1 in _diff_files1:
                    print(_df1)
            # 原目录存在，当前目录不存在
            _diff_files2 = _ori_file_sets - _current_file_sets
            if len(_diff_files2) > 0:
                all_is_same = False
                print("files bellow is not found in the current file set: ")
                for _df2 in _diff_files2:
                    print(_df2)
            _intersection = _current_file_sets & _ori_file_sets
            _not_matched = []
            for _if in _intersection:
                if _tm[_if] != _m[_if]:
                    _not_matched.append((_if, _tm[_if], _m[_if]))
            if len(_not_matched) > 0:
                all_is_same = False
                print("the md5sum of files bellow are not matched. details: ")
                print("file\toriginal\tcurrent")
                for _nf in _not_matched:
                    print(_nf[0] + "\t" + _nf[1] + "\t" + _nf[2])
            if all_is_same:
                print("all files are same!")