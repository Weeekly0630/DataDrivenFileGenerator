#ifndef MCAL_EXAMPLE_H
#define MCAL_EXAMPLE_H

#include <stdint.h>
#include <stdbool.h>

/* MCAL Version Info */
#define MCAL_VENDOR_ID        (123U)
#define MCAL_MODULE_ID        (456U)
#define MCAL_SW_MAJOR_VERSION (1U)
#define MCAL_SW_MINOR_VERSION (0U)
#define MCAL_SW_PATCH_VERSION (0U)

/* Error Codes */
typedef enum {
    MCAL_OK = 0,
    MCAL_ERROR = 1,
    MCAL_TIMEOUT = 2
} Mcal_StatusType;

/* Callback function type */
typedef void (*Mcal_CallbackType)(void);

/* Structure for configuration */
typedef struct {
    uint32_t configId;
    bool enableFeature;
    Mcal_CallbackType callback;
} Mcal_ConfigType;

/* Global variable */
extern Mcal_ConfigType gMcalConfig;

/* Function declarations */
void Mcal_Init(const Mcal_ConfigType* config);
Mcal_StatusType Mcal_DoAction(int param);
void Mcal_RegisterCallback(Mcal_CallbackType cb);
uint32_t Mcal_GetVersion(void);

#endif /* MCAL_EXAMPLE_H */