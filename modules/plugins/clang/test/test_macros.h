#ifndef TEST_MACROS_H
#define TEST_MACROS_H


#include "fake.h"

#ifndef MAX
#define MAX 100
#endif


#if defined(MIN)
#undef MIN
#define MIN 0
#endif

#define E_OK (0)

static inline int square(int x) {
    return SQUARE(x);
}

static inline int check(void){
    return (MAX > MIN) ? E_OK : -1;
}
#endif
