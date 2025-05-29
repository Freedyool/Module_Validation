# Module_Validation

立创·地文星CW32F030C8T6开发板

## 环境搭建

推荐使用 vscode 打开根目录并安装 [EIDE](https://marketplace.visualstudio.com/items?itemName=CL.eide) 插件打开本项目；

项目预设的编译工具为：AC5 编译器；
项目预设的烧录工具为：DAP-Link + uv4；

烧录注意事项：

1. cw32f030 暂时没有适用于 OpenOCD 的官方 target 脚本，故不支持 OpenOCD 烧录；
2. 本项目使用脚本调用 uv4.exe 实现固件烧录，命令参见 `.eide/eide.json` 中的 `uploadConfig` 字段；
3. 烧录工具使用的是网购的 DAP-Link 模块连接 `CW32F030` 的 `GND`、`CLK`、`DIO` 和 `5V` pin 脚；
4. 更多烧录方式请参考 [LC-DWX](https://wiki.lckfb.com/zh-hans/dwx-cw32f030c8t6/beginner)；

## INA226

Source Code from: https://github.com/libdriver/ina226

### 移植说明

根据 ina226 源码中的说明，移植总体需要以下几个关键步骤：

1. 复制代码，将 src 和 interface 目录下的代码拷贝到本地项目代码中；
2. 参考 cw32f030 iic 例程，编写基本的 iic bsp 接口，此时就需要确定好使用具体哪组 GPIO，并且对 iic 的读写接口进行对应实现，本项目参考了 STM32F4 中的 bsp 代码，使用软件模拟出了一组 IIC 实现的数据访问；
3. 参考 project 目录中的 driver_ina226_interface.c 实现本地项目所在平台上的代码；
4. 将新增的代码添加进 EIDE 项目文件列表中（包括 include path）；
5. 参照 example 中的实现，编写 main 函数，调用 driver_ina226 的初始化和值读取函数；
6. 编译烧录测试；