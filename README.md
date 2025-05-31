# Module_Validation

立创·天空星STM32F407VxT6开发板

## 环境搭建

推荐使用 vscode 打开根目录并安装 [EIDE](https://marketplace.visualstudio.com/items?itemName=CL.eide) 插件打开本项目；

项目预设的编译工具为：AC5 编译器；
项目预设的烧录工具为：DAP-Link + OpenOCD；

项目创建流程：

1. 模板工程代码拷贝至 ModuleValidation 根目录；
2. EIDE 导入工程，验证编译功能正常（可能需要配置调整编译工具）；
3. 在 EIDE 界面调整烧录器配置（根据你自己的烧录器以及手册选择合适的烧录方式）；