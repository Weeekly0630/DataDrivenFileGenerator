
/**
 * @brief Macro to calculate the square of a number.
 * 
 */
#define SQUARE(x) ((x) * (x))

typedef unsigned int uint32_t;

typedef struct {
    int a;
    uint32_t b0: 1; // 1-bit bitfield
    uint32_t b1: 3; // 3-bit bitfield
    uint32_t b2: 4; // 4-bit bitfield
    uint32_t b_rsvd: 24; // 24-bit reserved bitfield
} MyStruct;

uint32_t var = 0U;

MyStruct s = { .a = 10 };


/**
 * @brief Foo function that returns a MyStruct instance. but i have more comments.
 * 
 * @param x 
 * @return MyStruct 
 */
MyStruct foo(uint32_t x);

/**
 * @brief Foo function that returns a MyStruct instance.
 * 
 * @param x 
 * @return MyStruct 
 */
MyStruct foo(uint32_t x) {
    return (MyStruct){.a = x};
}