#include "mcal_example.h"

// #include <stdio.h>

#define EXAMPLE_MACRO 100

#define MULTI_LINE_MACRO(a, b) \
    do                         \
    {                          \
        a += b;                \
        b += a;                \
    } while (0)

/**
 * @brief Example enumeration
 *
 */
typedef enum
{
    /**
     * @brief Red color Multi Line Comment
     *
     */
    RED,
    // Single Line Comment
    GREEN,
    /* Single line Comment */
    BLUE,
    YELLOW,  // Trailing Comment
} COLOR_Type;

/*!
 * @brief Color
 *
 */
enum COLOR
{
    /* Comment RED */
    REDD,
    /* Comment GREEN */
    GREENN,
    // Comment Bule
    BULEE
};

/* Global variable definition */
Mcal_ConfigType gMcalConfig = { 0, false, NULL };

/**
 * @brief Example internal structure
 *
 */
typedef struct
{
    int   id;       /* aaa */
    char  name[32]; /* aaa */
    float value;    /* aaa */
} Mcal_InternalStructType;

/* Static variable */
static uint32_t s_internalState = 0;

/* Static function */
static void
Mcal_InternalFunction(void)
{
    s_internalState++;
    Mcal_InternalStructType s_internalStruct = { 1, "InternalStruct", 3.14f };
}

/**
 * @brief Mcal_Init
 * 
 * @param config 
 */
void
Mcal_Init(const Mcal_ConfigType* config)
{
    if (config != NULL)
    {
        gMcalConfig     = *config;
        s_internalState = config->configId;
        if (gMcalConfig.callback)
        {
            gMcalConfig.callback();
        }
    }
}

Mcal_StatusType
Mcal_DoAction(int param)
{
    Mcal_InternalFunction();
    if (param < 0)
    {
        return MCAL_ERROR;
    }
    else if (param == 0)
    {
        return MCAL_TIMEOUT;
    }
    return MCAL_OK;
}

void
Mcal_RegisterCallback(Mcal_CallbackType cb)
{
    gMcalConfig.callback = cb;
}

uint32_t
Mcal_GetVersion(void)
{
    return (MCAL_SW_MAJOR_VERSION << 16) | (MCAL_SW_MINOR_VERSION << 8)
           | (MCAL_SW_PATCH_VERSION);
}

/* Example callback function */
void
Example_Callback(void)
{
    // printf("Callback called!\n");
}