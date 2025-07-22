/**
*   @file           {{ Imp | expr_filter(__context__) }}_Ip_Types.h
*   @brief          {{ Imp | expr_filter(__context__) }}_Ip_Types for {{ PROJECT | expr_filter(__context__) }} MCAL DRIVER header file
*   @version        {{ x | expr_filter(__context__) }}.{{ y | expr_filter(__context__) }}.{{ z | expr_filter(__context__) }}
*   @addtogroup     {{ Imp | expr_filter(__context__) }}_Ip_Types
*   @{
*/
/*==============================================================================
*   Autosar Version      : {{ AR_RELEASE_MAJOR_VERSION | expr_filter(__context__) }}.{{ AR_RELEASE_MINOR_VERSION | expr_filter(__context__) }}.{{ AR_RELEASE_REVISION_VERSION | expr_filter(__context__) }}
*   Autosar Revision     : ASR_REL_{{ AR_RELEASE_MAJOR_VERSION | expr_filter(__context__) }}_{{ AR_RELEASE_MINOR_VERSION | expr_filter(__context__) }}_REV_{{ x | expr_filter(__context__) }}{{ y | expr_filter(__context__) }}{{ z | expr_filter(__context__) }}
*   Autosar Conf.Variant :
*   SW Version           : {{ x | expr_filter(__context__) }}.{{ y | expr_filter(__context__) }}.{{ z | expr_filter(__context__) }}

*   Copyright (C) 2022 Byd
*   All Rights Reserved.
 =============================================================================*/

#ifndef {{ Imp | expr_filter(__context__) }}_IP_TYPES_H
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_H


#ifdef __cplusplus
extern "C"{
#endif

/*==============================================================================
*                                INCLUDE FILES
==============================================================================*/
#include "{{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h"
#include "Sfl_If.h"
#include "device_register.h"

/*==============================================================================
*                        SOURCE FILE VERSION INFORMATION
==============================================================================*/

/*==============================================================================
*                        SOURCE FILE VERSION INFORMATION
==============================================================================*/
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_VENDOR_ID                          255
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_MAJOR_VERSION           {{ AR_RELEASE_MAJOR_VERSION | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_MINOR_VERSION           {{ AR_RELEASE_MINOR_VERSION | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_REVISION_VERSION        {{ AR_RELEASE_REVISION_VERSION | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_SW_MAJOR_VERSION                   {{ x | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_SW_MINOR_VERSION                   {{ y | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_TYPES_SW_PATCH_VERSION                   {{ z | expr_filter(__context__) }}

/*==============================================================================
*                              FILE VERSION CHECKS
==============================================================================*/
/* Check if current file and {{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h are of the same vendor */
#if ({{ Imp | expr_filter(__context__) }}_IP_TYPES_VENDOR_ID != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_VENDOR_ID)
    #error "{{ Imp | expr_filter(__context__) }}_Ip_Types.h and {{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h have different vendor ids"
#endif
/* Check if current file and {{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h are of the same Autosar version */
#if (({{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_MAJOR_VERSION    != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_AR_RELEASE_MAJOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_MINOR_VERSION    != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_AR_RELEASE_MINOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_REVISION_VERSION != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_AR_RELEASE_REVISION_VERSION))
    #error "AutoSar version of {{ Imp | expr_filter(__context__) }}_Ip_Types.h and {{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h are different"
#endif
/* Check if current file and {{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h are of the same software version */
#if (({{ Imp | expr_filter(__context__) }}_IP_TYPES_SW_MAJOR_VERSION    != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_SW_MAJOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_TYPES_SW_MINOR_VERSION    != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_SW_MINOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_TYPES_SW_REVISION_VERSION != {{ Imp | expr_filter(__context__) }}_IP_CFG_DEFINES_SW_REVISION_VERSION))
    #error "Software version of {{ Imp | expr_filter(__context__) }}_Ip_Types.h and {{ Imp | expr_filter(__context__) }}_Ip_Cfg_Defines.h are different"
#endif

#ifndef DISABLE_MCAL_INTERMODULE_ASR_CHECK
    /* Check if current file and Sfl_If.h are of the same Autosar version */
    #if (({{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_MAJOR_VERSION != SFL_IF_AR_RELEASE_MAJOR_VERSION) || \
         ({{ Imp | expr_filter(__context__) }}_IP_TYPES_AR_RELEASE_MINOR_VERSION != SFL_IF_AR_RELEASE_MINOR_VERSION))
        #error "AutoSar Version Numbers of {{ Imp | expr_filter(__context__) }}_Ip_Types.h and Sfl_If.h are different"
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

#endif /* {{ Imp | expr_filter(__context__) }}_IP_TYPES_H */

/* -------------------------------  EOF  ------------------------------------ */
