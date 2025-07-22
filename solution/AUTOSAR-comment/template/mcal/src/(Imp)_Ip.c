/**
*   @file           {{ Imp | expr_filter(__context__) }}_Ip.c
*   @brief          {{ Imp | expr_filter(__context__) }}_Ip for {{ PROJECT | expr_filter(__context__) }} MCAL DRIVER C source file
*   @version        {{ x | expr_filter(__context__) }}.{{ y | expr_filter(__context__) }}.{{ z | expr_filter(__context__) }}
*   @addtogroup     {{ Imp | expr_filter(__context__) }}_Ip
*   @{
*/
/*==============================================================================
*   Autosar Version      : {{ AR_RELEASE_MAJOR_VERSION_C | expr_filter(__context__) }}.{{ AR_RELEASE_MINOR_VERSION_C | expr_filter(__context__) }}.{{ AR_RELEASE_REVISION_VERSION_C | expr_filter(__context__) }}
*   Autosar Revision     : ASR_REL_{{ AR_RELEASE_MAJOR_VERSION_C | expr_filter(__context__) }}_{{ AR_RELEASE_MINOR_VERSION_C | expr_filter(__context__) }}_REV_{{ x | expr_filter(__context__) }}{{ y | expr_filter(__context__) }}{{ z | expr_filter(__context__) }}
*   Autosar Conf.Variant :
*   SW Version           : {{ x | expr_filter(__context__) }}.{{ y | expr_filter(__context__) }}.{{ z | expr_filter(__context__) }}

*   Copyright (C) 2022 Byd
*   All Rights Reserved.
==============================================================================*/

#ifdef __cplusplus
extern "C"{
#endif

/*==============================================================================
*                                INCLUDE FILES
==============================================================================*/
#include "{{ Imp | expr_filter(__context__) }}_Ip.h"

/*==============================================================================
*                        SOURCE FILE VERSION INFORMATION
==============================================================================*/
#define {{ Imp | expr_filter(__context__) }}_IP_VENDOR_ID_C                        {{ vi | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_MAJOR_VERSION_C         {{ AR_RELEASE_MAJOR_VERSION_C | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_MINOR_VERSION_C         {{ AR_RELEASE_MINOR_VERSION_C | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_REVISION_VERSION_C      {{ AR_RELEASE_REVISION_VERSION_C | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_SW_MAJOR_VERSION_C                 {{ x | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_SW_MINOR_VERSION_C                 {{ y | expr_filter(__context__) }}
#define {{ Imp | expr_filter(__context__) }}_IP_SW_PATCH_VERSION_C                 {{ z | expr_filter(__context__) }}

/*==============================================================================
*                              FILE VERSION CHECKS
==============================================================================*/
/* Check if current file and {{ Imp | expr_filter(__context__) }}_Ip.h are of the same vendor */
#if ({{ Imp | expr_filter(__context__) }}_IP_VENDOR_ID_C != {{ Imp | expr_filter(__context__) }}_IP_VENDOR_ID)
    #error "{{ Imp | expr_filter(__context__) }}_Ip.c and {{ Imp | expr_filter(__context__) }}_Ip.h have different vendor ids"
#endif
/* Check if current file and {{ Imp | expr_filter(__context__) }}_Ip.h are of the same Autosar version */
#if (({{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_MAJOR_VERSION_C    != {{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_MAJOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_MINOR_VERSION_C    != {{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_MINOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_REVISION_VERSION_C != {{ Imp | expr_filter(__context__) }}_IP_AR_RELEASE_REVISION_VERSION))
    #error "AutoSar version of {{ Imp | expr_filter(__context__) }}_Ip.c and {{ Imp | expr_filter(__context__) }}_Ip.h are different"
#endif
/* Check if current file and {{ Imp | expr_filter(__context__) }}_Ip.h are of the same software version */
#if (({{ Imp | expr_filter(__context__) }}_IP_SW_MAJOR_VERSION_C    != {{ Imp | expr_filter(__context__) }}_IP_SW_MAJOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_SW_MINOR_VERSION_C    != {{ Imp | expr_filter(__context__) }}_IP_SW_MINOR_VERSION) || \
     ({{ Imp | expr_filter(__context__) }}_IP_SW_REVISION_VERSION_C != {{ Imp | expr_filter(__context__) }}_IP_SW_REVISION_VERSION))
    #error "Software version of {{ Imp | expr_filter(__context__) }}_Ip.c and {{ Imp | expr_filter(__context__) }}_Ip.h are different"
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



/** @} */

/* -------------------------------  EOF  ------------------------------------ */
