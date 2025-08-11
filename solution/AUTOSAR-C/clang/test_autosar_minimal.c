
#include "mock_autosar.h"

/* AUTOSAR-style minimal test file for Clang AST parsing */

// #include "CDD_I2c.h"
// #include "I2c_Ipw.h"
// #include "I2c_FlexIO.h"
// #include "I2c_LPI2C.h"

#define I2C_IPW_VENDOR_ID_C 43
#define I2C_AR_RELEASE_MAJOR_VERSION_IPW_C 4
#define I2C_AR_RELEASE_MINOR_VERSION_IPW_C 2
#define I2C_AR_RELEASE_REVISION_VERSION_IPW_C 2
#define I2C_SW_MAJOR_VERSION_IPW_C 1
#define I2C_SW_MINOR_VERSION_IPW_C 0
#define I2C_SW_PATCH_VERSION_IPW_C 1

#define LPI2C_CHANNEL 1
#define FLEXIO_CHANNEL 2
#define E_OK 0
#define E_NOT_OK 1
#define FLEXIO_MAX_NUMBER_OF_BYTES_U32 255

typedef unsigned char uint8;
typedef int Std_ReturnType;
typedef int I2c_HwChannelType;
typedef int I2c_DataType;
typedef int I2c_StatusType;

I2c_StatusType I2cStatus = E_OK + E_NOT_OK;

struct I2c_Ipw_HwChannelConfigType {
    int I2c_Ipw_eChannelType;
    int I2c_Ipw_LPI2CHwConfig;
    int I2c_Ipw_FlexIOCHwConfig;
};

struct I2c_RequestType {
    int u8BufferSize;
};


FUNC(void, I2C_CODE) I2c_Ipw_InitChannel(
    CONST(uint8, AUTOMATIC) u8Channel,
    P2CONST(I2c_Ipw_HwChannelConfigType, AUTOMATIC, I2C_APPL_CONST) pConfigPtr)
{
    if (LPI2C_CHANNEL == (pConfigPtr->I2c_Ipw_eChannelType))
    {
        I2c_LPI2C_InitChannel(u8Channel, (pConfigPtr->I2c_Ipw_LPI2CHwConfig));
    }
    else
    {
        I2c_FlexIO_InitChannel(u8Channel, (pConfigPtr->I2c_Ipw_FlexIOCHwConfig));
    }
}

FUNC(Std_ReturnType, I2C_CODE) I2c_Ipw_CheckDataLength(
    P2CONST(I2c_RequestType, AUTOMATIC, I2C_APPL_CONST) pRequest,
    CONST(I2c_HwChannelType, AUTOMATIC) eChannelType)
{
    if (FLEXIO_CHANNEL == eChannelType)
    {
        if (FLEXIO_MAX_NUMBER_OF_BYTES_U32 >= pRequest->u8BufferSize)
        {
            return (Std_ReturnType)E_OK;
        }
    }
    else
    {
        return (Std_ReturnType)E_OK;
    }
    return (Std_ReturnType)E_NOT_OK;
}
