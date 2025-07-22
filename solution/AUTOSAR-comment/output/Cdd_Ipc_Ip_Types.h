/**
*   @file           Cdd_Ipc_Ip_Types.h
*   @brief          Cdd_Ipc_Ip_Types for BS9523XX MCAL DRIVER header file
*   @version        1.1.0
*   @addtogroup     Cdd_Ipc_Ip_Types
*   @{
*/
/*==============================================================================
*   Autosar Version      : 4.4.0
*   Autosar Revision     : ASR_REL_4_4_REV_110
*   Autosar Conf.Variant :
*   SW Version           : 1.1.0

*   Copyright (C) 2022 Byd
*   All Rights Reserved.
 =============================================================================*/

#ifndef CDD_IPC_IP_TYPES_H
#define CDD_IPC_IP_TYPES_H


#ifdef __cplusplus
extern "C"{
#endif

/*==============================================================================
*                                INCLUDE FILES
==============================================================================*/
#include "Cdd_Ipc_Ip_Cfg_Defines.h"
#include "Sfl_If.h"
#include "device_register.h"

/*==============================================================================
*                        SOURCE FILE VERSION INFORMATION
==============================================================================*/

/*==============================================================================
*                        SOURCE FILE VERSION INFORMATION
==============================================================================*/
#define CDD_IPC_IP_TYPES_VENDOR_ID                          255
#define CDD_IPC_IP_TYPES_AR_RELEASE_MAJOR_VERSION           4
#define CDD_IPC_IP_TYPES_AR_RELEASE_MINOR_VERSION           4
#define CDD_IPC_IP_TYPES_AR_RELEASE_REVISION_VERSION        0
#define CDD_IPC_IP_TYPES_SW_MAJOR_VERSION                   1
#define CDD_IPC_IP_TYPES_SW_MINOR_VERSION                   1
#define CDD_IPC_IP_TYPES_SW_PATCH_VERSION                   0

/*==============================================================================
*                              FILE VERSION CHECKS
==============================================================================*/
/* Check if current file and Cdd_Ipc_Ip_Cfg_Defines.h are of the same vendor */
#if (CDD_IPC_IP_TYPES_VENDOR_ID != CDD_IPC_IP_CFG_DEFINES_VENDOR_ID)
    #error "Cdd_Ipc_Ip_Types.h and Cdd_Ipc_Ip_Cfg_Defines.h have different vendor ids"
#endif
/* Check if current file and Cdd_Ipc_Ip_Cfg_Defines.h are of the same Autosar version */
#if ((CDD_IPC_IP_TYPES_AR_RELEASE_MAJOR_VERSION    != CDD_IPC_IP_CFG_DEFINES_AR_RELEASE_MAJOR_VERSION) || \
     (CDD_IPC_IP_TYPES_AR_RELEASE_MINOR_VERSION    != CDD_IPC_IP_CFG_DEFINES_AR_RELEASE_MINOR_VERSION) || \
     (CDD_IPC_IP_TYPES_AR_RELEASE_REVISION_VERSION != CDD_IPC_IP_CFG_DEFINES_AR_RELEASE_REVISION_VERSION))
    #error "AutoSar version of Cdd_Ipc_Ip_Types.h and Cdd_Ipc_Ip_Cfg_Defines.h are different"
#endif
/* Check if current file and Cdd_Ipc_Ip_Cfg_Defines.h are of the same software version */
#if ((CDD_IPC_IP_TYPES_SW_MAJOR_VERSION    != CDD_IPC_IP_CFG_DEFINES_SW_MAJOR_VERSION) || \
     (CDD_IPC_IP_TYPES_SW_MINOR_VERSION    != CDD_IPC_IP_CFG_DEFINES_SW_MINOR_VERSION) || \
     (CDD_IPC_IP_TYPES_SW_REVISION_VERSION != CDD_IPC_IP_CFG_DEFINES_SW_REVISION_VERSION))
    #error "Software version of Cdd_Ipc_Ip_Types.h and Cdd_Ipc_Ip_Cfg_Defines.h are different"
#endif

#ifndef DISABLE_MCAL_INTERMODULE_ASR_CHECK
    /* Check if current file and Sfl_If.h are of the same Autosar version */
    #if ((CDD_IPC_IP_TYPES_AR_RELEASE_MAJOR_VERSION != SFL_IF_AR_RELEASE_MAJOR_VERSION) || \
         (CDD_IPC_IP_TYPES_AR_RELEASE_MINOR_VERSION != SFL_IF_AR_RELEASE_MINOR_VERSION))
        #error "AutoSar Version Numbers of Cdd_Ipc_Ip_Types.h and Sfl_If.h are different"
    #endif
#endif

/*==============================================================================
*                             DEFINES AND MACROS
==============================================================================*/



/*==============================================================================
*                                    ENUMS
==============================================================================*/



/*==============================================================================
*                           STRUCTURES AND OTHER TYPES
==============================================================================*/



/*==============================================================================
*                         GLOBAL VARIABLES DECLARATION
==============================================================================*/


/*==============================================================================
*                             FUNCTION PROTOTYPES
==============================================================================*/



#ifdef __cplusplus
}
#endif

/** @} */

#endif /* CDD_IPC_IP_TYPES_H */

/* -------------------------------  EOF  ------------------------------------ */
