struct Point {
    int x;
    int y;
};

struct Rectangle {
    struct Point top_left;
    struct Point bottom_right;
};

struct Point p1 = {10, 20};

typedef struct Rectangle Rectangle_t;