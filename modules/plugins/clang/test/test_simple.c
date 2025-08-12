// test_simple.c
// 测试声明提取和宏保留流程

#define MAX 100
#define MIN 0

int a = MAX + 100;
int b = 100 + 100;
int c = 42;

// 结构体和typedef
struct Point
{
    int x;
    int y;
};
typedef struct Point Point;

Point p1 = { 1, 2 };

// 带宏的数组
int arr[MAX];

// 带宏的初始化
int d = MAX + MIN;

// 带注释的变量
int e = MAX;  // 需要保留MAX
