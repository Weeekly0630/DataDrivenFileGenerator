#include "fake.h"

/* VAR Type macro */
#define VAR(TYPE, STORAGE) TYPE

#define ASSERT(expr) \
    do { \
        if (!(expr)) { \
            printf("Assertion failed: %s, file %s, line %d\n", #expr, __FILE__, __LINE__); \
            exit(EXIT_FAILURE); \
        } \
    } while (0)
    
#define INIT_ARRAY         { 1, 2, 3 }
// 全局变量，带注释
static const int g_value = 42;

struct __attribute__((packed)) Point
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

int          array[]      = INIT_LIST;
int          array1[2][3] = { INIT_LIST, INIT_LIST };
struct Point pt           = { 1, 2 };

/* wth */
Rectangle rect = { { 0, 0 }, { 10, 10 } };

VAR(Rectangle, AUTO) rect2 = { { 1, 1 }, { 5, 5 } };