'''响应状态码
网页响应的对应的状态码
'''

class RET:
    OK                  = 20000
    FAIL                = 20001
    DBERR               = 4001
    NODATA              = 4002
    DATAEXIST           = 4003
    DATAERR             = 4004
    SESSIONERR          = 4101
    LOGINERR            = 4102
    PARAMERR            = 4103
    USERERR             = 4104
    ROLEERR             = 4105
    PWDERR              = 4106
    REQERR              = 4201
    IPERR               = 4202
    THIRDERR            = 4301
    IOERR               = 4302
    SERVERERR           = 4500
    UNKOWNERR           = 4501

error_map = {
    RET.OK                    : u"成功",
    RET.FAIL                  : u"失败",
    RET.DBERR                 : u"数据库查询错误",
    RET.NODATA                : u"无数据",
    RET.DATAEXIST             : u"数据已存在",
    RET.DATAERR               : u"数据错误",
    RET.SESSIONERR            : u"用户未登录",
    RET.LOGINERR              : u"用户登录失败",
    RET.PARAMERR              : u"参数错误",
    RET.USERERR               : u"用户不存在或未激活",
    RET.ROLEERR               : u"用户身份错误",
    RET.PWDERR                : u"密码错误",
    RET.REQERR                : u"非法请求或请求次数受限",
    RET.IPERR                 : u"IP受限",
    RET.THIRDERR              : u"第三方系统错误",
    RET.IOERR                 : u"文件读写错误",
    RET.SERVERERR             : u"内部错误",
    RET.UNKOWNERR             : u"未知错误",
}

# 成功20000
# 失败20001
# 用户名密码  20002
# 权限不 20003
# 程 用失败20004
# 复操作20005