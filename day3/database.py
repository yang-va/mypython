#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os,random
data = open('staffdata',encoding='utf-8').read()
tempdata = data.split('\n')
li = ['id','name','age','phone','dept','enroll_date']
def select(field,condition):            # 查询数据函数
    condition = condition.strip()
    res = parser(condition)[-1]
    printline = []
    if field == '*':                    # 当待查看的字段为*时
        printline.extend(res)
        for some in printline:
            print('\t'.join(some))
        print('\033[32;1m查询到 %s 行数据\033[0m'%len(printline))
    else:                               # 当待查看的字段为详细的字段时，比如name,age....
        field = field.split(',')
        for line in res:
            for key in field:
                cont = line[li.index(key)]
                printline.append(cont)
        name = printline[::2]
        age = printline[1::2]
        cont = dict(zip(name,age))
        for n in cont:
            print(n+'\t'+cont[n])
        print('\033[32;1m查询到 %s 行数据\033[0m'%len(cont))

def calc_big(x,y):      # 计算条件为大于符号时，比如age>22
    prints = []
    for i in tempdata:
        i = i.split(',')
        if int(i[li.index(x)]) > y:
            prints.append(i)
    return x,y,prints

def calc_sma(x,y):      # 计算条件为大于符号时，比如age<22
    prints = []
    for i in tempdata:
        i = i.split(',')
        if int(i[li.index(x)]) < y:
            prints.append(i)
    return x,y,prints

def calc_eq(x,y):       # 计算条件为=符号时，比如age=22
    prints = []
    for i in tempdata:
        i = i.split(',')
        if isinstance(y,int):
            if int(i[li.index(x)]) == y:
                prints.append(i)
        else:
            if i[li.index(x)] == y:
                prints.append(i)
    return x,y,prints

def calc_like(x,y):     # 计算条件为like时，比如dept like 'IT'
    prints = []
    for i in tempdata:
        i = i.split(',')
        if i[li.index(x)].startswith(y):
            prints.append(i)
    return x,y,prints

def parser(condition):  # 分类解析条件函数
    calc = {
        '>':calc_big,
        '<':calc_sma,
        '=':calc_eq,
        'like':calc_like
    }

    for term,func in calc.items():
        if term in condition:
            condleft,condright = condition.split(term)
            condleft = condleft.strip()     # 去空格
            condright = eval(condright.strip()) # 去空格
            result = func(condleft,condright)
            break
    else:
        print('\033[31;1m语法错误\033[0m\n 只支持<,>,=,like')
    return result


def create(sql):    # 添加数据函数
    index = sql.find('add staff_table')+len('add staff_table ') # 截取需要的数据
    '以phone做唯一键(即不允许表里有手机号重复的情况)'
    addline = []
    line = sql[index:].split(',')
    head = tempdata[-1].split(',')[0]                           # 待添加数据的开头文件，即索引
    newline = str(int(head)+1)+','+sql[index:]
    tempdata.append(newline)
    addline.append(newline)
    for i in tempdata:
        if i == tempdata[-1]:
            break
        last = i.split(',')
        if line[li.index('phone')-1] == last[li.index('phone')]:
            print('\033[31;1m已存在相同手机号，请输入其他手机号\033[0m')
            tempdata.pop()
            addline.pop()
    print('\033[32;1m添加 %s 行数据\033[0m'%len(addline))

def update(sql):    # 修改数据函数
    global tempdata
    if 'staff_table' in sql:
        # 把sql内的重要字段重新处理为程序可识别的格式
        important = sql[sql.find('SET')+len('SET '):].split('where')
        newkv,oldkv = important
        oldkey,oldvalue,res = parser(oldkv)
        newkey,newvalue = parser(newkv)[0],parser(newkv)[1]
        oldkey = oldkey.strip()
        newkey = newkey.strip()
        if isinstance(oldvalue,int):        # 如果是数字转为数字
            oldvalue = str(oldvalue).strip()
        if isinstance(newvalue,int):
            newvalue = int(newvalue)        # 如果是数字转为数字
        oldvalue = str(oldvalue).strip()
        newvalue = str(newvalue).strip()  # 去空格，转换引号，转为可识别的字符串

        # 对比数据，修改数据
        current = []
        for cont in tempdata:
            last = cont.split(',')
            current.append(last)
        for cont in current:
            if cont in res:
                current[current.index(cont)][li.index(newkey)] = newvalue
        for thing in current:
            temp = ','.join(thing)
            current[current.index(thing)] = temp
        tempdata = current

    else:
        print('数据表名错误')
    print('\033[32;1m修改 %s 行数据\033[0m'%len(res))

def delete(condition):  # 删除数据函数
    condition = condition.strip()
    res = parser(condition)[-1]
    for i in res:
        t = ','.join(i)
        if t in tempdata:
            tempdata.remove(t)
    print('\033[32;1m删除 %s 行数据\033[0m'%len(res))
    del res

def resolve(sql):   # 解析输入的sql并分别处理
    if sql.split()[0] in ('find','FIND','del','DEL','update','UPDATE','add','ADD'):     # 当sql开头字段为增删改查时
        if 'where' in sql or 'WHERE' in sql:                 # 当sql参数内有where字段时
            sql = sql.replace('WHERE','where')
            sqlleft,sqlright = sql.split('where')
            # print(sqlleft.split()[0])
            if sqlleft.split()[0] in ('find','FIND'):
                start = sqlleft.find('find')+len('find')
                end = sqlleft.find('from')
                field = sqlleft[start:end].strip()
                select(field,sqlright)

            if sqlleft.split()[0] in ('del','DEL'):
                delete(sqlright)
            if sqlleft.split()[0] in ('update','UPDATE'):
                update(sql)

        else:   # 当sql参数内无where字段时，即为添加数据sql语句时
            create(sql)
    else:       # 当sql开头字段不为增删改查时
        print('\033[31;1m语法错误\033[0m\nfind/del/update/create [columns] from staff [columns]')

def myquit():
    os.rename('staffdata','staffdata%s.bk'%random.randint(0,100))       # 备份初始数据
    with open('staffdata','w',encoding='utf-8') as f:
        for i in tempdata:
            if tempdata[-1] == i:   # 当i为数据的最后一行时,不用添加换行符
                f.write(i)
            else:
                f.write(i+'\n')
    exit()
def main():     # 主程序入口函数
    while True:
        print('----------------------员工信息表-------------------')
        print('\t'.join(li))
        for line in tempdata:
            one = line.split(',')
            print(one[0]+'\t\t'+one[1]+'\t\t'+one[2]+'\t\t'+one[3]+'\t\t'+one[4]+'\t\t'+one[5])
        print('--------------------------------------------------')
        ctrl = input('sql(输入“q”退出)>: ').strip()
        if ctrl in ('q','Q','exit','quit'):
            myquit()
        resolve(ctrl)
main()
