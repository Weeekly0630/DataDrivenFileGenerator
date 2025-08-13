#define VAR(TYPE, STORAGE) TYPE
#define INIT_ARRAY         { 1, 2, 3 }
// 全局变量，带注释
static const int g_value = 42;

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
int array[] = INIT_ARRAY;

struct Point pt = { 1, 2 };

Rectangle rect = { { 0, 0 }, { 10, 10 } };

VAR(Rectangle, AUTO) rect2 = { { 1, 1 }, { 5, 5 } };