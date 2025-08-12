struct Point
{
    int x;
    int y;
};

typedef struct Rectangle
{
    struct Point top_left;
    struct Point bottom_right;
} Rectangle;

struct UART_REG
{
    unsigned int DATA : 8;  // 数据寄存器
    unsigned int STATUS : 8;
    unsigned int CONTROL : 8;    // 控制寄存器
    unsigned int BAUD_RATE : 8;  // 波特率寄存器
    int          data[100];
};

struct Point pt = { 1, 2 };

Rectangle rect = { { 0, 0 }, { 10, 10 } };