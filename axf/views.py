import hashlib
import os
import uuid

from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from Python1809 import settings
from axf.models import Wheel, Nav, Mustbuy, Shop, MainShow, Foodtypes, Goods, User, Cart

# 首页
def home(request):
    # 轮播图数据
    wheels = Wheel.objects.all()

    # 导航栏数据
    nav = Nav.objects.all()
    # 每日必购数据
    mustbuys = Mustbuy.objects.all()

    # 商品数据
    shoplist = Shop.objects.all()
    shophead = shoplist[0]
    shoptab = shoplist[1:3]
    shopclass = shoplist[3:7]
    shopcommend = shoplist[7:11]

    # 商品主体部分
    mainshows = MainShow.objects.all()

    data = {
        'title': '我的',
        'wheels': wheels,
        'nav': nav,
        'mustbuys': mustbuys,
        'shophead': shophead,
        'shoptab': shoptab,
        'shopclass':shopclass,
        'shopcommend': shopcommend,
        'mainshows': mainshows,
    }
    return render(request,'home/home.html',context=data)

# 购物市场
def market(request,categoryid, childid, sortid):
    # 分类数据
    foodtypes = Foodtypes.objects.all()
    typeIndex = int(request.COOKIES.get('typeIndex', 0))
    print(foodtypes[typeIndex])
    categoryid = foodtypes[typeIndex].typeid
    # 子类
    childtypenames = foodtypes.get(typeid=categoryid).childtypenames # 对应分类下 子类字符串
    childlist = []
    for item in childtypenames.split('#'):
        arr = item.split(':')
        obj = {'childname':arr[0], 'childid':arr[1]}
        childlist.append(obj)

    # 商品数据
    # goodslist = Goods.objects.all()[1:10]

    # 根据商品分类 数据过滤
    if childid == '0':  # 全部分类
        goodslist = Goods.objects.filter(categoryid=categoryid)
    else:   # 对应分类
        goodslist = Goods.objects.filter(categoryid=categoryid, childcid=childid)

    # 排序处理
    if sortid == '1':   # 销量排序
        goodslist= goodslist.order_by('productnum')
    elif sortid == '2': # 价格最低
        goodslist= goodslist.order_by('price')
    elif sortid == '3': # 价格最高
        goodslist= goodslist.order_by('-price')


    # 购物车数量问题
    token = request.session.get('token')
    carts = []
    if token:
        user = User.objects.get(token=token)
        carts = Cart.objects.filter(user=user).exclude(number=0)

    data = {
        'title': '闪购超市',
        'foodtypes':foodtypes,
        'goodslist':goodslist,
        'childlist':childlist,
        'categoryid':categoryid,
        'childid':childid,
        'carts': carts
    }


    return render(request,'market/market.html',context=data)

# 购物车
def cart(request):
    token = request.session.get('token')
    if token:  # 显示该用户下 购物车信息
        user = User.objects.get(token=token)
        carts = Cart.objects.filter(user=user).exclude(number=0)

        return render(request, 'cart/cart.html', context={'carts': carts})
    else:  # 跳转到登录页面
        return redirect('axf:login')
# 我的
def mine(request):
    token = request.session.get('token')
    responseData = {
        'title':'我的',
        'wait_pay':'wait_pay',
        'payed':'payed',
    }
    if token:
        user = User.objects.get(token=token)
        responseData['account'] = user.account
        responseData['img'] = '/static/uploads/' + user.img
        responseData['rank'] = 100
        responseData['islogin'] = True
    else:
        responseData['account'] = '未登录'
        responseData['img'] = '/static/uploads/axf.png'
        responseData['rank'] = '无等级'
        responseData['islogin'] = False
    return render(request, 'mine/mine.html',context=responseData)
#  登录操作
def login(request):
    if request.method == 'GET':
        return render(request,'mine/login.html')
    elif request.method == 'POST':
        account = request.POST.get('account')
        password = request.POST.get('password')
        try:
            user = User.objects.get(account=account)
            if user.password != generate_password(password):
                return render(request,'mine/login.html',context={'error':'输入的密码有误！'})
            else:  #登录成功
                user.token = str(uuid.uuid5(uuid.uuid4(),'login'))
                user.save()
                # 持久化存储
                request.session['token'] = user.token
                return redirect('axf:mine')
        except:
            return render(request,'mine/login.html',context={'error':'输入的账号有误！'})
#　注册
def register(request):
    if request.method == 'POST':
        user = User()
        # 用户账号
        user.account = request.POST.get('account')
        # 用户密码加密
        user.password = generate_password(request.POST.get('password'))
        # 用户名
        user.name = request.POST.get('name')
        # 电话
        user.tel = request.POST.get('tel')
        # 地址
        user.address = request.POST.get('address')
        # 头像
        imgName = user.account + '.png'
        imgPath = os.path.join(settings.MEDIA_ROOT, imgName)
        print(imgPath)
        file = request.FILES.get('file')
        print(file)
        with open(imgPath, 'wb') as fp:
            for data in file.chunks():
                fp.write(data)
        user.img = imgName

        # token
        user.token = str(uuid.uuid5(uuid.uuid4(), 'register'))
        # 用户保存
        user.save()
        # 状态保持
        request.session['token'] = user.token
        # 注册成功之后的重定向
        return redirect('axf:mine')

    elif request.method == 'GET':
        return render(request,'mine/register.html')

# 密码
def generate_password(password):
    sha = hashlib.sha512()
    sha.update(password.encode('utf-8'))
    return sha.hexdigest()
# 退出登录
def quit(request):
    logout(request)
    return redirect('axf:mine')


def addcart(request):
    goodsid = request.GET.get('goodsid')
    token = request.session.get('token')

    responseData = {
        'msg': '添加购物车成功',
        'status': 1  # 1标识添加成功，0标识添加失败，-1标识未登录
    }

    if token:  # 登录 [直接操作模型]
        # 获取用户
        user = User.objects.get(token=token)
        # 获取商品
        goods = Goods.objects.get(pk=goodsid)

        # 商品已经在购物车，只修改商品个数
        # 商品不存在购物车，新建对象（加入一条新的数据）
        carts = Cart.objects.filter(user=user).filter(goods=goods)
        if carts.exists():  # 修改数量
            cart = carts.first()
            cart.number = cart.number + 1
            cart.save()
            responseData['number'] = cart.number
        else:  # 添加一条新记录
            cart = Cart()
            cart.user = user
            cart.goods = goods
            cart.number = 1
            cart.save()

            responseData['number'] = cart.number

        return JsonResponse(responseData)
    else:  # 未登录 [跳转到登录页面]
        # 由于addcart这个是 用于 ajax操作， 所以这里是不能进行重定向!!
        # return redirect('axf:login')
        responseData['msg'] = '未登录，请登录后操作'
        responseData['status'] = -1
        return JsonResponse(responseData)


def subcart(request):
    token = request.session.get('token')
    goodsid = request.GET.get('goodsid')
    user = User.objects.get(token=token)
    goods = Goods.objects.get(pk=goodsid)
    # 删减操作
    cart = Cart.objects.filter(user=user).filter(goods=goods).first()
    cart.number = cart.number - 1
    cart.save()
    responseData = {
        'msg':'删减成功！',
        'status': 1,
        'number': cart.number,
    }
    return JsonResponse(responseData)


# def changecartstatus(request):
#     cartid = request.GET.get('cartid')
#     cart = Cart.objects.get(pk=cartid)
#     cart.isselect = not cart.isselect
#     cart.save()
#     responseData = {
#
#     }
#     return JsonResponse(responseData)