#ifndef TEST_MACROS_H
#define TEST_MACROS_H


#include "stdio.h"

#ifndef MAX
#define MAX 100
#endif

#if defined(MIN)
#undef MIN
#define MIN 0
#endif

#endif
