import requests
from data import *
from checks import *
import time
from parameter import *
from qq_email import error_mail
from qq_email import right_mail
import os


def load_user():
    """
    :return:返回用户数据
    """
    user_list = eval(os.environ['USERS'])
    text = str(os.environ['DATA'])
    data_list = []
    data_dict = {}
    iter = find.finditer(text)
    for j in iter:
        key = j.group('key')
        value = j.group('value')
        data_dict[key] = value
        if key == 'askforleave':
            data_list.append(data_dict.copy())
            data_dict.clear()

    return user_list, data_list


def main(user, post_data):
    flag = 0
    RETURN_EMAIL = user['mail']
    session = requests.Session()
    account = user['user']
    pswd = user['pswd']
    id = user['id']
    while True:
        try:

            flag += 1
            if flag > MAX_NUM:
                error = '[{}]失败次数过多，其填报已终止'.format(user['id'])
                raise ZeroDivisionError(error)

            resp1 = session.post(check_url, headers=head, data=get_logindata(account, pswd))
            # 登陆
            message = re_message.search(resp1.text).groups()[0]
            message_check(message)
            # 检测登陆信息

            get_data = get_postdata(post_data)
            resp2 = session.post(post_url, headers=head, data=get_data)
            # 填报数据

            if resp1.status_code != 200:
                main_logger.warning('用户[{}]登陆失败，状态码不是200'.format(id))
                time.sleep(15)
                # 延迟一段时间后重试
                continue
            else:
                main_logger.info('{}登陆成功'.format(user['id']))

            if resp2.status_code != 200:
                main_logger.warning('用户[{}]填报失败，状态码不是200'.format(id))
                time.sleep(15)
                # 延迟一段时间后重试
                continue
            else:
                main_logger.info('{}填报成功'.format(user['id']))

            break
        #     正常执行一次结束

        except ZeroDivisionError as mes:
            print(mes)
            main_logger.error(str(mes))
            if RETURN_EMAIL:
                error_mail(user, get_log())

        except RuntimeWarning as mes:
            print(str(mes) + '请检查输入的账户信息')
            if RETURN_EMAIL:
                error_mail(user, str(mes) + '请检查输入的账户信息')
            exit(-1)
        #     登陆时会出现的错误
        #     随便找了两个错误来捕捉
    session.close()


if __name__ == '__main__':
    user_list, data_list = load_user()
    length = len(user_list)
    for i in range(length):
        try:
            main(user_list[i], data_list[i])
            if user_list[i]['mail']:
                if DATA_RETURN:
                    right_mail(user_list[i], str(data_list[i]))
                else:
                    right_mail(user_list[i])


        except Exception as e:
            print(repr(e))
            other_logger.error(repr(e))
            if user_list[i]['mail']:
                error_mail(user_list[i], get_log())
