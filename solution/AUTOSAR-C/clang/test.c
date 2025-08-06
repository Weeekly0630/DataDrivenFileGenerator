
// 基本类型别名
typedef unsigned int uint32;
typedef int sint32;
typedef float float32;

// 枚举类型
enum Color {
    RED = 0,
    GREEN = 1,
    BLUE = 2
};

typedef enum Color Color_t;

// 结构体定义
struct Point {
    int x;
    int y;
};

typedef struct Point Point_t;

// 联合体定义
union Data {
    int i;
    float f;
    char str[8];
};

// 带位域的结构体
struct Flags {
    unsigned int flag1 : 1;
    unsigned int flag2 : 1;
    unsigned int reserved : 6;
};

// 宏定义
#define MAX_SIZE 100
#define SQUARE(x) ((x)*(x))

// 全局变量
int global_var = 42;
static float static_var = 3.14f;
extern int extern_var;

// 函数声明
int add(int a, int b);
static void print_point(const struct Point* p);

// 函数定义
int add(int a, int b) {
    return a + b;
}

static void print_point(const struct Point* p) {
    printf("Point(%d, %d)\n", p->x, p->y);
}

// 主函数
int main(void) {
    struct Point p = {1, 2};
    union Data d;
    d.i = 10;
    print_point(&p);
    return add(p.x, d.i);
}
