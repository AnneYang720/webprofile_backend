# **Summer2021-一个对用户友好的 web profile 工具**

#### **介绍**

社区：MegEngine（天元）

项目：一个对用户友好的 web profile 工具

项目编号：210040021

简介：

本项目完成了一个对用户友好的 web profile 工具，其中前端负责收集模型、管理任务、可视化、显示 profile 结果等；Server端负责处理请求

管理数据库等；Worker端负责实际跑模型。

项目地址：

https://gitlab.summer-ospp.ac.cn/summer2021/210040021

https://gitlab.summer-ospp.ac.cn/summer2021/210040021-2



#### 使用说明

web profile 工具的项目背景、系统设计和使用说明请见项目仓库中的《项目功能说明书.pdf》



#### 安装教程

##### Step 1 获取代码

```shell
$ git clone https://gitlab.summer-ospp.ac.cn/summer2021/210040021.git frontend
$ git clone https://gitlab.summer-ospp.ac.cn/summer2021/210040021-2.git backend
```

此时当前目录下应有代码结构如下：

```
.
├── frontend/ - 前端
├── backend/ 
	├── deploy/ - 部署文件
	├── server/ - Server端
	├── worker/ - Worker端
```



##### Step 2 Docker

```shell
# 构建前端镜像
$ docker build frontend/ -t webprofile_web:latest

# 构建nginx镜像
$ docker build frontend/nginx/ -t webprofile_nginx:latest

# 构建Server镜像
$ docker build backend/server/ -t webprofile_backend:latest

# 编辑容器配置文件, 更改APP_M_ENDPOINT为网站的URL
$ cp backend/deploy/config.example.env config.env
$ vim config.env

# 启动容器
$ cd backend/deploy/
$ docker-compose up
```