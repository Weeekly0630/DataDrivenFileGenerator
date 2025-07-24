

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
#define CDD_IPC_IP_VENDER_ID_C 255
#define CDD_IPC_IP_AR_RELEASE_MAJOR_VERSION_C 4
#define CDD_IPC_IP_AR_RELEASE_MINOR_VERSION_C 4
#define CDD_IPC_IP_AR_RELEASE_REVISION_VERSION_C 0
#define CDD_IPC_IP_SW_MAJOR_VERSION_C 1
#define CDD_IPC_IP_SW_MINOR_VERSION_C 1
#define CDD_IPC_IP_SW_PATCH_VERSION_C 0


/*==============================================================================
*                              FILE VERSION CHECKS
==============================================================================*/
/* Check vendor */
#if (IPC_VENDOR_ID_C != IPC_VENDOR_ID)
    #error "Ipc.c and Ipc.h have different vendor ids"
#endif
/* Check AUTOSAR version */
#if (IPC_AR_RELEASE_MAJOR_VERSION_C != IPC_AR_RELEASE_MAJOR_VERSION) || \
    (IPC_AR_RELEASE_MINOR_VERSION_C != IPC_AR_RELEASE_MINOR_VERSION) || \
    (IPC_AR_RELEASE_REVISION_VERSION_C != IPC_AR_RELEASE_REVISION_VERSION)
    #error "AutoSar Version Numbers of Ipc.c and Ipc.h are different"
#endif
/* Check software version */
#if (IPC_SW_MAJOR_VERSION_C != IPC_SW_MAJOR_VERSION) || \
    (IPC_SW_MINOR_VERSION_C != IPC_SW_MINOR_VERSION) || \
    (IPC_SW_PATCH_VERSION_C != IPC_SW_PATCH_VERSION)
    #error "Software Version Numbers of Ipc.c and Ipc.h are different"
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