/*
 * 立创开发板软硬件资料与相关扩展板软硬件资料官网全部开源
 * 开发板官网：www.lckfb.com
 * 技术支持常驻论坛，任何技术问题欢迎随时交流学习
 * 立创论坛：https://oshwhub.com/forum
 * 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
 * 不靠卖板赚钱，以培养中国工程师为己任
 * Change Logs:
 * Date           Author       Notes
 * 2024-06-14     LCKFB-LP    first version
 */
 
#include "bsp_i2c.h"
#include "stdio.h"

void IIC_INIT(void)
{
	I2C_InitTypeDef I2C_InitStruct;
    
	//时钟初始化
	RCC_I2C_ENABLE();
	RCC_DBG_ENABLE();

    //IO口初始化
    GPIO_InitTypeDef GPIO_InitStructure;
    PB10_AFx_I2C1SCL();
    PB11_AFx_I2C1SDA();
    GPIO_InitStructure.Pins = GPIO_SCL | GPIO_SDA;
    GPIO_InitStructure.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStructure.Speed = GPIO_SPEED_HIGH;
    GPIO_Init(GPIO_PORT_I2C, &GPIO_InitStructure);
    //I2C初始化
    I2C_InitStruct.I2C_BaudEn = ENABLE;
    I2C_InitStruct.I2C_Baud = 0xF;//500K=(8000000/(8*(1+1))
    I2C_InitStruct.I2C_FLT = DISABLE;
    I2C_InitStruct.I2C_AA = DISABLE;

    I2C_Deinit();
    I2C_Master_Init(I2C_PORT, &I2C_InitStruct); //初始化模块
    I2C_Cmd(I2C_PORT, ENABLE); //模块使能
	
	// Debug Port 初始化
	GPIO_InitTypeDef GPIO_InitStruct_DBG;

	GPIO_InitStruct_DBG.Pins = GPIO_DBG;				// GPIO调试引脚
	GPIO_InitStruct_DBG.Mode = GPIO_MODE_OUTPUT_PP;	// 推挽输出
	GPIO_Init(GPIO_PORT_DBG, &GPIO_InitStruct_DBG);	// 初始化调试引脚

	DBG(1); // 设置调试引脚高电平
	DBG(0); // 设置调试引脚高电平
	DBG(1); // 设置调试引脚高电平
	DBG(0); // 设置调试引脚高电平
}

void IIC_DEINIT(void)
{
    GPIO_DeInit(GPIO_PORT_I2C, GPIO_SCL|GPIO_SDA); // 复位I2C引脚
	GPIO_DeInit(GPIO_PORT_DBG, GPIO_DBG);
	I2C_Deinit();
}

uint8_t IIC_Read(uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len)
{
    uint8_t i = 0, state, uc_err_time = 0;
    
	DBG(1); // 设置调试引脚高电平
    I2C_GenerateSTART(I2C_PORT, ENABLE);
	DBG(0); // 设置调试引脚高电平
    while (uc_err_time++ < 250)
    {
        while (0 == I2C_GetIrq(I2C_PORT))
        {}
        state = I2C_GetState(I2C_PORT);
        switch (state)
        {
            case 0x08:   //发送完START信号
                I2C_GenerateSTART(I2C_PORT, DISABLE);
                I2C_Send7bitAddress(I2C_PORT, reg, 0X00);  //发送从机地址
                break;
            case 0x18:    //发送完SLA+W/R字节
                I2C_SendData(I2C_PORT, reg);
                break;
            case 0x28:   //发送完1字节数据：发送EEPROM中memory地址也会产生，发送后面的数据也会产生
                I2C_PORT->CR_f.STA = 1;  //set start        //发送重复START信号,START生成函数改写后，会导致0X10状态被略过，故此处不调用函数
                break;
            case 0x10:   //发送完重复起始信号
                I2C_GenerateSTART(I2C_PORT, DISABLE);
                I2C_Send7bitAddress(I2C_PORT, I2C_SLAVEADDRESS, 0X01);
                break;
            case 0x40:   //发送完SLA+R信号，开始接收数据
                if (len > 1)
                {
                    I2C_AcknowledgeConfig(I2C_PORT, ENABLE);
                }
                break;
            case 0x50:   //接收完一字节数据，在接收最后1字节数据之前设置AA=0;
                buf[i++] = I2C_ReceiveData(I2C_PORT);
                if (i == len - 1)
                {
                    I2C_AcknowledgeConfig(I2C_PORT, DISABLE);
                }
                break;
            case 0x58:   //接收到一个数据字节，且NACK已回复
                buf[i++] = I2C_ReceiveData(I2C_PORT);
                I2C_GenerateSTOP(I2C_PORT, ENABLE);
                break;
            case 0x38:   //主机在发送 SLA+W 阶段或者发送数据阶段丢失仲裁  或者  主机在发送 SLA+R 阶段或者回应 NACK 阶段丢失仲裁
                I2C_GenerateSTART(I2C_PORT, ENABLE);
                break;
            case 0x48:   //发送完SLA+R后从机返回NACK
                I2C_GenerateSTOP(I2C_PORT, ENABLE);
                I2C_GenerateSTART(I2C_PORT, ENABLE);
                break;
            default:
                I2C_GenerateSTART(I2C_PORT, ENABLE);//其他错误状态，重新发送起始条件
                break;
        }
        I2C_ClearIrq(I2C_PORT);
        if (i == len)
        {
            break;
        }
    }
    printf("%x %d %d\r\n", state, uc_err_time, i);
	return 0;
}

uint8_t IIC_Write(uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len)
{
	uint8_t i = 0, state, uc_err_time = 0;
    I2C_GenerateSTART(I2C_PORT, ENABLE);
    while (uc_err_time++ < 250)
    {
        while (0 == I2C_GetIrq(I2C_PORT))
        {;}
        state = I2C_GetState(I2C_PORT);
        switch (state)
        {
            case 0x08:   //发送完START信号
                I2C_GenerateSTART(I2C_PORT, DISABLE);
                I2C_Send7bitAddress(I2C_PORT, addr, 0X00); //从设备地址发送
                break;
            case 0x18:   //发送完SLA+W信号,ACK已收到
                I2C_SendData(I2C_PORT, reg); //从设备内存地址发送
                break;
            case 0x28:   //发送完1字节数据：发送EEPROM中memory地址也会产生，发送后面的数据也会产生
                I2C_SendData(I2C_PORT, buf[i++]);
                break;
            case 0x20:   //发送完SLA+W后从机返回NACK
            case 0x38:    //主机在发送 SLA+W 阶段或者发送数据阶段丢失仲裁  或者  主机在发送 SLA+R 阶段或者回应 NACK 阶段丢失仲裁
                I2C_GenerateSTART(I2C_PORT, ENABLE);
                break;
            case 0x30:   //发送完一个数据字节后从机返回NACK
                I2C_GenerateSTOP(I2C_PORT, ENABLE);
                break;
            default:
                break;
        }
        if (i > len)
        {
            I2C_GenerateSTOP(I2C_PORT, ENABLE);//此顺序不能调换，出停止条件
            I2C_ClearIrq(I2C_PORT);
            break;
        }
        I2C_ClearIrq(I2C_PORT);
    }
    printf("%x %d %d\r\n", state, uc_err_time, i);
	return 0;
}
