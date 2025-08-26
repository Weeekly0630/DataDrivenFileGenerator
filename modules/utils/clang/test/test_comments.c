/**
 * @file test_comments.c
 * @brief Test file for all types of comments extraction
 */

// Single line comment before typedef
typedef struct {
    int x;     // Trailing comment for x
    char y;    /* C-style trailing comment for y */
    float z;   /**< Doxygen trailing comment for z */
} SimpleStruct;

/*
 * Multi-line C-style comment
 * before struct
 */
struct TestStruct {
    /** Doxygen style field comment */
    int field1;
    
    /*!
     * Qt style field comment
     * multiple lines
     */
    char field2;
    
    // Single line comment before field
    float field3;
    
    /* C-style comment before field */
    double field4;
    
    int field5;    // Trailing comment
    char field6;   /* C-style trailing */
    float field7;  /**< Doxygen trailing */
};

/// Single line doxygen comment
enum TestEnum {
    /** Doxygen style for FIRST */
    FIRST = 0,
    
    /*!
     * Qt style for SECOND
     * Multiple lines
     */
    SECOND,
    
    // Single line for THIRD
    THIRD,
    
    /* C style for FOURTH */
    FOURTH,
    
    FIFTH,   // Trailing for FIFTH
    SIXTH,   /* C-style trailing for SIXTH */
    SEVENTH  /**< Doxygen trailing for SEVENTH */
};

/*! 
 * Qt style function comment
 * @param x Description of x
 * @return Description of return
 */
int test_function(int x) {
    return x;
}

// Single line macro comment
#define MACRO_1 1

/* C-style macro comment */
#define MACRO_2 2

/** Doxygen style macro comment */
#define MACRO_3 3

/*!
 * Qt style macro comment
 * Multiple lines
 */
#define MACRO_4 4

/**
 * @brief Doxygen style macro comment
 * 
 * @param X First parameter
 * @param Y Second parameter
 * 
 * @return Sum of X and Y
 */
#define MACRO_5(X, Y) ((X) + (Y))
// Variable comments
/** Doxygen style variable */
int global_var1;

/*!
 * Qt style variable
 * Multiple lines
 */
char global_var2;

// Single line before variable
float global_var3;

/* C-style before variable */
double global_var4;

int global_var5;    // Trailing comment
char global_var6;   /* C-style trailing */
float global_var7;  /**< Doxygen trailing */
