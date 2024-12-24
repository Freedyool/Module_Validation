#include <linux/init.h>
#include <linux/module.h>

//内核模块的三要素 （面试）
//入口函数 向内核申请资源
static int __init demo_init(void)
{
    //__init 用来修饰demo_init函数的 作用是将这个函数放到init代码段中
    //__init被定义在init.h中  #define __init		__section(.init.text)
    //section 这个属性 是用来告诉编译器(linux gcc)  被修饰的变量或函数 在编译可执行文件时 放到特定的段中
    return 0;
}

//出口函数 释放向内核申请的资源
static void __exit demo_exit(void)
{

}

//修饰模块化驱动的入口函数
module_init(demo_init);

//修饰模块化驱动的出口函数
module_exit(demo_exit);

//许可证 遵循GPL开源协议
MODULE_LICENSE("GPL");