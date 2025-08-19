#ifndef __FAKE_H__
#define __FAKE_H__

#define MAX 100
#define MIN 0

#define SQUARE(x) ((x) * (x))

#define MYTYPE int

#define INIT_LIST {1, 2, 3}

static inline int square(int x) {
    return SQUARE(x);
}

#endif
