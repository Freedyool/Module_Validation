#include <linux/init.h>
#include <linux/module.h>


static int __init demo_init(void)
{
	//printk(消息等级 "格式化字符串",可变传参);
	//消息等级 共有8种 0-7 数值越小 优先级越高
	//4       			4       			1       			7
	//终端的消息级别			消息的默认级别				终端最大消息级别			终端最小消息级别

	//printk(KERN_ERR "hello world %s\n","init");
	printk("hello world %s\n","init");
    return 0;
}

static void __exit demo_exit(void)
{
	printk("hello world %s\n","exit");
}

module_init(demo_init); //这个函数会在 insmod加载驱动时 被调用

module_exit(demo_exit); //这个函数会在 rmmod卸载驱动时 被调用

MODULE_LICENSE("GPL");