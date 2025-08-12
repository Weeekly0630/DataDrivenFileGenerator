// 基本类型变量
int a;

// 带注释的变量
/**
 * @brief 这是一个带注释的全局变量
 */
float b = 3.14;

// 指针变量
char *pStr;

// 多级指针变量
int **ppInt;

// 数组变量
int arr[10];

// 多维数组变量
unsigned char matrix[3][4];

// 指针数组
int *ptrArr[5];

// 数组指针
int (*arrPtr)[10];

// const/volatile/restrict 限定符
const int cval = 42;
volatile float vval;
int * restrict rptr;

// 结构体类型变量
struct Point {
    int x;
    int y;
};
struct Point pt = {1, 2};

// 匿名结构体变量
struct {
    int a;
    int b;
} anon_pt = {3, 4};

// typedef 类型变量
typedef double real_t;
real_t dval;

// 指向结构体的指针
struct Point *ppt;

// 带初始化表达式的变量
int sum = 1 + 2;

// 静态变量
static int s_var = 100;

// 外部变量声明
extern int ext_var;

// register变量
register int reg_var;

// 位域变量
struct Flags {
    unsigned int flag1 : 1;
    unsigned int flag2 : 2;
};
struct Flags flags = {1, 2};

// 复合声明
int x, *y, arr2[5], **z;

// 指向函数的指针
typedef int (*func_ptr_t)(int, int);
func_ptr_t fp;

// const指针和指向const的指针
int val = 0;
int * const cp1 = &val;
const int * cp2 = &val;

// 复杂初始化
int arr3[3] = {1, 2, 3};

// 带注释的指针变量
/**
 * @brief 这是一个带注释的指针变量
 */
char *commented_ptr;
