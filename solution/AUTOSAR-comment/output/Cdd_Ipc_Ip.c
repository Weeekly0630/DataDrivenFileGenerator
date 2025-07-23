
/**
*   @file       Ipc
*   @brief      CDD Ipc Ip layer C source file
*   @version    1.1.0
*   @addtogroup CDD_IPC_MODULE
*   @{
*/
/*==============================================================================
*   Autosar Version      : 4.4.0
*   Autosar Revision     : 
*   Autosar Conf.Variant :
*   SW Version           : 1.1.0

*   Copyright (C) 2022 Byd
*   All Rights Reserved.
 =============================================================================*/

#ifdef __cplusplus
extern "C"{
#endif

/*==============================================================================
*                                INCLUDE FILES
==============================================================================*/
#if VERSION == "1.1.1"
    #include "Cdd_Ipc.h"
#endif
/*==============================================================================
*                        SOURCE FILE VERSION INFORMATION
==============================================================================*/
#define IPC_VENDOR_ID_C                          255
#define IPC_AR_RELEASE_MAJOR_VERSION_C           4
#define IPC_AR_RELEASE_MINOR_VERSION_C           4
#define IPC_AR_RELEASE_REVISION_VERSION_C        0
#define IPC_SW_MAJOR_VERSION_C                   1
#define IPC_SW_MINOR_VERSION_C                   1
#define IPC_SW_PATCH_VERSION_C                   0

/*==============================================================================
*                              FILE VERSION CHECKS
==============================================================================*/
/* Check if current file and Ipc_Ip.h are of the same vendor */
#if (IPC_IP_VENDOR_ID_C != IPC_IP_VENDOR_ID)
    #error "Ipc_Ip.c and Ipc_Ip.h have different vendor ids"
#endif
/* Check if current file and Ipc_Ip.h are of the same Autosar version */
#if ((IPC_IP_AR_RELEASE_MAJOR_VERSION_C    != IPC_IP_AR_RELEASE_MAJOR_VERSION) || \
     (IPC_IP_AR_RELEASE_MINOR_VERSION_C    != IPC_IP_AR_RELEASE_MINOR_VERSION) || \
     (IPC_IP_AR_RELEASE_REVISION_VERSION_C != IPC_IP_AR_RELEASE_REVISION_VERSION))
    #error "AutoSar version of Ipc_Ip.c and Ipc_Ip.h are different"
#endif
/* Check if current file and Ipc_Ip.h are of the same software version */
#if ((IPC_IP_SW_MAJOR_VERSION_C    != IPC_IP_SW_MAJOR_VERSION) || \
     (IPC_IP_SW_MINOR_VERSION_C    != IPC_IP_SW_MINOR_VERSION) || \
     (IPC_IP_SW_REVISION_VERSION_C != IPC_IP_SW_REVISION_VERSION))
    #error "Software version of Ipc_Ip.c and Ipc_Ip.h are different"
#endif

/*==============================================================================
*                              LOCAL TYPEDEFS
==============================================================================*/



/*==============================================================================
*                               LOCAL MACROS
==============================================================================*/



/*==============================================================================
*                              LOCAL CONSTANTS
==============================================================================*/



/*==============================================================================
*                              LOCAL VARIABLES
==============================================================================*/



/*==============================================================================
*                              GLOBAL CONSTANTS
==============================================================================*/



/*==============================================================================
*                              GLOBAL VARIABLES
==============================================================================*/



/*==============================================================================
*                          LOCAL FUNCTION PROTOTYPES
==============================================================================*/



/*==============================================================================
*                               LOCAL FUNCTION
==============================================================================*/



/*==============================================================================
*                               GLOBAL FUNCTION
==============================================================================*/


#ifdef __cplusplus
}
#endif

/*  @}*/

/* -------------------------------  EOF  ------------------------------------ */