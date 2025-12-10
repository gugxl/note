# Unity 学习

基础语言 C# 不进行记录了

[中文官方文档](https://docs.unity.cn/cn/2022.3/Manual/ProjectView.html)

视频 B站 unity教程零基础全套2025最新合集（unity游戏开发教程+unity3D游戏教程+unity2D游戏教程）unity游戏制作教程，unity下载安装教程

安装使用UnityHub安装Unity 2023

![unityhub主页面.png](img/unityhub主页面.png)

![Unity主页面.png](img/Unity主页面.png)

## 生命周期

常用生命周期函数
![生命周期.png](img/生命周期.png)

会在运行时自动调用，都继承 自 MonoBehaviour

说明：
-  Reset()
    -  调用情况：只在程序不运行的时候调用
    - 调用时间： 当脚本第一次挂载到对象上的时候，或使用Reset命令调用的时候
    - 调用次数：只会调用一次；
    - 作用：初始化脚本的各个属性
- Awake()
  - 调用情况：1. 在调用场景时；2. GameObject从未激活状态变为激活状态；3. 在初始化使用instantiate创建GameObject之后
  - 调用时间： 脚本实例的生命周期内
  - 调用次数：仅调用一次
- OnEnable()
  - 调用情况： 依附的GameObject每次被激活的时候调用
  - 调用时间、次数、作用：每次GameObject对象或脚本被激活时调用一次；重复赋值；变为初始状态
- Start()
  - 调用情况：进行每一帧更新之前才会执行，只有在GameObject被激活后才会被调用
  - 在Awake之后。Update之前执行，方便控制逻辑的先后调用顺序
- Fixed Update()
  - 主要用于物理更新，每个固定时间间隔执行。时间设置在 Project setting -> Time -> Fixed Timestep中设置 
- Update()
  - 主要用于处理游戏核心逻辑更新
  - 实时更新数据吗，接受输入数据，每帧调用，每秒60次左右
- Late Update()
  - 一般用于处理摄像机位置更新相关内容，Update和Late Update之间，Unity进行了一些处理，对动画相关的更新，影响渲染的结果，如果在Update中更新摄像机，即摄像机位置变化后再更新动画可能会出现渲染错误，其运行帧率和Update相同
- OnDisable()
  - 当对象被禁用是调用，脚本被禁用时，游戏对象被销毁时调用
  - 作用：对于一些状态的重置，资源回收与清理
- OnApplicationQuit()
  - 在程序退出之前所有的游戏对象都会调用这个函数
  - 编辑器中用户终止播放模式时调用
  - 在网页视图关闭时
  - 满足上情况调用一次，用于处理游戏退出后的一些逻辑
- OnDestory()
  - 当物体被销毁时调用，对象存在的最后一帧更新完之后的所有Update函数执行完之后执行。
  - 用于销毁一下游戏物体
  - Destopry(GameObject, time)